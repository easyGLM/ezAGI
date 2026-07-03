# SimpleCoder.py (c) 2024 Gregory L. Magnusson MIT license
# Access to reasoning from automind.agi and automindx.bdi
# extends mastermind with ./mindx/agency

import json
import logging
import os
import subprocess
from webmind.api import APIManager
from memory.memory import create_memory_folders
from automind.agi import AGI
from automindx.bdi import Belief, Desire, Intention, Goal, Reward
from webmind.chatter import GPT4o, GroqModel
from mastermind.controller import MASTERMIND  # Importing MASTERMIND

class SimpleCoder:
    def __init__(self, allow_execute=False):
        self.name = "SimpleCoder"
        self.supported_languages = ['Python', 'JavaScript', 'Markdown', 'Bash']
        self.activity_log = []
        # allow_execute gates the 'execute' action (running bash from user input);
        # defaults to False so nothing is executed unless the caller opts in.
        self.allow_execute = allow_execute
        self.api_manager = APIManager()
        self.agi = self.initialize_agi()
        create_memory_folders()
        self.agency_dir = './mindx/agency'
        self._setup_agency_directory()
        self.mastermind = MASTERMIND()  # Initialize MASTERMIND

    def _setup_agency_directory(self):
        """Ensure the agency directory exists and has the correct permissions."""
        if not os.path.exists(self.agency_dir):
            os.makedirs(self.agency_dir, exist_ok=True)
        current_permissions = oct(os.stat(self.agency_dir).st_mode)[-3:]
        if current_permissions != '700':
            os.chmod(self.agency_dir, 0o674)

    def initialize_agi(self):
        openai_key = self.api_manager.get_api_key('openai')
        groq_key = self.api_manager.get_api_key('groq')
        
        if openai_key:
            chatter = GPT4o(openai_key)
        elif groq_key:
            chatter = GroqModel(groq_key)
        else:
            self.api_manager.manage_api_keys()
            return self.initialize_agi()
        
        return AGI(chatter)

    def validate_input(self, language, task):
        if language not in self.supported_languages:
            return False, f"Language {language} is not supported."
        if task not in ['hello_world']:
            return False, f"Task {task} is not supported."
        return True, "Input is valid."

    def expand_supported_languages(self, new_languages):
        """Expand the list of supported languages based on direction from MASTERMIND."""
        for language in new_languages:
            if language not in self.supported_languages:
                self.supported_languages.append(language)
                logging.info(f"Added new supported language: {language}")

    def execute_task(self, language, task):
        is_valid, message = self.validate_input(language, task)
        if not is_valid:
            return message
        
        # Fetch direction/state from MASTERMIND (controller exposes get_status())
        bdi_update = self.mastermind.get_status()
        
        # Expand supported languages if directed by MASTERMIND
        new_languages = bdi_update.get('new_languages', [])
        self.expand_supported_languages(new_languages)
        
        # Placeholder for prompting AGI to ensure production-ready code
        prompt = (
            f"Generate production-ready {language} code for task: {task}. "
            f"Output only the code as the solution. "
            f"Direction from MASTERMIND: {bdi_update}"
        )
        
        # Example code snippets for demonstration purposes
        code_snippets = {
            'Python': "print('Hello, World!')",
            'JavaScript': "console.log('Hello, World!');",
            'Markdown': '# Hello, World!',
            'Bash': 'echo "Hello, World!"'
        }

        code = code_snippets.get(language, "Language not supported.")
        
        self.activity_log.append({'language': language, 'task': task, 'code': code})
        self.save_log()
        return code

    def save_log(self):
        try:
            with open(f"{self.name}_activity_log.json", "w") as f:
                json.dump(self.activity_log, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save log: {e}")

    def load_log(self):
        try:
            with open(f"{self.name}_activity_log.json", "r") as f:
                self.activity_log = json.load(f)
        except FileNotFoundError:
            self.activity_log = []
        except Exception as e:
            logging.error(f"Failed to load log: {e}")

    def interact_with_agency(self, action, filename=None, content=None):
        file_path = os.path.join(self.agency_dir, filename) if filename else None
        
        if action == 'read' and file_path:
            try:
                with open(file_path, 'r') as f:
                    return f.read()
            except FileNotFoundError:
                return "File not found."
            except Exception as e:
                logging.error(f"Failed to read file: {e}")
                return "Error reading file."

        elif action == 'write' and file_path and content:
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                return "File written successfully."
            except Exception as e:
                logging.error(f"Failed to write file: {e}")
                return "Error writing file."

        elif action == 'execute' and file_path:
            # Gated behind allow_execute; when disabled we refuse rather than run.
            if not self.allow_execute:
                return ("Execution refused: SimpleCoder was constructed with "
                        "allow_execute=False. Re-create with allow_execute=True "
                        "to run scripts from the agency directory.")
            try:
                # command is derived from user-provided filenames; shell=True is
                # acceptable only because execution is behind the explicit
                # allow_execute opt-in gate above.
                result = subprocess.run(
                    f'bash {file_path}', shell=True,
                    capture_output=True, text=True
                )
                return (f"Execution result (rc={result.returncode}): "
                        f"{result.stdout}{result.stderr}")
            except Exception as e:
                logging.error(f"Failed to execute file: {e}")
                return "Error executing file."

        else:
            return "Invalid action or missing parameters."

# Example usage
if __name__ == "__main__":
    # allow_execute=True opts the demo into actually running the test script.
    coder = SimpleCoder(allow_execute=True)
    coder.execute_task('Python', 'hello_world')
    print(coder.interact_with_agency('write', 'test.sh', '#!/bin/bash\necho "Hello from agency"'))
    print(coder.interact_with_agency('execute', 'test.sh'))
    print(coder.interact_with_agency('read', 'test.sh'))
