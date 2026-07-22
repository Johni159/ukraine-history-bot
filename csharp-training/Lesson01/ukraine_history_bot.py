import random
import os
import sys
import asyncio
from telegram import Poll, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Завантажуємо змінні оточення
load_dotenv()

# Імпортуємо базу подій (переконайся, що файл events.py лежить поруч)
try:
    from events import events
except ImportError:
    print("❌ ПОМИЛКА: Файл events.py не знайдено!")
    events = []

# Конфігурація з .env
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID', '@your_channel_username')  # Безпечний плейсхолдер

if not TOKEN:
    raise ValueError("❌ ПОМИЛКА: TELEGRAM_TOKEN не знайдено у .env файлі!")

poll_queue = []

def get_random_poll():
    global poll_queue

    if not events:
        return None

    if not poll_queue:
        poll_queue = events.copy()
        random.shuffle(poll_queue)

    event = poll_queue.pop()

    # Якщо це питання про рік (є ключі "event" та "year")
    if "event" in event and "year" in event:
        correct_year = event["year"]
        years_pool = [
            e["year"] for e in events
            if "year" in e and e["year"] != correct_year
        ]
        years_pool = list(set(years_pool))
        if len(years_pool) >= 3:
            wrong_years = random.sample(years_pool, 3)
        else:
            wrong_years = [correct_year + 1, correct_year - 1, correct_year + 5]

        options = [correct_year] + wrong_years
        random.shuffle(options)
        return {
            'question': f"У якому році відбулася подія: {event['event']}?",
            'options': [str(opt) for opt in options],
            'correct_option_id': options.index(correct_year)
        }

    # Якщо це факт (є ключі "question", "options", "correct_option_id")
    elif all(k in event for k in ("question", "options", "correct_option_id")):
        options = event["options"].copy()
        correct_answer = options[event["correct_option_id"]]
        random.shuffle(options)
        correct_option_id = options.index(correct_answer)
        return {
            'question': event["question"],
            'options': options,
            'correct_option_id': correct_option_id
        }

    return None


async def send_poll_job(context: ContextTypes.DEFAULT_TYPE):
    """Задача для вбудованого JobQueue: автоматична відправка опитування"""
    try:
        q = get_random_poll()
        if q:
            await context.bot.send_poll(
                chat_id=CHANNEL_ID,
                question=q['question'],
                options=q['options'],
                type=Poll.QUIZ,
                correct_option_id=q['correct_option_id'],
                is_anonymous=True
            )
            print(f"✅ Авто-опитування відправлено: {q['question'][:50]}...")
        else:
            print("⚠️ База подій порожня.")
    except Exception as e:
        print(f"❌ Помилка при авто-відправленні: {e}")


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /test для ручної перевірки"""
    try:
        q = get_random_poll()
        if q:
            await context.bot.send_poll(
                chat_id=update.effective_chat.id,
                question=q['question'],
                options=q['options'],
                type=Poll.QUIZ,
                correct_option_id=q['correct_option_id'],
                is_anonymous=False
            )
        else:
            await update.message.reply_text("⚠️ База подій порожня!")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка: {e}")


def main():
    """Головна функція запуску"""
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    print("🚀 Бот стартує...")
    print(f"📊 Завантажено подій: {len(events)}")

    # Створюємо додаток (включає підтримку job_queue за замовчуванням)
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Реєструємо планувальник на базі JobQueue (кожні 5 хвилин = 300 сек)
    job_queue = application.job_queue
    job_queue.run_repeating(send_poll_job, interval=300, first=10)
    print("📅 Автоматичні публікації налаштовано (кожні 5 хв)")

    # Реєструємо команду /test
    application.add_handler(CommandHandler("test", test_command))
    print("📡 Бот запущений та готовий до роботи.")
    
    application.run_polling()


if __name__ == '__main__':
    main()
