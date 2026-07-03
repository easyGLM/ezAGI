# chatter.py (c) Gregory L. Magnusson MIT license 2024
# modular input response mechanisms for the multi-model environment
# providers: openai, groq, together, anthropic, ollama (local daemon) and ollama-cloud
# every chatter exposes:
#   generate_response(knowledge) -> str                     (sync, error-string on failure)
#   generate_response_stream(knowledge) -> async iterator   (yields text chunks, raises on failure)
#   set_model / get_current_model, temperature / max_tokens sampling attributes
#   last_usage -> {"input_tokens": n, "output_tokens": n} | None after a response

import asyncio
import concurrent.futures
import logging

import openai
from groq import AsyncGroq
from together import AsyncTogether

try:
    import anthropic
except ImportError:  # optional dependency: pip install "ezagi[anthropic]"
    anthropic = None

from webmind.ollama_handler import OllamaHandler, OLLAMA_CLOUD_MODELS

DEFAULT_MODELS = {
    "openai": "gpt-4.1",
    "groq": "llama-3.3-70b-versatile",
    "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "anthropic": "claude-opus-4-8",
    "ollama": "llama3",
    "ollama-cloud": OLLAMA_CLOUD_MODELS[0],
}

# curated alternates offered in the model selector
KNOWN_MODELS = {
    "openai": ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "o4-mini"],
    "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-120b"],
    "together": ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "deepseek-ai/DeepSeek-V3",
                 "Qwen/Qwen2.5-72B-Instruct-Turbo"],
    "anthropic": ["claude-opus-4-8", "claude-sonnet-5", "claude-haiku-4-5-20251001"],
    "ollama-cloud": OLLAMA_CLOUD_MODELS,
}


def _run_coro_sync(coro):
    """
    Run a coroutine to completion from synchronous code, even when the caller
    happens to live inside a running event loop (executor threads are safe).
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


class BaseChatter:
    """
    Shared model selection, sampling controls, usage accounting and the
    sync generate_response built on each provider's async stream.
    """
    provider = "base"

    def __init__(self):
        self.current_model = DEFAULT_MODELS.get(self.provider)
        self.temperature = None   # None = provider default
        self.max_tokens = None    # None = provider default
        self.last_usage = None

    def set_model(self, model_name):
        """Set the current model to the specified model_name."""
        self.current_model = model_name

    def get_current_model(self):
        """Get the name of the current model."""
        return self.current_model

    def set_sampling(self, temperature=None, max_tokens=None):
        """Update sampling controls; None leaves a control at provider default."""
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _sampling_kwargs(self):
        kwargs = {}
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens
        return kwargs

    async def generate_response_stream(self, knowledge):
        raise NotImplementedError
        yield  # pragma: no cover

    async def generate_response_async(self, knowledge):
        pieces = []
        async for chunk in self.generate_response_stream(knowledge):
            pieces.append(chunk)
        return "".join(pieces).strip()

    def generate_response(self, knowledge):
        try:
            return _run_coro_sync(self.generate_response_async(knowledge))
        except Exception as e:
            logging.error(f"{self.provider} api error: {e}")
            return f"error: unable to generate a response due to an issue with the {self.provider} api."

    def generate_response_with_tokens(self, knowledge, on_token):
        """
        Synchronous generation that forwards each streamed chunk to on_token
        (called from the calling thread) and returns the full response.
        """
        async def _collect():
            pieces = []
            async for chunk in self.generate_response_stream(knowledge):
                pieces.append(chunk)
                on_token(chunk)
            return "".join(pieces).strip()
        try:
            return _run_coro_sync(_collect())
        except Exception as e:
            logging.error(f"{self.provider} api error: {e}")
            return f"error: unable to generate a response due to an issue with the {self.provider} api."


class GPT4o(BaseChatter):
    """OpenAI chat models (class name kept for compatibility; alias OpenAIModel)."""
    provider = "openai"

    def __init__(self, openai_api_key):
        super().__init__()
        self.openai_api_key = openai_api_key
        self.client = openai.AsyncOpenAI(api_key=openai_api_key)

    async def generate_response_stream(self, knowledge):
        self.last_usage = None
        stream = await self.client.chat.completions.create(
            model=self.current_model,
            messages=[{"role": "user", "content": f"{knowledge}"}],
            stream=True,
            stream_options={"include_usage": True},
            **self._sampling_kwargs(),
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            if getattr(chunk, "usage", None):
                self.last_usage = {
                    "input_tokens": chunk.usage.prompt_tokens,
                    "output_tokens": chunk.usage.completion_tokens,
                }


OpenAIModel = GPT4o


class GroqModel(BaseChatter):
    """Groq-hosted models."""
    provider = "groq"

    def __init__(self, groq_api_key):
        super().__init__()
        self.client = AsyncGroq(api_key=groq_api_key)

    async def generate_response_stream(self, knowledge):
        self.last_usage = None
        stream = await self.client.chat.completions.create(
            model=self.current_model,
            messages=[{"role": "user", "content": f"{knowledge}"}],
            stream=True,
            **self._sampling_kwargs(),
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            x_groq = getattr(chunk, "x_groq", None)
            usage = getattr(x_groq, "usage", None) if x_groq else None
            if usage:
                self.last_usage = {
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                }


class TogetherModel(BaseChatter):
    """together.ai-hosted models."""
    provider = "together"

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.async_client = AsyncTogether(api_key=api_key)

    async def generate_response_stream(self, knowledge):
        self.last_usage = None
        stream = await self.async_client.chat.completions.create(
            model=self.current_model,
            messages=[{"role": "user", "content": f"{knowledge}"}],
            stream=True,
            **self._sampling_kwargs(),
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            usage = getattr(chunk, "usage", None)
            if usage:
                self.last_usage = {
                    "input_tokens": getattr(usage, "prompt_tokens", None),
                    "output_tokens": getattr(usage, "completion_tokens", None),
                }


class AnthropicModel(BaseChatter):
    """Anthropic Claude models (optional dependency: pip install "ezagi[anthropic]")."""
    provider = "anthropic"

    def __init__(self, api_key):
        if anthropic is None:
            raise ImportError(
                'the anthropic SDK is not installed — pip install "ezagi[anthropic]"')
        super().__init__()
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate_response_stream(self, knowledge):
        self.last_usage = None
        kwargs = {}
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        async with self.client.messages.stream(
            model=self.current_model,
            max_tokens=self.max_tokens or 2048,  # anthropic requires max_tokens
            messages=[{"role": "user", "content": f"{knowledge}"}],
            **kwargs,
        ) as stream:
            async for text in stream.text_stream:
                yield text
            final = await stream.get_final_message()
            self.last_usage = {
                "input_tokens": final.usage.input_tokens,
                "output_tokens": final.usage.output_tokens,
            }


class OllamaModel(BaseChatter):
    """
    Ollama models — the local daemon by default, Ollama Cloud when an api_key
    is provided (https://ollama.com, OLLAMA_API_KEY).
    """
    provider = "ollama"

    def __init__(self, api_key=None, host=None):
        self.handler = OllamaHandler(host=host, api_key=api_key)
        if self.handler.is_cloud:
            self.provider = "ollama-cloud"
        super().__init__()
        self.current_model = self.handler.default_model()

    async def generate_response_stream(self, knowledge):
        self.last_usage = None
        async for chunk in self.handler.generate_stream_async(
                knowledge, model=self.current_model,
                temperature=self.temperature, max_tokens=self.max_tokens):
            yield chunk
        self.last_usage = self.handler.last_usage

    def list_models(self):
        return self.handler.list_models()


def check_ollama_running(host=None):
    """True when an Ollama daemon answers at the given (or local) host."""
    return OllamaHandler(host=host).check_installation()


def check_ollama_installation():
    """Backward-compatible alias: is the local Ollama endpoint reachable."""
    return check_ollama_running()


# cloud-first provider resolution with the local Ollama daemon as failsafe
RESOLVE_ORDER = ["openai", "groq", "together", "anthropic", "ollama-cloud", "ollama"]


def resolve_chatter(api_manager, provider=None, model=None):
    """
    Construct a chatter from stored API keys. An explicit provider is honored;
    otherwise providers are tried cloud-first with local Ollama as failsafe.
    Returns None when nothing is available.
    """
    def build(name):
        try:
            if name == "openai":
                key = api_manager.get_api_key("openai")
                return GPT4o(key) if key else None
            if name == "groq":
                key = api_manager.get_api_key("groq")
                return GroqModel(key) if key else None
            if name == "together":
                key = api_manager.get_api_key("together")
                return TogetherModel(key) if key else None
            if name == "anthropic":
                key = api_manager.get_api_key("anthropic")
                return AnthropicModel(key) if key else None
            if name == "ollama-cloud":
                key = api_manager.get_api_key("ollama")
                return OllamaModel(api_key=key) if key else None
            if name == "ollama":
                return OllamaModel() if check_ollama_running() else None
        except Exception as e:
            logging.error(f"failed to initialize {name} chatter: {e}")
        return None

    if provider:
        chatter = build(provider)
        if chatter and model:
            chatter.set_model(model)
        return chatter

    for name in RESOLVE_ORDER:
        chatter = build(name)
        if chatter:
            logging.info(f"resolve_chatter selected provider: {chatter.provider}")
            if model:
                chatter.set_model(model)
            return chatter
    return None
