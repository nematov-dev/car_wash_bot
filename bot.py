import asyncio
from aiogram import types
from aiogram.filters import Command

from loader import bot, dp, DBSession
from database.models import User
from database.session import init_db
from keyboards.user_kb import get_main_user_menu
from handlers.user import user_router

# Connect routers

dp.include_router(user_router)


# Start command handler

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    with DBSession() as db:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

        if not user:
            new_user = User(
                telegram_id=message.from_user.id,
                full_name=message.from_user.full_name
            )
            db.add(new_user)
            db.commit()
            await message.answer(
                "Assalomu alaykum, botimizga xush kelibsiz!\n\n Menudan kerakli bo‘limni tanlang 👇🏻",
                reply_markup=get_main_user_menu()
            )
        else:
            await message.answer("Marhamat o'zingizga kerakli bo'limni tanlang:",
                                 reply_markup=get_main_user_menu())

async def main():
    
    # Create database tables

    init_db()
    print("✅ Database tables created!")

    print("🚀 Bot ishga tushmoqda...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())