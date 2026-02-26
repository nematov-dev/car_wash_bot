from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def get_admin_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Buyurtma qabul qilish")],
            [KeyboardButton(text="📊 Statistika"),KeyboardButton(text="⬅️ Admin panel")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_order_management_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✍️ Qo'lda kiritish")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_washers_inline_keyboard(washers):
    buttons = []
    for w in washers:
        buttons.append([
            InlineKeyboardButton(text=f"🧼 {w.full_name}", callback_data=f"set_washer_{w.id}")
        ])
    # Agar moykachi bo'lmasa yoki keyinroq tanlanadigan bo'lsa
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)