
import random
from telegram import Poll, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from events import events  # Імпортуємо список подій

# Константи
TOKEN = '8309839168:AAE3zO4AloXymKUC1i4fDao7DFdNXZfkBsI'
GROUP_ID = -5148918793

poll_queue = []
def get_random_poll():
    global poll_queue

    if not events:
        return None

    # Якщо черга пуста — перемішуємо нову
    if not poll_queue:
        poll_queue = events.copy()
        random.shuffle(poll_queue)

    event = poll_queue.pop()

    if event.get("type") == "year":
        correct_year = event["year"]
        years_pool = list(set([e["year"] for e in events if e.get("type") == "year" and e["year"] != correct_year]))
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

    elif event.get("type") == "fact":
        return {
            'question': event["question"],
            'options': event["options"],
            'correct_option_id': event["correct_option_id"]
        }

    else:
        return None


async def send_poll(application):
    """Задача для планувальника: відправка опитування"""
    q = get_random_poll()
    if q:
        await application.bot.send_poll(
            chat_id=GROUP_ID,
            question=q['question'],
            options=q['options'],
            type=Poll.QUIZ,
            correct_option_id=q['correct_option_id'],
            is_anonymous=False
        )
    else:
        print("⚠️ База подій порожня, опитування не відправлено.")

# Команда для перевірки роботи бота
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот працює!")

# Функція, яка запускає планувальник
async def on_startup(application):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_poll, "interval", minutes=5, args=[application])
    scheduler.start()
    print("Планувальник запущено!")

if __name__ == '__main__':  # Ось тут була помилка, має бути __name__ == '__main__'
    import sys
    if sys.platform.startswith('win'):
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("Бот стартує!")
    application = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()
    application.add_handler(CommandHandler("test", test_command))
    print("Завантаження подій з events.py...")
    application.run_polling()
