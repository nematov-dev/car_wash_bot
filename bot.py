import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from database.models import User
from database.session import SessionLocal, init_db
from keyboards.user_kb import get_main_user_menu
from handlers.user import user_router
import config


# Bot & Dispatcher

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


# Helper: get DB session context

class DBSession:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

# Connect routers

dp.include_router(user_router)


# Start handler

@dp.message(Command("start"))
async def start_handler(message: types.Message):

    with DBSession() as db:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

        if not user:
            # create user
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



# Async main 

async def main():

    # DB create

    init_db()
    print("✅ Database tables created!")

    # Bot start

    print("🚀 Bot ishga tushmoqda...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


# Run 

if __name__ == "__main__":
    asyncio.run(main())