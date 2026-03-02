from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def get_admin_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Buyurtma qabul qilish (qo'lda)"),KeyboardButton(text="🟢 Buyurtma bajarildi")],
            [KeyboardButton(text="📊 Hisobot"),KeyboardButton(text="⬅️ Admin panel")],
        ],
        resize_keyboard=True
    )
    return keyboard



def get_active_orders_keyboard(active_orders):
    buttons = []
    for order in active_orders:
        buttons.append([
            InlineKeyboardButton(
                text=f"🚗 {order.car.plate_number} (Yakunlash)", 
                callback_data=f"finish_order_{order.id}"
            )
        ])
    
    if active_orders:
        buttons.append([InlineKeyboardButton(text="✅ Hammasini yakunlash", callback_data="finish_all_orders")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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
    buttons.append([KeyboardButton(text="✖️ Bekor qilish")])
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

def get_report_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 1 kunlik")],
            [KeyboardButton(text="📊 1 haftalik")],
            [KeyboardButton(text="📊 1 oylik")],
            [KeyboardButton(text="📅 Sana bo‘yicha")],
            [KeyboardButton(text="🏠 Bosh sahifa")]
        ],
        resize_keyboard=True
    )


# Admin panel reply keyboard

def get_admin_panel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👷 Ishchilar"), KeyboardButton(text="🛡️ Adminlar")],
            [KeyboardButton(text="🛠 Xizmatlar"), KeyboardButton(text="✉️ Xabar yuborish")],
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="🏠 Bosh sahifa")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Workers CRUD


def workers_crud():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Ishchi qo‘shish", callback_data="add_worker"),
                InlineKeyboardButton(text="🗑️ Ishchi o‘chirish", callback_data="delete_worker")
            ]
        ]
    )
    return keyboard


# Admins CRUD

def admins_crud():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Admin qo‘shish", callback_data="add_admin"),
                InlineKeyboardButton(text="🗑️ Admin o‘chirish", callback_data="delete_admin")
            ]
        ]
    )
    return keyboard


# Services

def services_crud():
    buttons = [
        [
            InlineKeyboardButton(text="➕ Xizmat qo‘shish", callback_data="add_service"),
            InlineKeyboardButton(text="🗑 Xizmat o‘chirish", callback_data="delete_service")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Send Message

def get_broadcast_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Hamma userlarga yuborish", callback_data="broadcast_all")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_admin")]
        ]
    )
    return keyboard


# Statistics

def get_statistics_keyboard(user_count, order_count=None):
    buttons = [
        [InlineKeyboardButton(text=f"👤 Userlar: {user_count}", callback_data="stat_users")],
    ]
    if order_count is not None:
        buttons.append([InlineKeyboardButton(text=f"🧾 Buyurtmalar: {order_count}", callback_data="stat_orders")])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)