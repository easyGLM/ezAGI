# SimpleCoder.py (c) 2024 Gregory L. Magnusson MIT licence
# access to internat reasoning through automind.agi
# coding agent with reasoning from automindx.bdi

import json
import logging
from ..webmind.api import APIManager
from ..memory.memory import create_memory_folders, store_in_stm, DialogEntry
from ..automind.agi import AGI
from ..automindx.bdi import Belief, Desire, Intention, BDIModel

class SimpleCoder:
    def __init__(self):
        self.name = "SimpleCoder"
        self.supported_languages = [
            'Python', 'JavaScript', 'Go', 'Ruby', 
            'Bash', 'Perl', 'HTML', 'Markup', 'AIML', 'CSS', 'Three.js', 'Solidity', 'PyTeal', 'Scilla'
        ]
        self.activity_log = []
        self.api_manager = APIManager()
        self.agi = self.initialize_agi()
        create_memory_folders()

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
        
        code_snippets = {
            'Python': "print('Hello, World!')",
            'JavaScript': "console.log('Hello, World!');",
            'Go': 'fmt.Println("Hello, World!")',
            'Ruby': 'puts "Hello, World!"',
            'Bash': 'echo "Hello, World!"',
            'Perl': 'print "Hello, World!\\n";',
            'HTML': '<h1>Hello, World!</h1>',
            'Markup': '# Hello, World!',
            'AIML': '<category><pattern>HELLO</pattern><template>World!</template></category>',
            'CSS': '/* Hello, World! */',
            'Three.js': 'console.log("Three.js Hello, World!");',
            'Solidity': '/* Solidity Hello, World! */',
            'PyTeal': '# PyTeal Hello, World!',
            'Scilla': '(* Scilla Hello, World! *)'
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

class MASTERMIND:
    def __init__(self):
        self.agents = {}
        self.bdi_model = BDIModel()
        create_memory_folders()

    def create_agent(self, agent_name, agent_class):
        agent = agent_class()
        agent.set_name(agent_name)
        
        belief = input("Enter Belief: ")
        desire = input("Enter Desire: ")
        intention = input("Enter Intention: ")
        
        belief_obj = Belief(belief)
        desire_obj = Desire(desire)
        intention_obj = Intention(intention)
        self.bdi_model.add_belief(belief_obj)
        self.bdi_model.add_desire(desire_obj)
        self.bdi_model.add_intention(intention_obj)
        
        self.agents[agent_name] = agent

    def delete_agent(self, agent_name):
        if agent_name in self.agents:
            del self.agents[agent_name]
        else:
            logging.warning(f"Agent '{agent_name}' not found.")

    def export_agent(self, agent_name, filename):
        agent = self.agents.get(agent_name)
        if agent:
            agent.export_config(filename)
        else:
            logging.warning(f"Agent '{agent_name}' not found.")

    def import_agent(self, agent_name, filename):
        agent = self.agents.get(agent_name)
        if agent:
            agent.import_config(filename)
        else:
            logging.warning(f"Agent '{agent_name}' not found.")

    def display_ui(self):
        print("MASTERMIND Console")
        while True:
            print("Loaded Agents:")
            for agent in self.agents.keys():
                print(f" - {agent}")
            command = input("Enter command ('help' for available commands): ")
            if command == 'help':
                print("Available commands: create, delete, export, import, interact, q")
            elif command == 'q':
                break
            elif command == 'create':
                agent_name = input("Enter the name of the new agent: ")
                agent_class = SimpleCoder  # Can be extended to other agent classes
                self.create_agent(agent_name, agent_class)
            elif command == 'delete':
                agent_name = input("Enter the name of the agent to delete: ")
                self.delete_agent(agent_name)
            elif command == 'export':
                agent_name = input("Enter the name of the agent to export: ")
                filename = input("Enter the filename to export to: ")
                self.export_agent(agent_name, filename)
            elif command == 'import':
                agent_name = input("Enter the name of the agent to import: ")
                filename = input("Enter the filename to import from: ")
                self.import_agent(agent_name, filename)
            elif command == 'interact':
                agent_name = input("Enter the name of the agent to interact with: ")
                agent = self.agents.get(agent_name)
                if agent:
                    agent.display_ui()
                else:
                    logging.warning(f"Agent '{agent_name}' not found.")

if __name__ == "__main__":
    mastermind = MASTERMIND()
    mastermind.display_ui()

