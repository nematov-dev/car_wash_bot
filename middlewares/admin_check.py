from aiogram import BaseMiddleware
from loader import DBSession
from database.models import User, UserRole
from decouple import config


SUPER_ADMIN_ID = int(config("ADMIN_TELEGRAM_ID", default=0))

# Admin check

class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id

        if user_id == SUPER_ADMIN_ID:
            return await handler(event, data)

        with DBSession() as db:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            
            if user and user.role == UserRole.admin:
                return await handler(event, data)
        return