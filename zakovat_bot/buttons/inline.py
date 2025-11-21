from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Yangi savol", callback_data="add_new_question"),
            InlineKeyboardButton(text="❓ Savollar ro'yxati", callback_data="questions_list"),
        ],
    ])
    return keyboard

def main_keyboard(uuid) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✍️ Javob berish", url=f"https://t.me/yoshlaruchuntanlov_bot?start={uuid}"),
        ],
    ])
    return keyboard

def back_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back"),
        ],
    ])
    return keyboard


def change_question_keyboard(question_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📥 Javoblarni yuklab olish", callback_data=f"change_download_{question_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Savolni o'chirish", callback_data=f"change_delete_{question_id}"),
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="questions_list"),
        ],
      
    ])
    return keyboard


def questions_list_keyboard(questions, page: int, total: int, per_page: int):
    builder = InlineKeyboardBuilder()
    start_index = (page - 1) * per_page

    for i, q in enumerate(questions, start=start_index + 1):
        builder.button(
            text=str(i),
            callback_data=f"question_detail_{q.id}"
        )

    builder.adjust(5)
    nav_buttons = []
    total_pages = (total + per_page - 1) // per_page

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"questions_list:{page - 1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"questions_list:{page + 1}"
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    # Orqaga tugmasi
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="admin_main_menu"
        )
    )

    return builder.as_markup()