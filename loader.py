from aiogram import Bot, Dispatcher
from database.session import SessionLocal
import config

# Bot and Dispatcher

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Helper: get DB session context

class DBSession:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()