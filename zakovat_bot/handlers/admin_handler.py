from aiogram import F
from aiogram.types import CallbackQuery,   Message
from aiogram.filters import  StateFilter
from zakovat_bot.models import  TelegramAdminsID,Questions, Users
from zakovat_bot.dispatcher import dp,bot
from zakovat_bot.buttons.inline import *
from aiogram.fsm.context import FSMContext
from zakovat_bot.state import  QuestionState, Register,ChannelSendState
from django.utils import timezone
from zakovat_bot.utils import sent_file_to_admins
from decouple import config

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

    # Savolni DB ga vaqtincha saqlaymiz
    question = Questions.objects.create(
        name=question_name,
        file_id=message.audio.file_id if message.audio else
                message.photo[-1].file_id if message.photo else
                message.video.file_id if message.video else
                message.voice.file_id if message.voice else
                message.document.file_id if message.document else
                None,
        file_type=message.content_type,   
    )

    # Faqat preview ko‘rsatamiz (kanalga yubormaymiz!)
    kb = approve_keyboard(question.id)

    if message.text:
        await message.answer(message.text, reply_markup=kb)

    elif message.photo:
        await message.answer_photo(
            photo=message.photo[-1].file_id,
            caption=question_name,
            reply_markup=kb
        )

    elif message.audio:
        await message.answer_audio(
            audio=message.audio.file_id,
            caption=question_name,
            reply_markup=kb
        )

    elif message.video:
        await message.answer_video(
            video=message.video.file_id,
            caption=question_name,
            reply_markup=kb
        )

    elif message.voice:
        await message.answer_voice(
            voice=message.voice.file_id,
            caption=question_name,
            reply_markup=kb
        )

    elif message.document:
        await message.answer_document(
            document=message.document.file_id,
            caption=question_name,
            reply_markup=kb
        )

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
        first_line = question.name.split('\n')[0]
        text += f"{i}. 📄 Savol nomi: {first_line}\n"

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
        await sent_file_to_admins(question, callback_query.from_user.id)
        return
       
    elif action == "delete":
        question.delete()
        await callback_query.message.delete()
        await callback_query.message.answer(text="🗑 Savol muvaffaqiyatli o'chirildi.", reply_markup=admin_main_keyboard())
        
        
@dp.callback_query( F.data == "cancel")
async def admin_main(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(text="🤵🏼 Admin paneli",reply_markup=admin_main_keyboard())
    
    
@dp.callback_query(F.data == "admin_main_menu" )
async def admin_main_menu(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await callback_query.message.edit_text(text="Admin paneli",reply_markup=admin_main_keyboard())
    
    
@dp.callback_query(F.data.startswith("approve:"))
async def approve_publish(callback: CallbackQuery):
    question_id = int(callback.data.split(":")[1])
    question = Questions.objects.get(id=question_id)
    keyboard = main_keyboard(question.uuid)
    question.questioned_at = timezone.now()
    question.save()

    if question.file_type == "text":
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=question.name,
            reply_markup=keyboard
        )

    elif question.file_type == "photo":
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=question.file_id,
            caption=question.name,
            reply_markup=keyboard
        )

    elif question.file_type == "audio":
        await bot.send_audio(
            chat_id=CHANNEL_ID,
            audio=question.file_id,
            caption=question.name,
            reply_markup=keyboard
        )

    elif question.file_type == "video":
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=question.file_id,
            caption=question.name,
            reply_markup=keyboard
        )

    elif question.file_type == "voice":
        await bot.send_voice(
            chat_id=CHANNEL_ID,
            voice=question.file_id,
            caption=question.name,
            reply_markup=keyboard
        )

    elif question.file_type == "document":
        await bot.send_document(
            chat_id=CHANNEL_ID,
            document=question.file_id,
            caption=question.name,
            reply_markup=keyboard
        )

    await callback.message.edit_reply_markup()
    await callback.message.answer("📤 Kanalga muvaffaqiyatli joylandi!")
    await callback.answer()



