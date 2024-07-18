# ezAGI.py
# ezAGI (c) Gregory L. Magnusson MIT license 2024
# conversation from main_loop(self) is saved to ./memory/stm/timestampmemeory.json from memory.py creating short term memory store of input response
# reasoning_loop(self)conversation from internal_conclusions are saved in ./memory/logs/thoughts.json
# easy augmented generative intelligence UIUX

from nicegui import ui, app  # handle UIUX
from fastapi.staticfiles import StaticFiles  # integrate fastapi static folder and gfx folder
from automind.openmind import OpenMind  # Importing OpenMind class from openmind.py
import concurrent.futures
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Serve static graphic files and easystyle.css from the 'gfx' directory
app.mount('/gfx', StaticFiles(directory='gfx'), name='gfx')

# Serve the CSS file
# app.mount('/static', StaticFiles(directory='static'), name='static')

openmind = OpenMind()

@ui.page('/')
def main():
    global executor, message_container, log, keys_container
    executor = concurrent.futures.ThreadPoolExecutor()

    async def send() -> None:
        question = text.value
        text.value = ''                              # openprompt for openmind
        await openmind.send_message(question)
        await openmind.internal_queue.put(question)  # add openmind to the internal queue for processing

    # ui.add_head_html
    ui.add_head_html('<link rel="stylesheet" href="/gfx/easystyle.css">')
    ui.add_head_html('<title>EasyAGI Augmented Generative Intelligence</title>')
    ui.add_head_html('''<meta name="description" content="easyAGI augmented generative intelligence for LLM">''')
    ui.add_head_html('''<meta name="keywords" content="EasyAGI Augmented Generative Intelligence">''')
    ui.add_head_html('''<meta name="author" content="Gregory L. Magnusson">''')
    ui.add_head_html('''<meta name="license" content="MIT">''')
    ui.add_head_html('<link rel="icon" type="image/x-icon" href="/gfx/fav/favicon.ico">')
    ui.add_head_html('''<meta name="viewport" content="width=device-width, initial-scale=1.0">''')
    ui.add_head_html('<link rel="apple-touch-icon" sizes="180x180" href="/gfx/fav/apple-touch-icon.png">')
    ui.add_head_html('<link rel="icon" type="image/png" sizes="32x32" href="/gfx/fav/favicon-32x32.png">')
    ui.add_head_html('<link rel="icon" type="image/png" sizes="16x16" href="/gfx/fav/favicon-16x16.png">')
    ui.add_head_html('<link rel="manifest" href="/site.webmanifest">')

    # Initialize dark mode toggle
    dark_mode = ui.dark_mode()

    async def toggle_dark_mode():
        dark_mode.value = not dark_mode.value
        dark_mode_toggle.text = 'Light Mode' if dark_mode.value else 'Dark Mode'

    with ui.row().classes('justify-end w-full p-4'):
        dark_mode_toggle = ui.button('Dark Mode', on_click=toggle_dark_mode).props('style="color: #ADD8E6; background-color: #1C3D5A; font-weight: bold; font-size: 16px; width: 150px; padding: 10px; border: 2px solid #1C3D5A; border-radius: 5px; transition: background-color 200ms ease-in-out, box-shadow 200ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:bg-blue-900 active:bg-blue-700')
        # Adding log file buttons
        log_files = {
            "Premises Log": "./memory/logs/premises.json",
            "Not Premise Log": "./memory/logs/notpremise.json",
            "Truth Tables Log": "./memory/logs/truth_tables.json",
            "Thoughts Log": "./memory/logs/thoughts.json",
            "Conclusions Log": "./memory/logs/conclusions.txt",
            "Decisions Log": "./memory/logs/decisions.json"
        }

    # Function to view log files
    def view_log(file_path):
        log_content = openmind.read_log_file(file_path)
        log_container.clear()  # Clear the existing log content
        with log_container:
            ui.markdown(log_content).classes('w-full')

    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('chat').classes('response-style')
        logs_tab = ui.tab('logs').props('style="color: #218838; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 200ms ease-in-out, box-shadow 200ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')
        api_tab = ui.tab('APIk').props('style="color: #218838; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 100ms ease-in-out, box-shadow 100ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')
    # response window
    with ui.tab_panels(tabs, value=chat_tab).props('style="color: rgb(0, 50, 0); background-color: rgba(0, 0, 0, 0.666);"').classes('response-style'):
        message_container = ui.tab_panel(chat_tab).classes('items-stretch')
        openmind.message_container = message_container  # Pass the container to OpenMind
        with ui.tab_panel(logs_tab):
            log = ui.log().classes('w-full h-full')
            log_container = ui.column().classes('w-full')
            openmind.log = log  # Pass the log to OpenMind
            for log_name, log_path in log_files.items():
                ui.button(log_name, on_click=lambda path=log_path: view_log(path)).props('style="color: #ADD8E6; font-weight: bold; background-color: #1C3D5A; font-size: 16px; width: 150px; padding: 10px; border: 2px solid #1C3D5A; border-radius: 5px;"').classes('justify-center')
        with ui.tab_panel(api_tab):
            ui.label('Manage API Keys').classes('text-lg font-bold')
            with ui.row().classes('items-center'):
                openmind.service_input = ui.input('Service (e.g., "openai", "groq")').classes('flex-1')
                openmind.key_input = ui.input('API Key').classes('flex-1')
            with ui.dropdown_button('Actions', auto_close=True):
                ui.menu_item('Add API Key', on_click=openmind.add_api_key).props('style="color: #218838; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 100ms ease-in-out, box-shadow 100ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')
                ui.menu_item('List API Keys', on_click=openmind.list_api_keys).props('style="color: green; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 100ms ease-in-out, box-shadow 100ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')

            # Container to list keys with delete buttons
            keys_container = ui.column().classes('w-full')
            openmind.keys_container = keys_container  # Pass the container to OpenMind

    with ui.footer().classes('bg-black'), ui.column().classes('w-full max-w-3xl mx-auto my-6 input-area'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'Enter your prompt here'
            text = ui.input(placeholder='Enter text here').props('rounded outlined input-class=mx-3 bg-green-100 input-style="color: green" input-class="font-mono"').props('style="border: 2px solid #4CAF50; width: 100%; outline: none;"').on('keydown.enter', send)
        ui.markdown('[easyAGI](https://rage.pythai.net)').classes('text-xs self-end mr-8 m-[-1em] text-primary').props('style="color: green; font-weight: bold;').classes('text-lg font-bold')

    # Start the main loop
    asyncio.create_task(openmind.main_loop())

logging.debug("starting easyAGI")
ui.run(title='easyAGI')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Shutting down...")

