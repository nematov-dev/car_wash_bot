from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def get_admin_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Buyurtma qabul qilish (qo'lda)")],
            [KeyboardButton(text="📊 Statistika"),KeyboardButton(text="⬅️ Admin panel")],
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
    buttons.append([InlineKeyboardButton(text="⛔️ Bekor qilish", callback_data="cancel_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_audio_confirm_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_audio_order"),
                InlineKeyboardButton(text="🔄 Qayta yuborish", callback_data="retry_audio_order")
            ],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")]
        ]
    )
    return keyboard


def get_services_reply_keyboard(services):
    buttons = []
    row = []
    for s in services:
        row.append(KeyboardButton(text=s.name))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    
    buttons.append([KeyboardButton(text="➡️ O'tkazib yuborish")])
    buttons.append([KeyboardButton(text="🏠 Bosh sahifa")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_washers_reply_keyboard(washers):
    buttons = []
    row = []
    for w in washers:
        row.append(KeyboardButton(text=w.full_name))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([KeyboardButton(text="✖️ Bekor qilish")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_skip_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➡️ O'tkazib yuborish")],
            [KeyboardButton(text="✖️ Bekor qilish")]
        ],
        resize_keyboard=True
    )


def admin_cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✖️ Bekor qilish")],
        ],
        resize_keyboard=True
    )