@dp.callback_query(F.data == "user_talk")
async def user_talk(callback_query: CallbackQuery,state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.answer(text="💬 Suhbat uchun foydalanuvchi ID sini yuboring:",reply_markup=back_keyboard())
    await state.set_state(QuestionState.user_id)
    
    
@dp.message(StateFilter(QuestionState.user_id))
async def process_user_id(message: Message, state: FSMContext) -> None:
    tg_id_text = message.text.strip() if message.text else None
    if not tg_id_text or not tg_id_text.isdigit():
        await message.answer("❗️ Iltimos, foydalanuvchi ID sini to'g'ri formatda yuboring.",reply_markup=back_keyboard())
        return

    tg_id = int(tg_id_text)
    await state.update_data(user_talk_id=tg_id)
    if not Users.objects.filter(tg_id=tg_id).exists():
        await message.answer("❗️ Bunday ID li foydalanuvchi topilmadi. Iltimos, to'g'ri ID ni kiriting.",reply_markup=back_keyboard())
        return
    await message.answer(
        text=f"💬 Foydalanuvchi (ID: {tg_id}) bilan suhbatni boshlang. Sizning xabaringiz ushbu foydalanuvchiga yuboriladi.",reply_markup=back_keyboard()
    )
    await state.set_state(QuestionState.user_talk)

@dp.message(StateFilter(QuestionState.user_talk))
async def process_user_talk(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    tg_id = data.get("user_talk_id")
    msg_id = message.message_id

    try:
        await bot.send_message(
            chat_id=tg_id,
            text=f"💬 Admindan xabar:\n\n{message.text}",
            reply_markup=answer_admin(message.from_user.id, msg_id)
        )
        await message.answer("✅ Xabaringiz foydalanuvchiga yuborildi.\nYana gapingiz bolsa yozing",reply_markup=end_talk_keyboard())
    except Exception as e:
        await message.answer(f"❗️ Xatolik yuz berdi: {str(e)}")

@dp.callback_query(F.data.startswith("answer_admin_"))
async def answer_from_admin(callback_query: CallbackQuery,state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    tg_id = int(callback_query.data.split("_")[-2])
    msg_id = int(callback_query.data.split("_")[-1])
    await callback_query.message.answer(
        text=f"💬 Javobingizni yozing. Sizning habaringiz adminga yetkaziladi"
    )
    await state.update_data(answer_to_admin_id=tg_id, answer_to_admin_msg_id=msg_id)
    
    await state.set_state(QuestionState.user_answer)
    
    
@dp.message(StateFilter(QuestionState.user_answer))
async def process_answer_to_admin(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    tg_id = data.get("answer_to_admin_id")
    msg_id = data.get("answer_to_admin_msg_id")

    try:
        await bot.send_message(
            chat_id=tg_id,
            text=f"💬 Foydalanuvchidan javob:\n\n{message.text}",
            reply_to_message_id=msg_id
        )
        await message.answer("✅ Javobingiz adminga yuborildi.")
    except Exception as e:
        await message.answer(f"❗️ Xatolik yuz berdi: {str(e)}")
    await state.clear()
    
    
@dp.callback_query(F.data == "end_talk")
async def end_talk(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer("💬 Suhbat yakunlandi.",reply_markup=admin_main_keyboard())
    
@dp.callback_query(F.data == "broadcast_message")
async def broadcast_message(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.answer("📢 Iltimos, bot foydalanuvchilariga jo'natiladigan xabar matnini kiriting:",reply_markup=back_keyboard(    ))
    await state.set_state(Register.every_one)
    
@dp.message(StateFilter(Register.every_one))
async def process_broadcast_message(message: Message, state: FSMContext) -> None:
    text = message.text.strip() if message.text else None
    if not text:
        await message.answer("❗️ Iltimos, xabar matnini kiriting.")
        return

    users = Users.objects.all()
    success_count = 0
    fail_count = 0

    for user in users:
        try:
            await bot.send_message(
                chat_id=user.tg_id,
                text=f"📢 Botdan umumiy xabar:\n\n{text}"
            )
            success_count += 1
        except Exception:
            fail_count += 1

    await message.answer(f"📢 Xabar yuborildi.\nMuvaffaqiyatli: {success_count}\nMuvaffaqiyatsiz: {fail_count}",reply_markup=admin_main_keyboard())
    await state.clear()
    
@dp.callback_query(F.data == "back")
async def back_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(text="🤵🏼 Admin paneli",reply_markup=admin_main_keyboard())
    
@dp.callback_query(F.data == "chanel")
async def send_message_to_channel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.set_state(ChannelSendState.waiting_for_excel)
    await callback_query.message.answer("Excel file yuboring.")
    
    
    
import pandas as pd

@dp.message(ChannelSendState.waiting_for_excel, F.document)
async def handle_excel(message: Message, state: FSMContext):
    file = await message.bot.get_file(message.document.file_id)
    file_path = file.file_path
    downloaded = await message.bot.download_file(file_path)

    df = pd.read_excel(downloaded)
    links = (
    df.iloc[:, 1]
    .dropna()
    .astype(str)
    .str.strip()
    .apply(lambda x: x.replace("https://t.me/", "")
                       .replace("http://t.me/", "")
                       .replace("t.me/", "")
                       .replace("@", ""))
    .tolist()
)

    await state.update_data(links=links)
    await state.set_state(ChannelSendState.waiting_for_message)

    await message.answer("Endi yuboriladigan xabarni yuboring.")
    
    
from collections import defaultdict
import asyncio

media_buffer = defaultdict(list)
media_locks = {}


def parse_message_link(link: str):
    link = link.strip()

    if "t.me/c/" in link:
        parts = link.split("/")
        chat_id = int("-100" + parts[-2])
        message_id = int(parts[-1])
        return chat_id, message_id

    else:
        parts = link.split("/")
        username = parts[-2]
        message_id = int(parts[-1])
        return f"@{username}", message_id



@dp.message(ChannelSendState.waiting_for_post_link)
async def handle_post_link(message: Message, state: FSMContext):

    post_link = message.text.strip()

    try:
        source_chat_id, message_id = parse_message_link(post_link)
    except:
        await message.answer("Link noto‘g‘ri formatda.")
        return

    await state.update_data(
        source_chat_id=source_chat_id,
        message_id=message_id
    )

    await state.set_state(ChannelSendState.waiting_for_confirmation)

    await message.answer(
        "Forward qilamizmi?",
        reply_markup=confirm_keyboard()
    )



@dp.callback_query(ChannelSendState.waiting_for_confirmation, F.data == "confirm_yes")
async def confirm_send(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback_query.answer()

    links = data["links"]
    source_chat_id = data["source_chat_id"]
    message_id = data["message_id"]

    await callback_query.message.edit_text("Yuborilmoqda...")

    success = 0

    for link in links:
        target_chat = link.strip()

        if not target_chat.startswith("@") and not target_chat.startswith("-100"):
            target_chat = f"@{target_chat}"

        print(f"Forward: {source_chat_id}/{message_id} → {target_chat}")

        try:
            await callback_query.bot.forward_message(
                chat_id=target_chat,
                from_chat_id=source_chat_id,
                message_id=message_id
            )
            success += 1
        except Exception as e:
            print(f"Xatolik {target_chat}: {e}")

        await asyncio.sleep(0.05)

    await state.clear()

    await callback_query.message.edit_text(
        f"Yuborildi: {success} ta."
    )



@dp.callback_query(ChannelSendState.waiting_for_confirmation, F.data == "confirm_no")
async def cancel_send(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()

    await callback_query.message.edit_text(
        "Bekor qilindi.",
        reply_markup=admin_main_keyboard()
    )