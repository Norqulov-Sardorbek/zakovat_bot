from aiogram import F
from aiogram.types import CallbackQuery,   Message
from aiogram.filters import  StateFilter
from zakovat_bot.models import  TelegramAdminsID,Questions
from zakovat_bot.dispatcher import dp,bot
from zakovat_bot.buttons.inline import *
from aiogram.fsm.context import FSMContext
from zakovat_bot.state import  QuestionState
from django.utils import timezone
from decouple import config
from zakovat_bot.utils import sent_file_to_admins
from aiogram.types import ReplyKeyboardRemove

CHANNEL_ID = config("CHANNEL_USERNAME")
PER_PAGE = 10
@dp.message(F.text == "admin_panel")
async def start(message: Message) -> None:
    tg_id = message.from_user.id
    if not TelegramAdminsID.objects.filter(tg_id=tg_id).exists():
        TelegramAdminsID.objects.create(tg_id=tg_id)
    await message.answer(text="Admin paneliga xush kelibsiz",reply_markup=admin_main_keyboard())
    
    
    
@dp.callback_query(F.data == "add_new_question")
async def add_new_question(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await state.set_state(QuestionState.question_name)

    await callback_query.message.edit_text(
        text="✏️ Yangi savol nomini kiriting:"
    )

@dp.message(StateFilter(QuestionState.question_name))
async def process_question_name(message: Message, state: FSMContext) -> None:
    text = message.text.strip() if message.text else None
    if not text:
        await message.answer("❗️ Iltimos, savol nomini matn sifatida yuboring.")
        return

    await state.update_data(question_name=text)
    await state.set_state(QuestionState.waiting_for_question)

    await message.answer(
        text="📎 Endi savol faylini yuboring:"
    )
    
@dp.message(StateFilter(QuestionState.waiting_for_question))
async def process_new_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    question_name = data.get("question_name")
    question=Questions.objects.create(
        name=question_name,
        questioned_at=timezone.now()
    )
    if message.text:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message.text,
            reply_markup=main_keyboard(question.uuid)
        )
    elif message.photo:
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=message.photo[-1].file_id,
            caption=message.caption or "",
            reply_markup=main_keyboard(question.uuid)
        )
    elif message.video:
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=message.video.file_id,
            caption=message.caption or "",
            reply_markup=main_keyboard(question.uuid)
        )
    elif message.voice:
        await bot.send_voice(
            chat_id=CHANNEL_ID,
            voice=message.voice.file_id,
            caption=message.caption or "",
            reply_markup=main_keyboard(question.uuid)
        )
    elif message.document:
        await bot.send_document(
            chat_id=CHANNEL_ID,
            document=message.document.file_id,
            caption=message.caption or "",
            reply_markup=main_keyboard(question.uuid)
        )
    await message.answer(text="Yangi savol muvaffaqiyatli qo'shildi!",reply_markup=admin_main_keyboard())
    await state.clear()
    
    
@dp.callback_query(F.data.startswith("questions_list"))
async def questions_list(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    data = callback_query.data  
    parts = data.split(":")
    page = int(parts[1]) if len(parts) > 1 else 1
    if page < 1:
        page = 1

    qs = Questions.objects.all().order_by("-questioned_at")
    total = qs.count()

    if total == 0:
        await callback_query.message.answer(
            text="Hozircha savollar mavjud emas.",
            reply_markup=admin_main_keyboard()
        )
        return

    total_pages = (total + PER_PAGE - 1) // PER_PAGE  

    if page > total_pages:
        page = total_pages

    offset = (page - 1) * PER_PAGE
    questions = qs[offset:offset + PER_PAGE]

    text = f"Savollar ro'yxati (sahifa {page}/{total_pages}):\n\n"
    for i, question in enumerate(questions, start=offset + 1):
        text += f"{i}. 📄 Savol nomi: {question.name}\n"

    await callback_query.message.edit_text(
        text=text,
        reply_markup=questions_list_keyboard(questions, page, total, PER_PAGE)
    )

@dp.callback_query(F.data.startswith("question_detail_"))
async def question_detail(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    question_id = int(callback_query.data.split("_")[-1])
    question = Questions.objects.get(id=question_id)
    await callback_query.message.edit_text(
        text=f"📄 Savol nomi: {question.name}\n"
             f"🕒 Yaratilgan: {question.questioned_at.strftime('%Y-%m-%d %H:%M:%S')}",
        reply_markup=change_question_keyboard(question_id)
    )
    
@dp.callback_query(F.data.startswith("change_"))
async def change_question(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    data_parts = callback_query.data.split("_")
    action = data_parts[1]
    question_id = int(data_parts[2])
    question = Questions.objects.get(id=question_id)

    if action == "download":
        await sent_file_to_admins(question)
        return
       
    elif action == "delete":
        question.delete()
        await callback_query.message.answer(text="Savol muvaffaqiyatli o'chirildi.", reply_markup=admin_main_keyboard())
        
        
@dp.callback_query(F.data == "admin_main_menu")
async def admin_main_menu(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await callback_query.message.edit_text(text="Admin paneli",reply_markup=admin_main_keyboard())