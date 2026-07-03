# provider classes construct offline; resolve_chatter fallback order
import asyncio

import pytest

from webmind import chatter as chatter_mod
from webmind.chatter import (GPT4o, OpenAIModel, GroqModel, TogetherModel, OllamaModel,
                             DEFAULT_MODELS, resolve_chatter, _run_coro_sync)
from webmind.ollama_handler import OllamaHandler, CLOUD_HOST, LOCAL_HOST


class FakeAPIManager:
    def __init__(self, keys=None):
        self.api_keys = keys or {}

    def get_api_key(self, service):
        return self.api_keys.get(service)


def test_openai_class_constructs_offline():
    model = GPT4o("sk-fake")
    assert model.get_current_model() == DEFAULT_MODELS["openai"]
    model.set_model("gpt-4.1-mini")
    assert model.get_current_model() == "gpt-4.1-mini"
    assert OpenAIModel is GPT4o


def test_sampling_controls():
    model = GroqModel("gsk-fake")
    model.set_sampling(temperature=0.3, max_tokens=256)
    kwargs = model._sampling_kwargs()
    assert kwargs == {"temperature": 0.3, "max_tokens": 256}
    model.set_sampling()
    assert model._sampling_kwargs() == {}


def test_together_constructs_offline():
    model = TogetherModel("fake")
    assert model.get_current_model() == DEFAULT_MODELS["together"]


def test_anthropic_optional_dependency():
    if chatter_mod.anthropic is None:
        with pytest.raises(ImportError):
            chatter_mod.AnthropicModel("fake")
    else:
        model = chatter_mod.AnthropicModel("fake")
        assert model.get_current_model() == DEFAULT_MODELS["anthropic"]


def test_ollama_handler_local_vs_cloud():
    local = OllamaHandler()
    assert local.host == LOCAL_HOST
    assert local.headers == {}
    assert local.is_cloud is False

    cloud = OllamaHandler(api_key="ok-fake")
    assert cloud.host == CLOUD_HOST
    assert cloud.headers == {"Authorization": "Bearer ok-fake"}
    assert cloud.is_cloud is True
    assert cloud.api_url == f"{CLOUD_HOST}/api"


def test_ollama_model_cloud_provider(monkeypatch):
    monkeypatch.setattr(OllamaHandler, "list_models", lambda self: [])
    cloud = OllamaModel(api_key="ok-fake")
    assert cloud.provider == "ollama-cloud"
    assert cloud.get_current_model() == DEFAULT_MODELS["ollama-cloud"]


def test_resolve_chatter_prefers_cloud_keys(monkeypatch):
    monkeypatch.setattr(chatter_mod, "check_ollama_running", lambda host=None: False)
    manager = FakeAPIManager({"groq": "gsk-fake", "together": "t-fake"})
    resolved = resolve_chatter(manager)
    assert isinstance(resolved, GroqModel)  # groq before together in RESOLVE_ORDER


def test_resolve_chatter_ollama_cloud_key(monkeypatch):
    monkeypatch.setattr(chatter_mod, "check_ollama_running", lambda host=None: False)
    monkeypatch.setattr(OllamaHandler, "list_models", lambda self: [])
    manager = FakeAPIManager({"ollama": "ok-fake"})
    resolved = resolve_chatter(manager)
    assert isinstance(resolved, OllamaModel)
    assert resolved.provider == "ollama-cloud"


def test_resolve_chatter_local_failsafe(monkeypatch):
    monkeypatch.setattr(chatter_mod, "check_ollama_running", lambda host=None: True)
    monkeypatch.setattr(OllamaHandler, "list_models", lambda self: ["llama3"])
    resolved = resolve_chatter(FakeAPIManager())
    assert isinstance(resolved, OllamaModel)
    assert resolved.provider == "ollama"


def test_resolve_chatter_none_when_nothing_available(monkeypatch):
    monkeypatch.setattr(chatter_mod, "check_ollama_running", lambda host=None: False)
    assert resolve_chatter(FakeAPIManager()) is None


def test_resolve_explicit_provider_with_model(monkeypatch):
    manager = FakeAPIManager({"openai": "sk-fake"})
    resolved = resolve_chatter(manager, provider="openai", model="gpt-4o")
    assert isinstance(resolved, GPT4o)
    assert resolved.get_current_model() == "gpt-4o"


def test_run_coro_sync_inside_running_loop():
    async def inner():
        return 42

    async def outer():
        return _run_coro_sync(inner())

    assert asyncio.run(outer()) == 42
