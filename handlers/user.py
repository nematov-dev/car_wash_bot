from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import desc,func


from database.session import SessionLocal
from database.models import User, Service,Car,Order, OrderStatus
from keyboards.user_kb import get_main_user_menu, get_cancel_keyboard,get_user_cars_keyboard,get_account_settings_keyboard,get_cars_delete_list_keyboard,get_confirm_delete_kb,get_history_pagination_keyboard
from states.states import AddCarStates


user_router = Router()


# Cancel handler (global)

@user_router.message(lambda message: message.text == "❌ Bekor qilish")
async def global_cancel(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "Asosiy menyu",
        reply_markup=get_main_user_menu()
    )


# Service handler

@user_router.message(lambda message: message.text == "🛠️ Xizmatlar")
async def show_services(message: Message):
    db = SessionLocal()
    try:
        services = db.query(Service).filter(Service.active == True).all()
        if not services:
            await message.answer("Hozircha xizmatlar mavjud emas.")
            return

        text = "📋 Bizning xizmatlarimiz:\n\n"
        for s in services:
            text += f"• {s.name} — Narxi: {s.price:,} so'm\n"

        await message.answer(text)
    finally:
        db.close()


# My account handler

@user_router.message(lambda message: message.text == "👤 Hisobim")
async def my_account(message: Message):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if not user:
            await message.answer("Siz ro'yxatdan o‘tmagansiz.")
            return

        text = f"👤 **Ismingiz:** {user.full_name}\n\n🚗 **Mashinalaringiz:**\n"
        if user.cars:
            for car in user.cars:
                text += f"• {car.plate_number}\n"
            reply_markup = get_account_settings_keyboard()
        else:
            text += "Siz hali mashina qo‘shmagansiz."
            reply_markup = None

        await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")
    finally:
        db.close()

# My car delete process (car list)

@user_router.callback_query(lambda c: c.data == "start_delete_process")
async def process_delete_list(callback: CallbackQuery):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
        if not user.cars:
            await callback.answer("O'chirishga mashina yo'q")
            return

        await callback.message.edit_text(
            "🗑️ Qaysi mashinani o'chirib tashlamoqchisiz?",
            reply_markup=get_cars_delete_list_keyboard(user.cars)
        )
    finally:
        db.close()
    await callback.answer()

# My car delete confirmation

@user_router.callback_query(lambda c: c.data.startswith("del_select_"))
async def process_delete_confirm_ask(callback: CallbackQuery):
    car_id = int(callback.data.split("_")[2])
    db = SessionLocal()
    try:
        car = db.query(Car).filter(Car.id == car_id).first()
        await callback.message.edit_text(
            f"⚠️ **{car.plate_number}** ni o'chirishni tasdiqlaysizmi?",
            reply_markup=get_confirm_delete_kb(car_id),
            parse_mode="Markdown"
        )
    finally:
        db.close()
    await callback.answer()

# My car delete

@user_router.callback_query(lambda c: c.data.startswith("del_confirm_"))
async def process_delete_final(callback: CallbackQuery):
    car_id = int(callback.data.split("_")[2])
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
        car = db.query(Car).filter(Car.id == car_id).first()

        if car and user in car.owners:
            car.owners.remove(user) # remove user
            db.commit()
            await callback.message.edit_text(f"{car.plate_number} muvaffaqiyatli o'chirildi.")
        else:
            await callback.answer("Xatolik: Mashina topilmadi.", show_alert=True)
    finally:
        db.close()
    await callback.answer()

# Back to account callback

@user_router.callback_query(lambda c: c.data == "back_to_account")
async def back_to_account_callback(callback: CallbackQuery):
    await callback.message.delete()
    await my_account(callback.message)
    await callback.answer()

# Add car handler

@user_router.message(lambda message: message.text == "➕ Moshina qo'shish")
async def add_car_start(message: Message, state: FSMContext):
    await message.answer(
        "➕ Mashinangizni davlat raqamini kiriting: (misol: A123AA)",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AddCarStates.waiting_for_plate)

