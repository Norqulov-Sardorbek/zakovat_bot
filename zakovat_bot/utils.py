from aiogram.types import  BotCommand
from zakovat_bot.models import TelegramAdminsID, Users, Answers
from io import BytesIO
from openpyxl import Workbook
from aiogram.types import BufferedInputFile
from zakovat_bot.dispatcher import bot
async def set_bot_commands(bot):
    commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish"),
    ]
    await bot.set_my_commands(commands)

def humanize_timedelta(delta):
    total_seconds = int(delta.total_seconds())
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    parts = []
    if hours:
        parts.append(f"{hours} soat")
    if minutes:
        parts.append(f"{minutes} daqiqa")
    if seconds or not parts:
        parts.append(f"{seconds} soniya")

    return " ".join(parts)



def build_answers_excel(question):
    wb = Workbook()
    ws = wb.active
    ws.title = "Answers"

    # Sarlavhalar
    ws.append(["Telegram ID", "Username", "Phone number", "Full name", "Answer", "Answer time"])

    answers = (
        Answers.objects
        .filter(question=question)
        .select_related("user")
        .order_by("answered_at")
    )

    for ans in answers:
        delta = ans.answered_at - question.questioned_at
        answer_time_str = humanize_timedelta(delta)

        ws.append([
            ans.user.tg_id or "",
            ans.user.username or "",
            ans.user.phone_number or "",
            ans.user.full_name or "",
            ans.answer,
            answer_time_str,
        ])

    # Faylni xotirada saqlaymiz
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

async def sent_file_to_admins( question):
    excel_buffer = build_answers_excel(question)
    file_bytes = excel_buffer.getvalue()
    filename = f"{question.name}.xlsx"

    admins = TelegramAdminsID.objects.all()
    doc = BufferedInputFile(file_bytes, filename=filename)

    for admin in admins:
        try:
            await bot.send_document(
                chat_id=admin.tg_id,
                document=doc,
                caption=f"Savol ID: {question.name} bo'yicha barcha javoblar."
            )
        except Exception as e:
            print(f"Admin {admin.tg_id} ga yuborishda xatolik: {e}")

    # 4) Flagni yangilash
    question.answers_file_sent = True
    question.save(update_fields=["answers_file_sent"])
