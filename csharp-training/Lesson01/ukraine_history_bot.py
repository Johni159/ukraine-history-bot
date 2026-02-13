   python ukraine_history_bot.py

import asyncio
import random
from telegram import Poll
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = '8309839168:AAH7L9h6q20gD0OHUnV3G-CHbnqjtxsyZI8'
GROUP_ID = -5148918793

# Шаблони для генерації питань
question_templates = [
    {
        'question': "У якому році відбулася подія №{num}?",
        'options': ["{year1}", "{year2}", "{year3}", "{year4}"],
        'correct_option_id': 0
    },
    # Можна додати ще шаблонів для різноманітності
]

# Список років для генерації
years = list(range(1500, 2025))
# --- ТУТ ДОДАЙ СПИСОК ПОДІЙ ---
events = [
    {"year": 882, "event": "Київ став столицею Київської Русі"},
    {"year": 1240, "event": "Монгольська навала — розгром Києва"},
    {"year": 1654, "event": "Підписання Переяславської угоди"},
    {"year": 1917, "event": "Проголошення Української Народної Республіки"},
    {"year": 1918, "event": "Проголошення Західноукраїнської Народної Республіки"},
    {"year": 1932, "event": "Початок Голодомору"},
    {"year": 1991, "event": "Проголошення незалежності України"},
    {"year": 1996, "event": "Прийняття Конституції України"},
    {"year": 2004, "event": "Помаранчева революція"},
    {"year": 2014, "event": "Революція Гідності"},
    {"year": 2014, "event": "Анексія Криму Росією"},
    {"year": 2022, "event": "Повномасштабне вторгнення Росії в Україну"},
]
# --- КІНЕЦЬ СПИСКУ ---

def generate_question(index):
    event = events[index % len(events)]
    correct_year = event["year"]
    # Вибираємо три інші роки для варіантів відповіді
    wrong_years = random.sample([e["year"] for e in events if e["year"] != correct_year], 3)
    options = [correct_year] + wrong_years
    random.shuffle(options)
    correct_option_id = options.index(correct_year)
    question_text = f"У якому році відбулася подія: {event['event']}?"
    options_text = [str(opt) for opt in options]
    return {
        'question': question_text,
        'options': options_text,
        'correct_option_id': correct_option_id
    }

TOTAL_QUESTIONS = 500
questions = [generate_question(i) for i in range(TOTAL_QUESTIONS)]
current_index = 0

async def send_poll(application):
    global current_index
    q = questions[current_index]
    await application.bot.send_poll(
        chat_id=GROUP_ID,
        question=q['question'],
        options=q['options'],
        type=Poll.QUIZ,
        correct_option_id=q['correct_option_id'],
        is_anonymous=False
    )
    current_index += 1
    if current_index >= len(questions):
        # Коли питання закінчились — згенерувати нові і почати знову
        regenerate_questions()
        current_index = 0

def regenerate_questions():
    global questions
    questions = [generate_question(i) for i in range(TOTAL_QUESTIONS)]
    print("Питання згенеровано наново!")

async def test_command(update, context: ContextTypes.DEFAULT_TYPE):
    global current_index
    q = questions[current_index]
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=q['question'],
        options=q['options'],
        type=Poll.QUIZ,
        correct_option_id=q['correct_option_id'],
        is_anonymous=False
    )
    current_index += 1
    if current_index >= len(questions):
        regenerate_questions()
        current_index = 0

async def on_startup(application):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_poll, 'cron', minute='*', args=[application])
    scheduler.start()
    print("Планувальник запущено, опитування буде кожну хвилину.")

if __name__ == '__main__':
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    application = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()
    application.add_handler(CommandHandler("test", test_command))
    application.run_polling()
