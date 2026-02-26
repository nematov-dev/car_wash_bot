from aiogram.types import ReplyKeyboardMarkup, KeyboardButton 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def get_main_user_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠️ Xizmatlar"),KeyboardButton(text="🔍 Buyurtmani tekshirish")],
            [KeyboardButton(text="➕ Moshina qo'shish"),KeyboardButton(text="👤 Hisobim")],
            [KeyboardButton(text="📒 Qo'llanma")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


def get_cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_user_cars_keyboard(cars):
    buttons = []
    for car in cars:
        buttons.append([
            InlineKeyboardButton(
                text=car.plate_number,
                callback_data=f"car_status_{car.id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_account_settings_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑️ Mashinani o'chirish", callback_data="start_delete_process")]
        ]
    )
    return keyboard


def get_cars_delete_list_keyboard(cars):
    buttons = []
    for car in cars:
        buttons.append([
            InlineKeyboardButton(text=f"{car.plate_number}", callback_data=f"del_select_{car.id}")
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_account")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_delete_kb(car_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=f"del_confirm_{car_id}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data="start_delete_process")
            ]
        ]
    )
    return keyboard