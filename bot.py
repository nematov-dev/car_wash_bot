import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from database.models import Base, User
from database.session import engine, SessionLocal, init_db

from decouple import config

BOT_TOKEN = config("BOT_TOKEN")

# Bot and Dispatcher

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Handler: /start

@dp.message(Command("start"))
async def start_handler(message: Message):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

        if not user:
            # User not found → create new user
            new_user = User(
                telegram_id=message.from_user.id,
                full_name=message.from_user.full_name
            )
            db.add(new_user)
            db.commit()
            await message.answer("Xush kelibsiz 🚗 Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!")
        else:
            await message.answer("Salom 👋 Siz allaqachon ro‘yxatdan o‘tgansiz.")

    finally:
        db.close()


# Async main

async def main():
    # DB create
    init_db()
    print("✅ Database tables created!")

    # Bot polling start
    print("🚀 Bot ishga tushmoqda...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


# Run bot

if __name__ == "__main__":
    asyncio.run(main())