@user_router.message(AddCarStates.waiting_for_plate)
async def add_car_save(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Asosiy menyu", reply_markup=get_main_user_menu())
        return

    plate_number = message.text.strip().upper()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        car = db.query(Car).filter(Car.plate_number == plate_number).first()
        
        if not car:
            car = Car(plate_number=plate_number)
            db.add(car)
            db.flush()

        if user in car.owners:
            await message.answer(f"Siz bu mashinani allaqachon qo‘shgansiz.")
        else:
            car.owners.append(user)

            db.query(Order).filter(
                Order.car_id == car.id, 
                Order.user_id == None
            ).update({Order.user_id: user.id})
            
            db.commit()
            await message.answer(
                f"✅ Mashina {plate_number} qo‘shildi!\n"
                f"Eski buyurtmalaringiz ham hisobingizga biriktirildi.",
                reply_markup=get_main_user_menu()
            )
    finally:
        db.close()
        await state.clear()


# Check orders

@user_router.message(lambda message: message.text == "🔍 Buyurtmani tekshirish")
async def check_status_handler(message: Message):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

        if not user or not user.cars:
            await message.answer("🚗 Sizda hali mashinalar mavjud emas. Avval mashina qo'shing.")
            return

        await message.answer(
            "🚗 Kerakli mashinangizni tanlang.",
            reply_markup=get_user_cars_keyboard(user.cars)
        )

    finally:
        db.close()

# Select car status callback

@user_router.callback_query(F.data.startswith('car_status_') | F.data.startswith('car_hist_'))
async def process_car_status_callback(callback: CallbackQuery):
    data = callback.data.split("_")
    car_id = int(data[2])
    page = int(data[3]) if len(data) > 3 else 1
    page_size = 10
    
    db = SessionLocal()
    try:
        car = db.query(Car).filter(Car.id == car_id).first()
        if not car:
            await callback.answer("Mashina topilmadi.")
            return

        latest_order = db.query(Order).filter(Order.car_id == car.id).order_by(desc(Order.created_at)).first()

        if not latest_order:
            await callback.message.edit_text(f"🤷🏻‍♂️ {car.plate_number} uchun buyurtmalar topilmadi.")
            return

        if latest_order.status == OrderStatus.washing:
            status_text = "⏳ Yuvilmoqda"
        elif latest_order.status == OrderStatus.done:
            status_text = "✅ Tayyor"
        elif latest_order.status == OrderStatus.cancelled:
            status_text = "❌ Bekor qilingan"
        else:
            status_text = str(latest_order.status.value)

        total_orders = db.query(func.count(Order.id)).filter(Order.car_id == car.id).scalar()
        total_pages = (total_orders + page_size - 1) // page_size
        
        history_orders = (
            db.query(Order)
            .filter(Order.car_id == car.id)
            .order_by(desc(Order.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        price_val = f"{latest_order.price} so’m" if latest_order.price else "Noma’lum"
        service_val = latest_order.services_name if latest_order.services_name else "Noma’lum"

        text = (
            f"🚘 **Mashina:** {car.plate_number}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🟢 **So'nggi buyurtma holati:**\n\n"
            f"📌 **Status:** {status_text}\n"
            f"👤 **Moykachi:** {latest_order.washer.full_name if latest_order.washer else 'Noma’lum'}\n"
            f"🧾 **Xizmat:** {service_val}\n"
            f"💰 **Narx:** {price_val}\n"
            f"📅 **Vaqt:** {latest_order.created_at.strftime('%H:%M')} | {latest_order.created_at.strftime('%d.%m.%Y')}\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📜 **Yuvishlar tarixi:**\n\n"
        )

        for i, o in enumerate(history_orders):
            washer_name = o.washer.full_name if o.washer else "Noma'lum"
            h_service = o.services_name if o.services_name else ""
            h_price = f"{o.price} so'm" if o.price else ""
            text += f"🔹 {o.created_at.strftime('%d.%m.%Y')} — {h_service} {h_price} ({washer_name})\n"

        kb = get_history_pagination_keyboard(car_id, page, total_pages) if total_pages > 1 else None
        
        try:
            await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
        except Exception as e:
            await callback.message.edit_text(text.replace("**", "").replace("__", ""), reply_markup=kb)
            
        await callback.answer()

    finally:
        db.close()

# Help handler

@user_router.message(lambda message: message.text == "📒 Qo'llanma")
async def help(message: Message):
        text = "📒 Qo‘llanma:\n\n"
        await message.answer(text)