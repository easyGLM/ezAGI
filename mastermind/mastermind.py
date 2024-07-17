# MASTERMIND.py (c) 2024 Gregory L. Magnusson MIT license

import os
import json
import logging
import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from webmind.api import APIManager
from memory.memory import create_memory_folders
from automind.agi import AGI
from automindx.bdi import Belief, Desire, Intention, Goal, Reward
from webmind.chatter import GPT4o, GroqModel

logging.basicConfig(level=logging.INFO)

class AgentInterface(ABC):
    """Abstract base class defining the essential methods for agents managed by MASTERMIND."""

    @abstractmethod
    def initialize(self):
        """Prepare the agent for execution."""
        pass

    @abstractmethod
    def execute_task(self, language, task):
        """Core logic of the agent."""
        pass

    @abstractmethod
    def fetch_data(self):
        """Retrieve execution results or data."""
        pass

    @abstractmethod
    def terminate(self):
        """Clean up resources post-execution."""
        pass

class MASTERMIND:
    """Core class responsible for managing agent lifecycles within the MASTERMIND framework."""

    def __init__(self):
        self.agents = {}
        self.directories = ["agents", "tools", "executor", "./mindx/agency"]
        self._setup_directories()
        self._load_agents_from_directory("agents")
        self._load_agents_from_directory("tools")

    def _setup_directories(self):
        """Ensures the existence of required directories and sets appropriate permissions."""
        for directory in self.directories:
            os.makedirs(directory, exist_ok=True)
            os.chmod(directory, 0o674)

    def _load_agents_from_directory(self, directory):
        """Dynamically loads and initializes agents from the specified directory."""
        for filename in os.listdir(directory):
            if filename.endswith('.py'):
                agent_name = filename[:-3]  # Strip off '.py'
                module_path = os.path.join(directory, filename)
                self._load_agent_module(agent_name, module_path)

    def _load_agent_module(self, agent_name, module_path):
        """Loads an agent module and initializes its class if it implements AgentInterface."""
        spec = importlib.util.spec_from_file_location(agent_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[agent_name] = module
        spec.loader.exec_module(module)
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type) and issubclass(attribute, AgentInterface) and attribute != AgentInterface:
                self.agents[agent_name] = attribute()
                logging.info(f"Loaded agent: {agent_name}")

    def execute_agents(self):
        """Executes all loaded agents concurrently in separate threads."""
        for agent_name, agent_instance in self.agents.items():
            thread = threading.Thread(target=self._execute_single_agent, args=(agent_name, agent_instance,))
            thread.start()
            thread.join()

    def _execute_single_agent(self, agent_name, agent_instance):
        """Handles the lifecycle of a single agent, including initialization, execution, and shutdown."""
        try:
            agent_instance.initialize()
            agent_instance.execute_task('Python', 'hello_world')
            data = agent_instance.fetch_data()
            logging.info(f"Agent {agent_name} executed successfully with data: {data}")
            agent_instance.terminate()
        except Exception as e:
            logging.error(f"Error executing agent {agent_name}: {e}")

if __name__ == "__main__":
    mastermind = MASTERMIND()
    mastermind.execute_agents()
    logging.info("All agents have been executed.")
