# Ukraine History Quiz Bot 🇺🇦

A Telegram quiz bot that publishes interactive quizzes about Ukrainian history, notable Ukrainians and geography.

## Features

- Interactive Telegram quiz polls with one correct answer.
- Randomized questions and answer options.
- Automatically generates three incorrect years for event-based questions.
- Scheduled quiz publishing using `python-telegram-bot` JobQueue.
- `/test` command for manually sending a quiz.
- Environment-based configuration for the Telegram bot token and channel ID.
- Graceful handling of missing data and runtime errors.

## Tech Stack

- Python 3.11+
- python-telegram-bot
- asyncio
- python-dotenv
- GitHub Actions / pytest

## Project Structure

```text
.
├── csharp-training/
│   └── Lesson01/
│       ├── events.py
│       └── ukraine_history_bot.py
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

> The legacy `csharp-training/Lesson01` path is kept for now so the existing history/data remains intact. The bot code can be moved to a cleaner `src/` layout in a future refactor.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Johni159/ukraine-history-bot.git
cd ukraine-history-bot
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your Telegram bot token and channel ID.

```env
TELEGRAM_TOKEN=your_bot_token
CHANNEL_ID=@your_channel
```

Never commit `.env` or real bot credentials.

### 5. Run the bot

```bash
python csharp-training/Lesson01/ukraine_history_bot.py
```

The bot schedules a quiz every 5 minutes and supports the `/test` command.

## Testing

Run:

```bash
pytest
```

## Future Improvements

- Move application code and data into a clean `src/` structure.
- Add richer question categories and difficulty levels.
- Add persistent user statistics and leaderboards.
- Add configurable publishing intervals instead of a hard-coded schedule.
- Add more unit and integration tests.
- Add deployment documentation for a cloud host.

## License

This project is available for educational and portfolio purposes.
