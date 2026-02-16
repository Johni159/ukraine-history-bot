import random
import os
import sys
import asyncio
from telegram import Poll, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# Завантажуємо змінні оточення
load_dotenv()

from events import events

# Константи з .env файлу
TOKEN = os.getenv('TELEGRAM_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID', '-5148918793'))

if not TOKEN:
    raise ValueError("❌ ПОМИЛКА: TELEGRAM_TOKEN не знайдено у .env файлі!")

poll_queue = []

def shuffle_fact_options(events):
    import random
    for event in events:
        if event.get("type") == "fact":
            correct_answer = event["options"][event["correct_option_id"]]
            random.shuffle(event["options"])
            event["correct_option_id"] = event["options"].index(correct_answer)


def get_random_poll():
    """
    Отримує випадкове опитування з черги.
    Якщо черга порожня, перемішує нову з усіх подій.
    """
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
        # Отримуємо всі роки, крім поточного
        years_pool = [
            e["year"] for e in events 
            if e.get("type") == "year" and e["year"] != correct_year
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

    elif event.get("type") == "fact":
        # --- Додаємо перемішування варіантів ---
        options = event["options"].copy()
        correct_answer = options[event["correct_option_id"]]
        random.shuffle(options)
        correct_option_id = options.index(correct_answer)
        return {
            'question': event["question"],
            'options': options,
            'correct_option_id': correct_option_id
        }
    else:
        return None


async def send_poll(application):
    """Задача для планувальника: відправка опитування"""
    try:
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
            print(f"✅ Опитування відправлено: {q['question'][:50]}...")
        else:
            print("⚠️ База подій порожня, опитування не відправлено.")
    except Exception as e:
        print(f"❌ Помилка при відправленні опитування: {e}")


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /test для перевірки роботи бота"""
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


async def on_startup(application):
    """Функція, яка запускає планувальник при старті бота"""
    try:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(send_poll, "interval", minutes=5, args=[application])
        scheduler.start()
        print("✅ Планувальник запущено! Опитування кожні 5 хвилин.")
    except Exception as e:
        print(f"❌ Помилка при запуску планувальника: {e}")


def main():
    """Головна функція"""
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    print("🚀 Бот стартує!")
    print(f"📁 Завантаження подій з events.py...")
    print(f"📊 Кількість подій: {len(events)}")

    shuffle_fact_options(events)
    
    application = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()
    application.add_handler(CommandHandler("test", test_command))
    
    print("✅ Обробники команд завантажені")
    print("📡 Бот слухає повідомлення...\n")
    
    application.run_polling()


if __name__ == '__main__':
    main()
