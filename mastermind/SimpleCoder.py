# SimpleCoder.py (c) 2024 Gregory L. Magnusson MIT license
# Access to reasoning from automind.agi and automindx.bdi

import json
import logging
import os
from webmind.api import APIManager
from memory.memory import create_memory_folders
from automind.agi import AGI
from automindx.bdi import Belief, Desire, Intention, Goal, Reward
from webmind.chatter import GPT4o, GroqModel

class SimpleCoder:
    def __init__(self):
        self.name = "SimpleCoder"
        self.supported_languages = ['Python', 'JavaScript', 'Markdown', 'Bash']
        self.activity_log = []
        self.api_manager = APIManager()
        self.agi = self.initialize_agi()
        create_memory_folders()
        self.agency_dir = './mindx/agency'
        self._setup_agency_directory()

    def _setup_agency_directory(self):
        """Ensure the agency directory exists and has the correct permissions."""
        if not os.path.exists(self.agency_dir):
            os.makedirs(self.agency_dir, exist_ok=True)
        current_permissions = oct(os.stat(self.agency_dir).st_mode)[-3:]
        if current_permissions != '700':
            os.chmod(self.agency_dir, 0o700)

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

    def execute_task(self, language, task):
        is_valid, message = self.validate_input(language, task)
        if not is_valid:
            return message
        
        # Placeholder for prompting AGI to ensure production-ready code
        prompt = f"Generate production-ready {language} code for task: {task}. Output only the code as the solution."
        
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
            try:
                result = os.system(f'bash {file_path}')
                return f"Execution result: {result}"
            except Exception as e:
                logging.error(f"Failed to execute file: {e}")
                return "Error executing file."

        else:
            return "Invalid action or missing parameters."

# Example usage
if __name__ == "__main__":
    coder = SimpleCoder()
    coder.execute_task('Python', 'hello_world')
    print(coder.interact_with_agency('write', 'test.sh', '#!/bin/bash\necho "Hello from agency"'))
    print(coder.interact_with_agency('execute', 'test.sh'))
    print(coder.interact_with_agency('read', 'test.sh'))
