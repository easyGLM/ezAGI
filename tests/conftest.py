# conftest.py — ezAGI offline test fixtures (no API keys, no network)
import sys
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(autouse=True)
def tmp_workdir(tmp_path, monkeypatch):
    """Run every test from a temp cwd so ./memory writes never pollute the repo."""
    monkeypatch.chdir(tmp_path)
    yield tmp_path


class MockChatter:
    """
    Offline chatter: canned responses, VALID judgments, fake streaming + usage.
    Mirrors the BaseChatter interface used across the codebase.
    """
    provider = "mock"

    def __init__(self, response="the sky is blue therefore it is daytime"):
        self.response = response
        self.current_model = "mock-model"
        self.temperature = None
        self.max_tokens = None
        self.last_usage = None
        self.calls = []

    def set_model(self, model_name):
        self.current_model = model_name

    def get_current_model(self):
        return self.current_model

    def set_sampling(self, temperature=None, max_tokens=None):
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _answer(self, knowledge):
        if "Answer exactly VALID or INVALID" in knowledge:
            return "VALID"
        return self.response

    def generate_response(self, knowledge):
        self.calls.append(knowledge)
        answer = self._answer(knowledge)
        self.last_usage = {"input_tokens": len(knowledge) // 4, "output_tokens": len(answer) // 4}
        return answer

    async def generate_response_stream(self, knowledge):
        self.calls.append(knowledge)
        answer = self._answer(knowledge)
        for word in answer.split(" "):
            yield word + " "
        self.last_usage = {"input_tokens": len(knowledge) // 4, "output_tokens": len(answer) // 4}

    def generate_response_with_tokens(self, knowledge, on_token):
        answer = self.generate_response(knowledge)
        for word in answer.split(" "):
            on_token(word + " ")
        return answer


@pytest.fixture
def mock_chatter():
    return MockChatter()
