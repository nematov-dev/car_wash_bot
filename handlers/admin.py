import os, asyncio
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from loader import DBSession
from database.models import Car, Washer, Order, OrderStatus
from database.models import Service


from states.states import ManualOrderStates, AudioOrderStates
from keyboards.admin_kb import (
    get_admin_main_menu,
    admin_cancel_kb,
    get_washers_reply_keyboard,
    get_services_reply_keyboard,
    get_skip_keyboard,
    get_audio_confirm_keyboard,
    get_report_keyboard
)
from states.states import ManualOrderStates, ReportStates
from services.speech_to_text import transcribe_audio_to_order
from middlewares.admin_check import AdminCheckMiddleware
from services.report_service import generate_monthly_report,generate_range_report


admin_router = Router()

admin_router.message.middleware(AdminCheckMiddleware())
admin_router.callback_query.middleware(AdminCheckMiddleware())

# Cancel handlers

@admin_router.message(
    (F.text == "🏠 Bosh sahifa") | (F.text == "✖️ Bekor qilish")
)
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Asosiy menyuga qaytdingiz:",
        reply_markup=get_admin_main_menu()
    )

# Callback query cancel handler

@admin_router.callback_query(F.data == "cancel_admin")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Amal bekor qilindi.",reply_markup=get_admin_main_menu())
    await callback.answer()

# Admin panel main menu handler

@admin_router.message(F.text == "⬅️ Admin panel")
async def admin_panel_main(message: Message):
    await message.answer("Asosiy admin panel menyusi:", reply_markup=get_admin_main_menu())

# Manual order process handlers

@admin_router.message(F.text == "📥 Buyurtma qabul qilish (qo'lda)")
async def manual_order_start(message: Message, state: FSMContext):

    await message.answer("🚗 Mashina davlat raqamini kiriting (01A123AA):", reply_markup=admin_cancel_kb())
    await state.set_state(ManualOrderStates.waiting_for_plate)

# Plate number handler

@admin_router.message(ManualOrderStates.waiting_for_plate)
async def process_plate(message: Message, state: FSMContext):

    if message.text in ["🏠 Bosh sahifa", "✖️ Bekor qilish"]:
        await cancel_handler(message, state)
        return
    
    plate = message.text.strip().upper()
    await state.update_data(plate_number=plate)
    
    with DBSession() as db:
        washers = db.query(Washer).filter(Washer.active == True).all()
        markup = get_washers_reply_keyboard(washers)
        await message.answer(f"🚘 Mashina: {plate}\n\nXizmat ko'rsatuvchi? (Tugmadan tanlang yoki ismini yozing):", reply_markup=markup)
        await state.set_state(ManualOrderStates.selecting_washer)

# Washer selection handler

@admin_router.message(ManualOrderStates.selecting_washer) 
async def process_washer(message: Message, state: FSMContext):
    if message.text in ["🏠 Bosh sahifa", "✖️ Bekor qilish"]:
        await cancel_handler(message, state)
        return

    washer_name = message.text
    await state.update_data(temp_washer=washer_name)
    
    with DBSession() as db:
        services = db.query(Service).filter(Service.active == True).all()
        
        markup = get_services_reply_keyboard(services)
        await message.answer(
            "🛠 Xizmat turini tanlang yoki o'zingiz yozing:", 
            reply_markup=markup
        )
    await state.set_state(ManualOrderStates.waiting_for_service)

# Service selection handler

@admin_router.message(ManualOrderStates.waiting_for_service)
async def process_service(message: Message, state: FSMContext):
    if message.text in ["🏠 Bosh sahifa", "✖️ Bekor qilish"]:
        return await cancel_handler(message, state)
    
    service = message.text if message.text != "➡️ O'tkazib yuborish" else None
    await state.update_data(services_name=service)
    
    await message.answer("💰 Narxini kiriting:", reply_markup=get_skip_keyboard())
    await state.set_state(ManualOrderStates.waiting_for_price)

# Price input handler

@admin_router.message(ManualOrderStates.waiting_for_price)
async def finalize_order(message: Message, state: FSMContext):
    if message.text in ["🏠 Bosh sahifa", "✖️ Bekor qilish"]:
        return await cancel_handler(message, state)
    
    price_text = message.text
    price = 0.0
    if price_text != "➡️ O'tkazib yuborish":
        try:
            price = float(price_text.replace(" ", ""))
        except:
            await message.answer("⚠️ Narxni raqamda kiriting!")
            return

    data = await state.get_data()
    
    with DBSession() as db:
        car = db.query(Car).filter(Car.plate_number == data['plate_number']).first()
        if not car:
            car = Car(plate_number=data['plate_number'])
            db.add(car)
            db.flush()

        washer = db.query(Washer).filter(Washer.full_name.ilike(f"%{data['temp_washer']}%")).first()
        
        new_order = Order(
            car_id=car.id,
            washer_id=washer.id if washer else None,
            services_name=data.get('services_name'),
            price=price,
            status=OrderStatus.washing
        )
        db.add(new_order)
        db.commit()

    await message.answer(
        f"✅ Buyurtma saqlandi!\n\n"
        f"🚗 Raqam: {data['plate_number']}\n"
        f"🧼 Moykachi: {data['temp_washer']}\n"
        f"🛠️ Xizmat: {data.get('services_name') or 'Noma’lum'}\n"
        f"💰 Narx: {price} so'm", 
        reply_markup=get_admin_main_menu()
    )
    await state.clear()


# Audio order handlers


