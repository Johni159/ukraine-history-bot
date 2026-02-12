import asyncio
from telegram import Poll
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = '8309839168:AAH7L9h6q20gD0OHUnV3G-CHbnqjtxsyZI8'
GROUP_ID = -5148918793

questions = [
    {
        'question': 'Коли була проголошена незалежність України?',
        'options': ['1991', '1989', '2001', '1945'],
        'correct_option_id': 0
    },
    {
        'question': 'Яке місто було першою столицею УНР?',
        'options': ['Київ', 'Харків', 'Львів', 'Житомир'],
        'correct_option_id': 0
    },
    # Додай ще питання тут!
]

async def send_polls(application):
    print("Відправляю опитування за розкладом!")  # Логування для перевірки
    for q in questions[:4]:
        await application.bot.send_poll(
            chat_id=GROUP_ID,
            question=q['question'],
            options=q['options'],
            type=Poll.QUIZ,
            correct_option_id=q['correct_option_id'],
            is_anonymous=False  # НЕ анонімне опитування
        )

async def test_command(update, context: ContextTypes.DEFAULT_TYPE):
    print("Отримано команду /test")
    for q in questions[:4]:
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=q['question'],
            options=q['options'],
            type=Poll.QUIZ,
            correct_option_id=q['correct_option_id'],
            is_anonymous=False  # НЕ анонімне опитування
        )

async def on_startup(application):
    scheduler = AsyncIOScheduler()
    # Час — 22:09 (9 хвилин 22-ї години)
    scheduler.add_job(send_polls, 'cron', hour=22, minute=32, args=[application])
    scheduler.start()
    print("Планувальник запущено, чекаємо 22:32...")

if __name__ == '__main__':  # Ось так правильно!
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    application = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()
    application.add_handler(CommandHandler("test", test_command))
    application.run_polling()
