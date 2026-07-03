# openmind.py
# openmind (c) 2024 Gregory L. Magnusson MIT licence
# internal reasoning loop for continuous AGI reasoning without user interaction
# openmind internal reasoning asynchronous task ensuring non-blocking execution and efficient concurrency
# modular integration of automind reasoning with memory
# webmind for API and model handling of input response from various LLM
# providers: openai, groq, together, anthropic, ollama (local) and ollama-cloud
# all logs are memories:
#   internal reasoning conclusion      ./memory/logs/thoughts.json
#   not premise                        ./memory/logs/notpremise.json
#   short term memory input response   ./memory/stm/{timestamp}memory.json

import os
import time
from datetime import datetime
from nicegui import ui  # importing ui for easyAGI
from memory.memory import (create_memory_folders, store_in_stm, save_conversation_memory,
                           save_internal_reasoning, DialogEntry, save_valid_truth, append_json_log)
from webmind.ollama_handler import OllamaHandler, OLLAMA_CLOUD_MODELS
from automind.automind import FundamentalAGI
from webmind.chatter import (GPT4o, GroqModel, TogetherModel, AnthropicModel, OllamaModel,
                             resolve_chatter, check_ollama_running, DEFAULT_MODELS, KNOWN_MODELS)
from webmind.api import APIManager
import ujson as json
import asyncio
import logging
import httpx

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# sentinel pushed into the token queue when a conclusion attempt restarts
STREAM_RESET = object()