@admin_router.message(F.voice | F.audio)
async def handle_audio_order(message: Message, state: FSMContext):
    processing_msg = await message.answer("🎙 Audio tahlil qilinmoqda...")
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"temp_{file_id}.ogg"
    
    try:
        await message.bot.download_file(file.file_path, file_path)
        order_data = transcribe_audio_to_order(file_path)
        
        plate = order_data.get('plate_number')
        price = order_data.get('price', 0)
        washer_name = order_data.get('washer_name')
        services_name = order_data.get('services_name')

        if not plate:
            await processing_msg.edit_text("❌ Raqamni aniqlab bo'lmadi. Iltimos, qaytadan aniqroq gapiring.")
            return

        await state.update_data(
            temp_plate=str(plate).upper(),
            temp_price=price,
            temp_washer=washer_name,
            services_name=services_name
        )

        await processing_msg.edit_text(
            f"📋 **Ma'lumotlar to'g'rimi?**\n\n"
            f"🚘 Mashina: `{plate}`\n"
            f"🧼 Ishchi: `{washer_name}`\n"
            f"🛎 Xizmat turi: `{services_name}`\n"
            f"💰 Narxi: `{price}` so'm\n\n"
            f"Tasdiqlaysizmi?",
            reply_markup=get_audio_confirm_keyboard(),
            parse_mode="Markdown"
        )
        await state.set_state(AudioOrderStates.confirming)

    except Exception as e:
        await processing_msg.edit_text(f"Xatolik bor qayta yuboring.")
    finally:
        if os.path.exists(file_path):
            await asyncio.sleep(1)
            try: os.remove(file_path)
            except: pass

# Audio order confirmation handlers

@admin_router.callback_query(AudioOrderStates.confirming, F.data == "confirm_audio_order")
async def commit_audio_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    with DBSession() as db:
        car = db.query(Car).filter(Car.plate_number == data['temp_plate']).first()
        if not car:
            car = Car(plate_number=data['temp_plate'])
            db.add(car)
            db.flush()

        owner = car.owners[0] if car.owners else None

        washer = db.query(Washer).filter(Washer.full_name.ilike(f"%{data['temp_washer']}%")).first()
        if not washer:
            await callback.message.edit_text(f"❌ '{data['temp_washer']}' topilmadi.")
            await state.clear()
            return

        new_order = Order(
            car_id=car.id,
            user_id=owner.id if owner else None, 

            washer_id=washer.id,
            price=float(data['temp_price']) if data['temp_price'] else 0.0,
            status=OrderStatus.washing,
            services_name=data['services_name'] if data.get('services_name') else None
        )
        db.add(new_order)
        db.commit()

    res_msg = "✅ Buyurtma saqlandi!"
    
    await callback.message.edit_text(res_msg)
    await callback.message.answer("Asosiy menyu:", reply_markup=get_admin_main_menu())
    await state.clear()

# Retry audio order handler

@admin_router.callback_query(AudioOrderStates.confirming, F.data == "retry_audio_order")
async def retry_audio_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🔄 Qayta yuborish tanlandi. Iltimos, yangi audio yuboring:")
    await callback.answer()


# Admin stat

@admin_router.message(F.text == "📊 Hisobot")
async def admin_panel_stat(message: Message):
    await message.answer("Hisobot:", reply_markup=get_report_keyboard())

# 1 day

@admin_router.message(lambda m: m.text == "📊 1 kunlik")
async def daily_report(message: Message):
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0)
    end = today

    file_name = generate_range_report(start, end)

    try:
        await message.answer_document(FSInputFile(file_name))
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# 1 week

@admin_router.message(lambda m: m.text == "📊 1 haftalik")
async def weekly_report(message: Message):
    end = datetime.now()
    start = end - timedelta(days=7)

    file_name = generate_range_report(start, end)

    try:
        await message.answer_document(FSInputFile(file_name))
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# 1 month

@admin_router.message(lambda m: m.text == "📊 1 oylik")
async def monthly_report(message: Message):
    now = datetime.now()

    file_name = generate_monthly_report(now.year, now.month)

    try:
        await message.answer_document(FSInputFile(file_name))
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


# Custom day

@admin_router.message(lambda m: m.text == "📅 Sana bo‘yicha")
async def custom_report_start(message: Message, state: FSMContext):
    await message.answer("Boshlanish sanani kiriting:\nFormat: 2026-03-01 (yil-oy-kun)", reply_markup=admin_cancel_kb())
    await state.set_state(ReportStates.waiting_for_start)


@admin_router.message(ReportStates.waiting_for_start)
async def get_start_date(message: Message, state: FSMContext):
    try:
        start_date = datetime.strptime(message.text.strip(), "%Y-%m-%d")
        await state.update_data(start_date=start_date)

        await message.answer(
            "Tugash sanani kiriting:\nFormat: 2026-03-10 (yil-oy-kun)", 
            reply_markup=admin_cancel_kb()
        )
        await state.set_state(ReportStates.waiting_for_end)

    except ValueError:
        await message.answer(
            "❌ Format noto‘g‘ri. Masalan: 2026-03-01",
            reply_markup=admin_cancel_kb()
        )


@admin_router.message(ReportStates.waiting_for_end)
async def get_end_date(message: Message, state: FSMContext):
    try:
        end_date = datetime.strptime(message.text.strip(), "%Y-%m-%d")

        data = await state.get_data()
        start_date = data.get("start_date")

        if not start_date:
            await message.answer(
                "❌ Avval boshlanish sanani kiriting.",
                reply_markup=admin_cancel_kb()
            )
            return

        end_date = end_date.replace(hour=23, minute=59, second=59)

        file_name = generate_range_report(start_date, end_date)

        try:
            await message.answer_document(FSInputFile(file_name))
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

        await state.clear()

    except ValueError:
        await message.answer(
            "❌ Format noto‘g‘ri. Masalan: 2026-03-10",
            reply_markup=admin_cancel_kb()
        )