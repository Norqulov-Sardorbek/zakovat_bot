from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



def ask_phone_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard