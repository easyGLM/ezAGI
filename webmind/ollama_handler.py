# ollama_handler.py
# dual-endpoint handler for Ollama: local daemon (http://localhost:11434) and
# Ollama Cloud (https://ollama.com with Authorization: Bearer $OLLAMA_API_KEY)
# ollama_handler (c) 2024 codephreak MIT licence

import logging
import subprocess
import asyncio
import aiohttp
import ujson as json

LOCAL_HOST = "http://localhost:11434"
CLOUD_HOST = "https://ollama.com"

# curated cloud models offered when /api/tags is unavailable on the cloud endpoint
OLLAMA_CLOUD_MODELS = ["gpt-oss:120b", "gpt-oss:20b", "deepseek-v3.1:671b", "qwen3-coder:480b"]


class OllamaHandler:
    """
    Interact with an Ollama endpoint: the local daemon by default, or
    Ollama Cloud when constructed with an api_key.
    """
    def __init__(self, host=None, api_key=None):
        self.api_key = api_key
        self.host = host or (CLOUD_HOST if api_key else LOCAL_HOST)
        self.api_url = f"{self.host}/api"
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.is_cloud = self.host.rstrip('/') == CLOUD_HOST
        self.models = []
        self.selected_model = None
        self.last_usage = None  # {"input_tokens": n, "output_tokens": n} after a response

    def check_installation(self):
        """
        Check that the endpoint is reachable (auth probe against /api/tags).
        """
        try:
            import httpx
            response = httpx.get(f"{self.api_url}/tags", headers=self.headers, timeout=5)
            if response.status_code == 200:
                logging.info(f"Ollama endpoint {self.host} is accessible.")
                return True
            logging.error(f"Ollama endpoint {self.host} returned {response.status_code}.")
            return False
        except Exception as e:
            logging.error(f"Failed to reach Ollama endpoint {self.host}: {e}")
            return False

    def list_models(self):
        """
        List available models from /api/tags (works for local and cloud).
        Falls back to the ollama CLI locally and to the curated cloud list.
        """
        try:
            import httpx
            response = httpx.get(f"{self.api_url}/tags", headers=self.headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                if not self.models and self.is_cloud:
                    self.models = list(OLLAMA_CLOUD_MODELS)
                return self.models
            logging.error(f"Ollama /api/tags error: {response.status_code}")
        except Exception as e:
            logging.error(f"Ollama /api/tags error: {e}")

        if self.is_cloud:
            self.models = list(OLLAMA_CLOUD_MODELS)
            return self.models

        # local CLI fallback
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().splitlines()[1:]  # skip header row
                self.models = [line.split()[0] for line in lines if line.split()]
                return self.models
            logging.error(f"ollama list error: {result.stderr}")
        except Exception as e:
            logging.error(f"ollama list error: {e}")
        return []

    def default_model(self):
        """
        First available model, else a sensible default per endpoint.
        """
        if self.selected_model:
            return self.selected_model
        models = self.models or self.list_models()
        if models:
            return models[0]
        return OLLAMA_CLOUD_MODELS[0] if self.is_cloud else "llama3"

    async def generate_stream_async(self, knowledge, model=None, temperature=None, max_tokens=None):
        """
        Stream chat chunks from /api/chat as an async generator of text pieces.
        Records token usage from the final chunk into self.last_usage.
        """
        model = model or self.default_model()
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": knowledge}],
            "stream": True,
        }
        options = {}
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        if options:
            payload["options"] = options

        self.last_usage = None
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_url}/chat", json=payload, headers=self.headers) as response:
                if response.status != 200:
                    body = await response.text()
                    raise RuntimeError(f"Ollama API error {response.status}: {body[:200]}")
                async for line in response.content:
                    if not line.strip():
                        continue
                    data = json.loads(line.decode('utf-8'))
                    if "error" in data:
                        raise RuntimeError(f"Ollama API error: {data['error']}")
                    content = data.get("message", {}).get("content")
                    if content:
                        yield content
                    if data.get("done"):
                        self.last_usage = {
                            "input_tokens": data.get("prompt_eval_count"),
                            "output_tokens": data.get("eval_count"),
                        }

    async def generate_response_async(self, knowledge, model=None, temperature=None, max_tokens=None):
        """
        Generate a complete response by joining the chat stream.
        """
        try:
            pieces = []
            async for chunk in self.generate_stream_async(knowledge, model=model,
                                                          temperature=temperature, max_tokens=max_tokens):
                pieces.append(chunk)
            return "".join(pieces)
        except Exception as e:
            logging.error(f"Ollama API error: {e}")
            return "Error: Unable to generate a response due to an issue with the Ollama API."

    async def show_ollama_info_async(self, container=None):
        """
        Show information about the local Ollama service.
        """
        if self.is_cloud:
            return f"Ollama Cloud endpoint: {self.host}"
        try:
            result = await asyncio.create_subprocess_exec(
                "ollama", "list",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await result.communicate()
            if result.returncode == 0:
                return stdout.decode().strip()
            logging.error(f"Ollama info error: {stderr.decode().strip()}")
            return ""
        except Exception as e:
            logging.error(f"Ollama info error: {e}")
            return ""

    def install_ollama(self, confirm=False):
        """
        Ollama is installed by the user from https://ollama.com/download
        This method no longer pipes curl to a shell with sudo; it prints the
        official command and only runs it when explicitly confirmed.
        """
        command = "curl -fsSL https://ollama.com/install.sh | sh"
        if not confirm:
            message = (
                "Ollama is not installed. Install it yourself with:\n"
                f"    {command}\n"
                "or download from https://ollama.com/download — then rerun ezAGI.\n"
                "(call install_ollama(confirm=True) to let ezAGI run the installer)"
            )
            logging.info(message)
            return message
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return "Ollama installation successful."
            logging.error(f"Ollama install error: {result.stderr}")
            return "Error: Unable to install Ollama."
        except Exception as e:
            logging.error(f"Ollama install error: {e}")
            return "Error: Unable to install Ollama."

    async def test_ollama(self):
        """
        Test the endpoint by generating a response to a default prompt.
        """
        return await self.generate_response_async(
            "explain easy Augmented Generative Intelligence LLM reasoning enhancement framework",
            self.selected_model)

    def select_model(self, model_name):
        """
        Select the model to use for generating responses.
        """
        self.selected_model = model_name
        logging.info(f"Selected model: {model_name}")
