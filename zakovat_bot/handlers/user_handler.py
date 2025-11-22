from aiogram import F
from aiogram.types import CallbackQuery, Message,ReplyKeyboardRemove
from aiogram.filters import Command , StateFilter
from zakovat_bot.models import  TelegramAdminsID,Users,Questions,Answers
from zakovat_bot.dispatcher import dp
from zakovat_bot.buttons.inline import *
from zakovat_bot.buttons.reply import *
from aiogram.fsm.context import FSMContext
from zakovat_bot.state import Register
from django.utils import timezone
from zakovat_bot.utils import sent_file_to_admins

@dp.message(Command("start"))
async def start(message: Message,state: FSMContext) -> None:
    tg_id = message.from_user.id
    username = message.from_user.username or ""
    if TelegramAdminsID.objects.filter(tg_id=tg_id).exists():
        await message.answer(text="Siz admin panelidasiz.",reply_markup=admin_main_keyboard())
        return
    if not Users.objects.filter(tg_id=message.from_user.id).exists():
        Users.objects.create(tg_id=message.from_user.id,username=username)
        await message.answer(text="Iltimos, to'liq ismingizni kiriting:",reply_markup=ReplyKeyboardRemove())
        await state.set_state(Register.full_name)
        return
    user = Users.objects.get(tg_id=tg_id)
    if not " " in message.text:
        await message.answer(text="Botga xush kelibsiz! ",reply_markup=user_profile_keyboard())
        return
    args = message.text.split(" ")[1]
    question = Questions.objects.get(uuid=args)
    if question.questioned_at + timezone.timedelta(days=1) < timezone.now():
        await message.answer(text="Ushbu savolga javob berish muddati tugagan.",reply_markup=ReplyKeyboardRemove())
        if not question.answers_file_sent:
            await sent_file_to_admins(question)
        return
    if  Answers.objects.filter(user_id=user.id,question_id=question.id).exists():
        await message.answer(text="Siz allaqachon javob bergansiz.",reply_markup=ReplyKeyboardRemove())
        return
    await state.update_data(question_id=question.id)
    await message.answer(text="Javobingizni kiriting:")
    await state.set_state(Register.answer)
    return


@dp.message(StateFilter(Register.full_name))
async def register_full_name(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    user = Users.objects.get(tg_id=tg_id)
    user.full_name = message.text
    user.save()
    await message.answer(text="Iltimos, telefon raqamingizni ulashing:",reply_markup=ask_phone_keyboard())
    await state.set_state(Register.phone_number)
    
@dp.message(StateFilter(Register.phone_number))
async def register_phone_number(message: Message, state: FSMContext):

    # 1️⃣ Agar foydalanuvchi "kontakt" yubormagan bo‘lsa
    if not message.contact:
        await message.answer(
            text="❗️ Iltimos, telefon raqamingizni yuborish uchun pastdagi "
                 "📞 *“Nomer jo‘natish”* tugmasini bosing.",
            reply_markup=ask_phone_keyboard(), 
            parse_mode="Markdown"
        )
        return

    tg_id = message.from_user.id
    user = Users.objects.get(tg_id=tg_id)
    user.phone_number = message.contact.phone_number
    user.save()

    await message.answer(
        text="✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi.\n"
             "Savolga javob berish tugmasini qaytadan bosing.",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.clear()

@dp.callback_query(F.data == "user_profile")
async def user_profile(callback: CallbackQuery):
    await callback.answer()
    tg_id = callback.from_user.id
    user = Users.objects.get(tg_id=tg_id)
    profile_text = f"👤 <b>Foydalanuvchi profili:</b>\n\n"
    profile_text += f"📝 <b>To'liq ism:</b> {user.full_name or 'Noma\'lum'}\n"
    profile_text += f"📞 <b>Telefon raqam:</b> {user.phone_number or 'Noma\'lum'}\n"
    profile_text += f"🔖 <b>Username:</b> @{user.username}\n"
    await callback.message.answer(text=profile_text,parse_mode="HTML",reply_markup=change_info_keyboard())
    
@dp.callback_query(F.data == "change_info")
async def change_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(text="Iltimos, to'liq ismingizni kiriting:",reply_markup=ReplyKeyboardRemove())
    await state.set_state(Register.full_name)

@dp.message(StateFilter(Register.answer))
async def process_answer(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    user = Users.objects.get(tg_id=tg_id)
    data = await state.get_data()
    question_id = data.get("question_id")
    question = Questions.objects.get(id=question_id)
    Answers.objects.create(
        question=question,
        user=user,
        answer=message.text,
        answered_at=timezone.now()
    )
    await message.answer(text="Javobingiz qabul qilindi. Rahmat!",reply_markup=ReplyKeyboardRemove())
    await state.clear()