import asyncio
import os
import random
import sys

from dotenv import load_dotenv
from telegram import Poll, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from events import events

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
POLL_INTERVAL_SECONDS = 300

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not configured")
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID is not configured")

poll_queue = []


def get_random_poll():
    """Build a randomized Telegram quiz from the event database."""
    global poll_queue

    if not events:
        return None

    if not poll_queue:
        poll_queue = events.copy()
        random.shuffle(poll_queue)

    event = poll_queue.pop()

    if "event" in event and "year" in event:
        correct_year = event["year"]
        years = list({e["year"] for e in events if "year" in e and e["year"] != correct_year})
        wrong_years = random.sample(years, 3) if len(years) >= 3 else [correct_year + 1, correct_year - 1, correct_year + 5]
        options = [correct_year, *wrong_years]
        random.shuffle(options)
        return {
            "question": f"У якому році відбулася подія: {event['event']}?",
            "options": [str(option) for option in options],
            "correct_option_id": options.index(correct_year),
        }

    if all(key in event for key in ("question", "options", "correct_option_id")):
        options = event["options"].copy()
        correct_answer = options[event["correct_option_id"]]
        random.shuffle(options)
        return {
            "question": event["question"],
            "options": options,
            "correct_option_id": options.index(correct_answer),
        }

    return None


async def send_quiz(context: ContextTypes.DEFAULT_TYPE, chat_id, anonymous=True):
    quiz = get_random_poll()
    if not quiz:
        return False

    await context.bot.send_poll(
        chat_id=chat_id,
        question=quiz["question"],
        options=quiz["options"],
        type=Poll.QUIZ,
        correct_option_id=quiz["correct_option_id"],
        is_anonymous=anonymous,
    )
    return True


async def send_poll_job(context: ContextTypes.DEFAULT_TYPE):
    """Publish a quiz automatically on the configured channel."""
    try:
        if await send_quiz(context, CHANNEL_ID):
            print("Quiz published automatically")
        else:
            print("Quiz database is empty or invalid")
    except Exception as exc:
        print(f"Automatic publishing error: {exc}")


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send one quiz to the chat when /test is used."""
    try:
        if not await send_quiz(context, update.effective_chat.id, anonymous=False):
            await update.message.reply_text("⚠️ База подій порожня!")
    except Exception as exc:
        await update.message.reply_text(f"❌ Помилка: {exc}")


def main():
    """Create the bot, scheduler and command handlers."""
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print(f"Loaded events: {len(events)}")
    application = ApplicationBuilder().token(TOKEN).build()
    application.job_queue.run_repeating(
        send_poll_job,
        interval=POLL_INTERVAL_SECONDS,
        first=10,
    )
    application.add_handler(CommandHandler("test", test_command))
    application.run_polling()


if __name__ == "__main__":
    main()
