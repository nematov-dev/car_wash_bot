from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import desc


from database.session import SessionLocal
from database.models import User, Service,Car,Order
from keyboards.user_kb import get_main_user_menu, get_cancel_keyboard,get_user_cars_keyboard,get_account_settings_keyboard,get_cars_delete_list_keyboard,get_confirm_delete_kb
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
        await message.answer(
            "Asosiy menyu",
            reply_markup=get_main_user_menu()
        )
        return

    plate_number = message.text.strip().upper()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if not user:
            await message.answer("Siz ro‘yxatdan o‘tmagansiz.")
            await state.clear()
            return

        car = db.query(Car).filter(Car.plate_number == plate_number).first()
        if car:
            if user in car.owners:
                await message.answer(f"Siz bu mashinani allaqachon qo‘shgansiz: {plate_number}")
            else:
                car.owners.append(user)
                db.commit()
                await message.answer(f"✅ Mashina {plate_number} sizning hisobingizga qo‘shildi!",
                                     reply_markup=get_main_user_menu())
        else:
            new_car = Car(plate_number=plate_number)
            new_car.owners.append(user)
            db.add(new_car)
            db.commit()
            await message.answer(f"✅ Mashina {plate_number} muvaffaqiyatli qo‘shildi!",
                                 reply_markup=get_main_user_menu())

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

@user_router.callback_query(lambda c: c.data.startswith('car_status_'))
async def process_car_status_callback(callback: CallbackQuery):
    car_id = int(callback.data.split("_")[2])
    db = SessionLocal()
    
    try:
        car = db.query(Car).filter(Car.id == car_id).first()
        if not car:
            await callback.answer("Mashina topilmadi.")
            return

        order = (
            db.query(Order)
            .filter(Order.car_id == car.id)
            .order_by(desc(Order.created_at))
            .first()
        )

        if not order:
            text = f"🤷🏻‍♂️ {car.plate_number} mashina uchun buyurtma topilmadi."
        else:
            status_val = order.status.value if hasattr(order.status, 'value') else order.status
            text = (
                f"🚗 **Mashina:** {car.plate_number}\n"
                f"📌 **Status:** {status_val}\n"
                f"💰 **Narx:** {order.price or 'Belgilanmagan'} so'm\n"
                f"⏳ **Taxminiy vaqt:** {order.estimated_time or 'Noma’lum'}\n"
                f"📅 **Yaratilgan:** {order.created_at.strftime('%Y-%m-%d %H:%M')}"
            )

        await callback.message.edit_text(text, parse_mode="Markdown")
        await callback.answer()

    finally:
        db.close()


# Help handler

@user_router.message(lambda message: message.text == "📒 Qo'llanma")
async def help(message: Message):
        text = "📒 Qo‘llanma:\n\n"
        await message.answer(text)