class OpenMind:
    def __init__(self):
        self.api_manager = APIManager()
        self.agi_instance = None
        self.initialize_memory()
        self.message_container = ui.column()
        self.ollama_handler = OllamaHandler()  # local endpoint handler
        self.internal_queue = asyncio.Queue()
        self.prompt = ""  # Initialize an empty prompt field
        self.keys_container = ui.column()  # initialize keys_container
        self.log = None  # placeholder for log
        self.initialization_warning_shown = False

        # console state: provider/model, sampling, token accounting, reasoning trace
        self.current_provider = None
        self.current_model = None
        self.temperature = None
        self.max_tokens = None
        self.session_tokens = {"last_in": 0, "last_out": 0, "total": 0}
        self.trace_queue = asyncio.Queue()   # reasoning-trace events for the UI panel
        self.reasoning_state = "idle"        # idle | thinking

        # autonomous-loop stuck guard
        self._last_reasoned_prompt = None
        self._same_prompt_count = 0

    def initialize_memory(self):
        create_memory_folders()

    # ------------------------------------------------------------------ keys

    def use_api_key(self, service, key):
        self.api_manager.api_keys[service] = key
        self.initialize_agi()
        if self.message_container.client.connected:
            with self.message_container:
                ui.notify(f'Using API key for {service}', type='positive')
        logging.info(f'Using API key for {service}')

    def add_api_key(self):
        service = self.service_input.value.strip().lower()
        api_key = self.key_input.value.strip()
        logging.debug(f"Adding API key for {service}: {api_key[:4]}...{api_key[-4:]}")
        if service and api_key:
            self.api_manager.api_keys[service] = api_key
            self.api_manager.save_api_key(service, api_key)
            self.initialize_agi()
            if self.message_container.client.connected:
                ui.notify(f'API key for {service} added and loaded successfully')
            self.service_input.value = ''
            self.key_input.value = ''
            ui.run_javascript('setTimeout(() => { window.location.href = "/"; }, 1000);')
        else:
            ui.notify('Provide both service name and API key')

    def delete_api_key(self, service):
        logging.debug(f"Deleting API key for {service}")
        if service in self.api_manager.api_keys:
            del self.api_manager.api_keys[service]
            self.api_manager.remove_api_key(service)
            self.initialize_agi()
            if self.message_container.client.connected:
                ui.notify(f'API key for {service} removed successfully')
            self.list_api_keys()  # Refresh the list after deletion
        else:
            ui.notify(f'No API key found for {service}')

    def list_api_keys(self):
        if self.api_manager.api_keys:
            keys_list = [(service, key) for service, key in self.api_manager.api_keys.items()]
            logging.debug(f"Stored API keys: {[s for s, _ in keys_list]}")
            if self.keys_container.client.connected:
                self.keys_container.clear()
                for service, key in keys_list:
                    with self.keys_container:
                        ui.label(f"{service}: {key[:4]}...{key[-4:]}").classes('flex-1')
                        ui.button('Delete', on_click=lambda s=service: self.delete_api_key(s)).classes('ml-4')
        else:
            if self.keys_container.client.connected:
                ui.notify('No API keys in storage')
                self.keys_container.clear()
                with self.keys_container:
                    ui.label('No API keys in storage')

    # -------------------------------------------------------- model selection

    def available_providers(self):
        """
        Providers usable right now: those with stored keys, ollama-cloud when
        an ollama key is stored, and the local daemon when it responds.
        """
        providers = []
        for service in ("openai", "groq", "together", "anthropic"):
            if self.api_manager.get_api_key(service):
                providers.append(service)
        if self.api_manager.get_api_key("ollama"):
            providers.append("ollama-cloud")
        if check_ollama_running():
            providers.append("ollama")
        return providers

    def models_for(self, provider):
        """Model choices for the selector: curated lists, live list for local ollama."""
        if provider == "ollama":
            return OllamaHandler().list_models() or [DEFAULT_MODELS["ollama"]]
        if provider == "ollama-cloud":
            return list(OLLAMA_CLOUD_MODELS)
        return list(KNOWN_MODELS.get(provider, [DEFAULT_MODELS.get(provider)]))

    def select_model(self, provider, model=None):
        """
        Select a provider (and optionally a model) for the AGI instance.
        """
        def notify_user(message, message_type='info'):
            if self.message_container.client.connected:
                with self.message_container:
                    ui.notify(message, type=message_type)

        key_service = "ollama" if provider == "ollama-cloud" else provider
        if provider not in ("ollama",) and not self.api_manager.get_api_key(key_service):
            notify_user(f'{provider} API key not found. Please add the key first.', 'negative')
            logging.warning(f'{provider} API key not found')
            return

        chatter = resolve_chatter(self.api_manager, provider=provider, model=model)
        if chatter is None:
            notify_user(f'Failed to initialize AGI with {provider}', 'negative')
            logging.warning(f'Failed to initialize AGI with {provider}')
            return

        self._apply_sampling(chatter)
        self.agi_instance = FundamentalAGI(chatter)
        self.current_provider = chatter.provider
        self.current_model = chatter.get_current_model()
        notify_user(f'Using {chatter.provider} ({self.current_model}) for AGI')
        logging.info(f'AGI initialized with {chatter.provider} ({self.current_model})')

    def set_sampling(self, temperature=None, max_tokens=None):
        """Wire the console sampling controls into the active chatter."""
        self.temperature = temperature
        self.max_tokens = max_tokens
        if self.agi_instance is not None:
            self._apply_sampling(self.agi_instance.agi.chatter)

    def _apply_sampling(self, chatter):
        if hasattr(chatter, 'set_sampling'):
            chatter.set_sampling(temperature=self.temperature, max_tokens=self.max_tokens)

    def initialize_agi(self):
        """
        Resolve a chatter cloud-first with the local Ollama daemon as failsafe.
        """
        chatter = resolve_chatter(self.api_manager)
        if chatter is not None:
            self._apply_sampling(chatter)
            self.agi_instance = FundamentalAGI(chatter)
            self.current_provider = chatter.provider
            self.current_model = chatter.get_current_model()
            self.initialization_warning_shown = False
            if self.message_container.client.connected:
                with self.message_container:
                    ui.notify(f'Using {chatter.provider} ({self.current_model}) for ezAGI')
            logging.debug(f"AGI initialized with {chatter.provider} ({self.current_model})")
        else:
            self.agi_instance = None
            self.current_provider = None
            self.current_model = None
            if not self.initialization_warning_shown:
                if self.message_container.client.connected:
                    with self.message_container:
                        ui.notify('No valid API key or Ollama instance found. Please add an API key or start Ollama')
                logging.debug("No valid API key or Ollama instance found. AGI not initialized")
                self.initialization_warning_shown = True

    def check_llama_running(self):
        return check_ollama_running()

    # ------------------------------------------------------------- reasoning

    async def get_conclusion_from_agi(self, prompt):
        """
        Get a conclusion from the AGI based on the provided prompt
        This method is asynchronous to allow non-blocking operations
        """
        if self.agi_instance is None:
            return "AGI not initialized. Please add an API key or start Ollama"
        conclusion = await asyncio.get_event_loop().run_in_executor(
            None, self.agi_instance.get_conclusion_from_agi, prompt)
        return conclusion

    def communicate_response(self, conclusion):
        """
        Log and print the conclusion from the AGI.
        """
        self.display_internal_conclusion(conclusion)
        return conclusion

    def _account_usage(self, response_text=""):
        """Update session token counters from the active chatter's last_usage."""
        usage = None
        if self.agi_instance is not None:
            usage = getattr(self.agi_instance.agi.chatter, 'last_usage', None)
        if not usage or usage.get("output_tokens") is None:
            usage = {"input_tokens": 0, "output_tokens": max(1, len(response_text) // 4)}
        self.session_tokens["last_in"] = usage.get("input_tokens") or 0
        self.session_tokens["last_out"] = usage.get("output_tokens") or 0
        self.session_tokens["total"] += (usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0)

    def _trace(self, event_type, payload):
        """Queue a reasoning-trace event for the UI panel (thread-safe)."""
        entry = {"type": event_type, "time": datetime.now().strftime('%H:%M:%S'), **payload}
        try:
            loop = getattr(self, '_ui_loop', None)
            if loop is not None and loop.is_running():
                loop.call_soon_threadsafe(self.trace_queue.put_nowait, entry)
            else:
                self.trace_queue.put_nowait(entry)
        except Exception as e:
            logging.debug(f"trace queue error: {e}")

    async def reasoning_loop(self):
        """
        Internal reasoning loop for continuous AGI reasoning without user interaction.
        Conclusions are shown in the reasoning panel and saved to ./memory/logs/thoughts.json
        (not premise results go to ./memory/logs/notpremise.json).
        Idles when there is no prompt and stops re-reasoning an unchanged prompt
        after three autonomous passes.
        """
        while True:
            if self.agi_instance is None:
                self.initialize_agi()
                if self.agi_instance is None:
                    if not self.initialization_warning_shown:
                        logging.debug("Waiting for API key or Ollama instance...")
                        self.initialization_warning_shown = True
                    await asyncio.sleep(30)  # Wait before checking again
                    continue

            prompt = self.prompt
            if not prompt.strip():
                await asyncio.sleep(10)  # nothing to reason about yet
                continue
            if prompt == self._last_reasoned_prompt and self._same_prompt_count >= 3:
                await asyncio.sleep(10)  # already reasoned this prompt to rest
                continue
            if prompt == self._last_reasoned_prompt:
                self._same_prompt_count += 1
            else:
                self._last_reasoned_prompt = prompt
                self._same_prompt_count = 1

            self.reasoning_state = "thinking"
            conclusion = await self.get_conclusion_from_agi(prompt)
            self.reasoning_state = "idle"
            self.display_internal_conclusion(conclusion)
            self._account_usage(conclusion)
            save_internal_reasoning({"timestamp": int(time.time()), "prompt": prompt, "conclusion": conclusion})

            await asyncio.sleep(10)  # Adjust the delay as necessary

    def display_internal_conclusion(self, conclusion):
        """
        Route an internal reasoning conclusion to the trace panel and the
        thoughts/notpremise memory logs (all logs are memories).
        """
        if conclusion != "No premises available for logic as conclusion":
            self._trace("internal_conclusion", {"conclusion": conclusion})
            logging.info(f"Internal reasoning conclusion: {conclusion}")

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "conclusion": conclusion
        }
        if conclusion == "No premises available for logic as conclusion.":
            append_json_log("./memory/logs/notpremise.json", log_entry)
        else:
            append_json_log("./memory/logs/thoughts.json", log_entry)

        # Also log the conclusions to conclusions.txt
        with open('./memory/logs/conclusions.txt', 'a') as file:
            file.write(f"{datetime.now().isoformat()}: {conclusion}\n")

    async def main_loop(self):
        """
        Main loop to handle both internal reasoning and user input.
        """
        self._ui_loop = asyncio.get_running_loop()
        reasoning_task = asyncio.create_task(self.reasoning_loop())
        reasoning_task.add_done_callback(self._handle_task_result)

        while True:
            prompt = await self.internal_queue.get()
            if prompt == 'exit':
                break
            self.prompt = prompt  # Update the prompt with the new input
            self._last_reasoned_prompt = None  # new input resets the autonomous guard
            self._same_prompt_count = 0

    async def send_message(self, question):
        """
        Production interaction: stream the reasoned answer into the main chat
        window while SocraticReasoning trace events flow to the reasoning panel.
        """
        if not self.message_container.client.connected:
            return
        with self.message_container:
            ui.chat_message(text=question, name='query', sent=True)
            response_message = ui.chat_message(name='ezAGI', sent=False)
            spinner = ui.spinner(type='dots')

        if self.agi_instance is None:
            self.initialize_agi()
        if self.agi_instance is None:
            with self.message_container:
                response_message.clear()
                with response_message:
                    ui.html("AGI not initialized. Please add an API key or start Ollama")
                self.message_container.remove(spinner)
            return

        loop = asyncio.get_running_loop()
        self._ui_loop = loop
        token_queue = asyncio.Queue()
        reasoning = self.agi_instance.agi.reasoning

        def on_token(chunk):
            loop.call_soon_threadsafe(token_queue.put_nowait, chunk)

        def on_event(event_type, payload):
            if event_type == "conclusion_attempt" and payload.get("attempt", 1) > 1:
                loop.call_soon_threadsafe(token_queue.put_nowait, STREAM_RESET)
            self._trace(event_type, payload)

        reasoning.on_token = on_token
        reasoning.on_event = on_event
        self.reasoning_state = "thinking"

        try:
            conclusion_future = loop.run_in_executor(
                None, self.agi_instance.get_conclusion_from_agi, question)

            streamed = ""
            last_render = 0.0
            while True:
                done = conclusion_future.done() and token_queue.empty()
                if done:
                    break
                try:
                    item = await asyncio.wait_for(token_queue.get(), timeout=0.25)
                except asyncio.TimeoutError:
                    continue
                if item is STREAM_RESET:
                    streamed = ""
                else:
                    streamed += item
                now = time.monotonic()
                if now - last_render > 0.1 and self.message_container.client.connected:
                    last_render = now
                    response_message.clear()
                    with response_message:
                        ui.html(streamed)

            conclusion = await conclusion_future

            if self.message_container.client.connected:
                response_message.clear()
                with response_message:
                    ui.html(conclusion)

            self._account_usage(conclusion)

            await self.run_javascript_with_retry(
                'window.scrollTo(0, document.body.scrollHeight)', retries=3, timeout=30.1)

            # Store the dialog entry
            entry = DialogEntry(question, conclusion)
            store_in_stm(entry)
            # saves conversation following each input response to ./memory/stm/timestampmemory.json
            save_conversation_memory({"dialog": {"instruction": question, "response": conclusion}})
        except Exception as e:
            logging.error(f"Error getting conclusion from easyAGI: {e}")
            if self.log:
                self.log.push(f"Error getting conclusion from easyAGI: {e}")
        finally:
            reasoning.on_token = None
            reasoning.on_event = None
            self.reasoning_state = "idle"
            try:
                if self.message_container.client.connected:
                    self.message_container.remove(spinner)  # Correctly remove the spinner
            except (KeyError, ValueError):
                logging.warning("Spinner element not found in message_container")

    async def run_javascript_with_retry(self, script, retries=5, timeout=12.0):
        for attempt in range(retries):
            task = asyncio.create_task(ui.run_javascript(script, timeout=timeout))
            task.add_done_callback(self._handle_task_result)
            try:
                await task
                return
            except TimeoutError:
                logging.warning(f"JavaScript did not respond within {timeout} s on attempt {attempt + 1}")
        raise TimeoutError(f"JavaScript did not respond after {retries} attempts")

    def _handle_task_result(self, task: asyncio.Task) -> None:
        try:
            task.result()
        except asyncio.CancelledError:
            pass  # Task cancellation should not be logged as an error.
        except Exception as e:
            logging.exception('Exception raised by task = %r', task)

    def read_log_file(self, file_path):
        """
        Read the content of a log file and return it.
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"Log file not found: {file_path}")
            return f"Log file not found: {file_path}"
        except Exception as e:
            logging.error(f"Error reading log file {file_path}: {e}")
            return f"Error reading log file {file_path}: {e}"
