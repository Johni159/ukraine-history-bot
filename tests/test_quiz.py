import importlib.util
import sys
from pathlib import Path

import pytest


MODULE_DIR = Path(__file__).parents[1]
MODULE_PATH = MODULE_DIR / "ukraine_history_bot.py"


def load_module(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
    monkeypatch.setenv("CHANNEL_ID", "@test-channel")

    sys.path.insert(0, str(MODULE_DIR))
    try:
        spec = importlib.util.spec_from_file_location("ukraine_history_bot", MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def test_quiz_generation(monkeypatch):
    module = load_module(monkeypatch)
    quiz = module.get_random_poll()

    assert quiz is not None
    assert quiz["question"]
    assert len(quiz["options"]) == 4
    assert len(set(quiz["options"])) == 4
    assert 0 <= quiz["correct_option_id"] < 4


def test_quiz_has_correct_option(monkeypatch):
    module = load_module(monkeypatch)
    quiz = module.get_random_poll()

    assert quiz["options"][quiz["correct_option_id"]]


def test_all_questions_have_valid_structure(monkeypatch):
    module = load_module(monkeypatch)

    assert module.events

    for index, event in enumerate(module.events):
        assert event.get("question"), f"Question {index} has no text"
        options = event.get("options")
        assert isinstance(options, list), f"Question {index} options are not a list"
        assert len(options) == 4, f"Question {index} must have 4 options"
        assert len(set(options)) == 4, f"Question {index} has duplicate options"

        correct_option_id = event.get("correct_option_id")
        assert isinstance(correct_option_id, int)
        assert 0 <= correct_option_id < len(options)
        assert options[correct_option_id]


def test_randomized_quizzes_keep_correct_answer(monkeypatch):
    module = load_module(monkeypatch)

    module.poll_queue = []
    generated = []

    for _ in range(len(module.events)):
        quiz = module.get_random_poll()
        assert quiz is not None
        generated.append(quiz)
        assert len(quiz["options"]) == 4
        assert quiz["options"][quiz["correct_option_id"]]

    assert len(generated) == len(module.events)


def test_invalid_event_returns_none(monkeypatch):
    module = load_module(monkeypatch)
    module.events = [{"question": "Broken", "options": ["A"]}]
    module.poll_queue = []

    assert module.get_random_poll() is None
