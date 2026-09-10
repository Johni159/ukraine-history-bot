import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "csharp-training" / "Lesson01" / "ukraine_history_bot.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ukraine_history_bot", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_quiz_generation(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
    monkeypatch.setenv("CHANNEL_ID", "@test-channel")
    module = load_module()

    quiz = module.get_random_poll()

    assert quiz is not None
    assert quiz["question"]
    assert len(quiz["options"]) == 4
    assert len(set(quiz["options"])) == 4
    assert 0 <= quiz["correct_option_id"] < 4


def test_quiz_has_correct_option(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
    module = load_module()

    quiz = module.get_random_poll()

    assert quiz["options"][quiz["correct_option_id"]]
