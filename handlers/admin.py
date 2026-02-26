from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loader import DBSession
from database.models import Car, Washer, Order, OrderStatus, User, UserRole
from keyboards.admin_kb import (
    get_washers_inline_keyboard, 
    get_admin_main_menu, 
    get_order_management_keyboard
)
from states.states import ManualOrderStates

admin_router = Router()

# Admin panelga kirish
@admin_router.message(F.text == "⬅️ Admin panel")
async def admin_panel_main(message: Message):
    await message.answer("Asosiy admin panel menyusi:", reply_markup=get_admin_main_menu())

# Buyurtma qabul qilish bo'limi
@admin_router.message(F.text == "📥 Buyurtma qabul qilish")
async def order_menu(message: Message):
    await message.answer("Buyurtma bo'limi:", reply_markup=get_order_management_keyboard())

# 1. Jarayonni boshlash (Qo'lda kiritish)
@admin_router.message(F.text == "✍️ Qo'lda kiritish")
async def manual_order_start(message: Message, state: FSMContext):
    await message.answer("🚗 Mashina davlat raqamini kiriting:\n(Misol: 01A777AA)")
    await state.set_state(ManualOrderStates.waiting_for_plate)

# 2. Raqamni qabul qilish va Mashinani bazadan tekshirish
@admin_router.message(ManualOrderStates.waiting_for_plate)
async def process_plate_number(message: Message, state: FSMContext):
    plate = message.text.strip().upper()
    
    with DBSession() as db:
        # Mashinani qidirish, bo'lmasa yaratish
        car = db.query(Car).filter(Car.plate_number == plate).first()
        if not car:
            car = Car(plate_number=plate)
            db.add(car)
            db.commit()
            db.refresh(car)
        
        # Faol moykachilarni olish
        washers = db.query(Washer).filter(Washer.active == True).all()
        
        if not washers:
            await message.answer("⚠️ Faol moykachilar topilmadi! Avval ishchi qo'shing.")
            await state.clear()
            return

        await state.update_data(car_id=car.id, plate_number=plate)
        
        await message.answer(
            f"🚘 Mashina: {plate}\n\nKim yuvadi? Ishchini tanlang:",
            reply_markup=get_washers_inline_keyboard(washers)
        )
        await state.set_state(ManualOrderStates.selecting_washer)

# 3. Moykachi tanlanganda Order yaratish
@admin_router.callback_query(ManualOrderStates.selecting_washer, F.data.startswith("set_washer_"))
async def finalize_manual_order(callback: CallbackQuery, state: FSMContext):
    washer_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    car_id = data.get('car_id')
    plate = data.get('plate_number')

    with DBSession() as db:
        washer = db.query(Washer).get(washer_id)
        
        # Yangi buyurtma yaratish
        new_order = Order(
            car_id=car_id,
            washer_id=washer_id,
            status=OrderStatus.washing
        )
        db.add(new_order)
        db.commit()

        # 1. Avvalgi inline tugmalarni o'chirib, matnni yangilaymiz
        await callback.message.edit_text(
            f"✅ Buyurtma muvaffaqiyatli yaratildi!\n\n"
            f"🚗 Mashina: {plate}\n"
            f"🧼 Moykachi: {washer.full_name}\n"
            f"⏳ Status: Yuvilmoqda..."
        )
    
    # 2. Yangi xabar bilan asosiy menyuni yuboramiz
    await callback.message.answer(
        "Asosiy menyuga qaytdingiz:",
        reply_markup=get_admin_main_menu()
    )
    
    await state.clear()
    await callback.answer()

# Bekor qilish (Callback orqali)
@admin_router.callback_query(F.data == "cancel_admin")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Amal bekor qilindi. ❌")
    await callback.answer()