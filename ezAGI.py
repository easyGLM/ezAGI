# ezAGI.py
# ezAGI (c) Gregory L. Magnusson MIT license 2024
# easy augmented generative intelligence UIUX — the ezAGI console
# main chat window is the production interaction from ezAGI: user queries and
# streamed answers only; internal SocraticReasoning is displayed in its own
# reasoning panel (premises, challenges, validation verdicts, conclusions)
# conversation from send_message is saved to ./memory/stm/{timestamp}memory.json
# internal conclusions are saved to ./memory/logs/thoughts.json

from pathlib import Path
import asyncio
import logging

from nicegui import ui, app  # handle UIUX
from fastapi.staticfiles import StaticFiles  # integrate fastapi static folder and gfx folder

from automind.openmind import OpenMind
from webmind.html_head import add_head_html  # handler for the html head imports and meta tags

logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).parent

# Serve static graphic files and easystyle.css from the 'gfx' directory
app.mount('/gfx', StaticFiles(directory=str(ROOT / 'gfx')), name='gfx')

openmind = OpenMind()  # initialize OpenMind instance

# log files as the code actually writes them
LOG_FILES = {
    "Premises Log": "./memory/logs/premises.json",
    "Not Premise Log": "./memory/logs/notpremise.json",
    "Truth Log": "./memory/logs/truth.json",
    "Thoughts Log": "./memory/logs/thoughts.json",
    "Conclusions Log": "./memory/logs/conclusions.txt",
    "Socratic Log": "./memory/logs/socraticlogs.txt",
    "Error Log": "./memory/logs/errorlogs.txt",
}

# per-log accent colour, surfaced through the --log-accent CSS custom property
LOG_COLORS = {
    "Premises Log": "#6c8cff",      # indigo
    "Not Premise Log": "#f0a04b",   # amber
    "Truth Log": "#3ecf8e",         # green
    "Thoughts Log": "#b57edc",      # violet
    "Conclusions Log": "#2dd4bf",   # teal
    "Socratic Log": "#4aa3df",      # blue
    "Error Log": "#ef5f6b",         # red
}

# one internal reasoning main_loop for the whole app, not one per page visit
app.on_startup(lambda: asyncio.create_task(openmind.main_loop()))


def _trace_row(container, event):
    """Render one reasoning-trace event into the trace container."""
    kind = event.get("type")
    stamp = event.get("time", "")
    with container:
        if kind == "premise":
            ui.label(f"{stamp}  premise: {event.get('premise', '')}").classes('trace-row trace-premise')
        elif kind == "generated_premise":
            ui.label(f"{stamp}  generated premise: {event.get('premise', '')}").classes('trace-row trace-generated')
        elif kind == "challenge":
            ui.label(f"{stamp}  challenged: {event.get('premise', '')}").classes('trace-row trace-challenge')
        elif kind == "conclusion_attempt":
            ui.separator()
            ui.label(f"{stamp}  conclusion attempt {event.get('attempt', '?')}").classes('trace-row trace-attempt')
        elif kind == "validation":
            verdict = "VALID" if event.get("valid") else "INVALID"
            badge_color = "green" if event.get("valid") else "orange"
            with ui.row().classes('trace-row items-center'):
                ui.label(f"{stamp}  validation ({event.get('method', '')})")
                ui.badge(f"{verdict} · {event.get('confidence', 0):.1f}", color=badge_color)
        elif kind == "conclusion":
            with ui.card().classes('trace-conclusion w-full'):
                ui.label(f"{stamp}  conclusion (confidence {event.get('confidence', 0):.1f})").classes('text-bold')
                ui.markdown(event.get("conclusion", ""))
        elif kind == "internal_conclusion":
            with ui.card().classes('trace-internal w-full'):
                ui.label(f"{stamp}  autonomous reasoning").classes('text-bold')
                ui.markdown(event.get("conclusion", ""))


