# Ukraine History Quiz Bot 🇺🇦

A Telegram quiz bot that publishes interactive quizzes about Ukrainian history, culture, geography, science, sport and modern Ukraine.

## Features

- Interactive Telegram quiz polls with one correct answer.
- Randomized questions and answer options.
- Automatic scheduled publishing via `python-telegram-bot` JobQueue.
- `/test` command for manually sending a quiz.
- Environment-based configuration for the Telegram token and channel ID.
- Automated tests with pytest and GitHub Actions CI.
- Question-bank validation to prevent malformed quizzes.

## Tech Stack

- Python 3.11+
- python-telegram-bot
- asyncio
- python-dotenv
- pytest
- GitHub Actions

## Project Structure

```text
.
├── events.py
├── ukraine_history_bot.py
├── tests/
│   └── test_quiz.py
├── .github/workflows/tests.yml
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

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

Copy `.env.example` to `.env` and set your Telegram bot token and channel ID.

```env
TELEGRAM_TOKEN=your_bot_token
CHANNEL_ID=@your_channel
```

Never commit `.env` or real bot credentials.

### 5. Run the bot

```bash
python ukraine_history_bot.py
```

The bot publishes a quiz every 5 minutes and supports the `/test` command.

## Testing

Run locally:

```bash
pytest
```

GitHub Actions runs the test suite automatically on pushes and pull requests.

## Portfolio Highlights

This project demonstrates:

- asynchronous Python programming;
- Telegram Bot API integration;
- scheduled background jobs;
- environment configuration and secret handling;
- randomized quiz generation;
- automated testing and CI;
- clean repository structure and documentation.

## Future Improvements

- Add difficulty levels and richer question categories.
- Add user statistics and leaderboards.
- Add configurable publishing intervals.
- Add database-backed question and user storage.
- Add deployment documentation.

## License

This project is available for educational and portfolio purposes.