@ui.page('/')
def main():
    # configure HTML head content from html_head.py external module in the webmind folder
    add_head_html(ui)

    dark_mode = ui.dark_mode()

    async def send() -> None:
        question = text.value  # get value from input field
        if not question or not question.strip():
            return
        text.value = ''  # clear input field for openmind
        await openmind.internal_queue.put(question)  # feed the autonomous reasoning loop
        await openmind.send_message(question)  # production answer, streamed

    # ---------------------------------------------------------------- header
    def refresh_providers():
        providers = openmind.available_providers()
        provider_select.set_options(providers)
        if providers and provider_select.value not in providers:
            provider_select.value = providers[0]

    def on_provider_change():
        provider = provider_select.value
        if not provider:
            return
        models = openmind.models_for(provider)
        model_select.set_options(models)
        model_select.value = models[0] if models else None

    def on_model_change():
        if provider_select.value and model_select.value:
            openmind.select_model(provider_select.value, model_select.value)

    with ui.header().classes('console-header items-center'):
        ui.label('ezAGI').classes('text-lg text-bold')
        provider_select = ui.select(options=[], label='provider',
                                    on_change=lambda _: on_provider_change()).classes('console-select')
        model_select = ui.select(options=[], label='model',
                                 on_change=lambda _: on_model_change()).classes('console-select console-model')
        ui.button(icon='refresh', on_click=refresh_providers).props('flat dense').tooltip('rescan providers')
        ui.space()
        state_chip = ui.badge('idle', color='grey')
        token_label = ui.html().classes('token-counter')
        ui.button(icon='tune', on_click=lambda: settings_drawer.toggle()).props('flat dense').tooltip('sampling controls')
        ui.button(icon='dark_mode', on_click=lambda: dark_mode.toggle()).props('flat dense').tooltip('toggle dark mode')

    def refresh_status():
        tokens = openmind.session_tokens
        live_out = openmind._live_out               # int estimate while streaming, else None
        streaming = live_out is not None
        # While streaming the provider hasn't reported input yet, so show the
        # live output estimate on its own and fold it into the session total so
        # the cumulative figure is never smaller than the turn in progress.
        last_in = 0 if streaming else tokens['last_in']
        last_out = live_out if streaming else tokens['last_out']
        session = tokens['total'] + (live_out or 0)
        out_prefix = '≈' if streaming else ''
        token_label.set_content(
            f'<span class="tok-pill tok-in" title="input tokens, last turn">'
            f'<span class="tok-k">in</span> {last_in:,}</span>'
            f'<span class="tok-pill tok-out{" tok-live" if streaming else ""}" title="output tokens, last turn">'
            f'<span class="tok-k">out</span> {out_prefix}{last_out:,}</span>'
            f'<span class="tok-pill tok-total" title="total tokens this session">'
            f'<span class="tok-k">session</span> {session:,}</span>')
        thinking = openmind.reasoning_state == 'thinking'
        state_chip.set_text('thinking' if thinking else 'idle')
        state_chip._props['color'] = 'primary' if thinking else 'grey'
        state_chip.update()
        active = openmind.current_provider
        if active and provider_select.value is None:
            refresh_providers()

    ui.timer(1.0, refresh_status)

    # ------------------------------------------------------- sampling drawer
    with ui.right_drawer(value=False).classes('console-drawer') as settings_drawer:
        ui.label('sampling controls').classes('text-bold')
        temp_enabled = ui.switch('set temperature', value=False)
        temp_slider = ui.slider(min=0.0, max=2.0, step=0.1, value=0.7).props('label-always')
        max_tokens_input = ui.number('max tokens (blank = provider default)', value=None, min=1, max=128000)

        def apply_sampling():
            temperature = float(temp_slider.value) if temp_enabled.value else None
            max_tokens = int(max_tokens_input.value) if max_tokens_input.value else None
            openmind.set_sampling(temperature=temperature, max_tokens=max_tokens)
            ui.notify(f'sampling: temperature={temperature}, max_tokens={max_tokens}')

        ui.button('apply', on_click=apply_sampling).classes('mt-2')

    # ------------------------------------------------------------------ tabs
    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('chat').classes('tab-style')
        reasoning_tab = ui.tab('reasoning').classes('tab-style')
        logs_tab = ui.tab('logs').classes('tab-style')
        api_tab = ui.tab('APIk').classes('tab-style')

    with ui.tab_panels(tabs, value=chat_tab).classes('response-style w-full'):
        # chat: the production interaction from ezAGI — queries and answers only
        message_container = ui.tab_panel(chat_tab).classes('items-stretch response-container')
        openmind.message_container = message_container

        # reasoning: the live internal SocraticReasoning trace
        with ui.tab_panel(reasoning_tab):
            ui.label('internal reasoning — SocraticReasoning trace').classes('text-bold')
            trace_container = ui.column().classes('w-full trace-container')

        # logs: reasoning artifacts on disk
        with ui.tab_panel(logs_tab):
            # log choices — compact pills, all on one horizontal row
            with ui.row().classes('w-full no-wrap gap-2 items-stretch'):
                for log_name, log_path in LOG_FILES.items():
                    accent = LOG_COLORS.get(log_name, '#4aa3df')
                    ui.button(log_name, on_click=lambda path=log_path: view_log(path)) \
                        .props('flat no-caps dense') \
                        .classes('logbuttons') \
                        .style(f'--log-accent: {accent}')

            # selected log file content
            log_container = ui.column().classes('w-full')
            # runtime push messages (compact, below the display)
            log = ui.log().classes('w-full h-16')
            openmind.log = log

            def view_log(file_path):
                log_content = openmind.read_log_file(file_path)
                log_container.clear()
                with log_container:
                    ui.markdown(f"```\n{log_content}\n```").classes('w-full')

        # API keys management
        with ui.tab_panel(api_tab):
            ui.label('Manage API Keys').classes('text-lg font-bold')
            ui.label('services: openai · groq · together · anthropic · ollama (Ollama Cloud key)').classes('text-caption')
            with ui.row().classes('items-center'):
                openmind.service_input = ui.input('service (e.g. "openai", "anthropic", "ollama")').classes('flex-1 input')
                openmind.key_input = ui.input('API Key', password=True).classes('flex-1 input')
            with ui.row().classes('items-center'):
                ui.button('Add API Key', on_click=openmind.add_api_key).classes('api-action')
                ui.button('List API Keys', on_click=openmind.list_api_keys).classes('api-action')
            keys_container = ui.column().classes('w-full')
            openmind.keys_container = keys_container

    # ---------------------------------------------------------------- footer
    with ui.footer().classes('footer'), ui.column().classes('footer w-full'):
        with ui.row().classes('w-full no-wrap items-center'):
            text = ui.input(placeholder='Enter text here').classes('input').on('keydown.enter', send)
        with ui.row().classes('footer-link items-center no-wrap gap-1'):
            ui.link('easyAGI', 'https://rage.pythai.net', new_tab=True)
            ui.label('— a PYTHAI project')

    # ------------------------------------------------- reasoning trace feed
    async def consume_trace():
        while True:
            event = await openmind.trace_queue.get()
            try:
                if trace_container.client.connected:
                    _trace_row(trace_container, event)
            except Exception as e:
                logging.debug(f"trace render error: {e}")

    # one consumer per page; replace any previous page's consumer
    previous = getattr(openmind, '_trace_consumer', None)
    if previous is not None:
        previous.cancel()
    openmind._trace_consumer = asyncio.create_task(consume_trace())

    refresh_providers()
    on_provider_change()


def run():
    """Start the ezAGI console (console script entry point)."""
    logging.info("starting ezAGI")
    ui.run(title='ezAGI', reload=False)


if __name__ in {'__main__', '__mp_main__'}:
    run()
