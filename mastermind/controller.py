"""
MASTERMIND Controller Documentation
===================================

The MASTERMIND Controller is a sophisticated framework designed to manage and execute a collection of agents, each with distinct capabilities and tasks. It employs a modular architecture, facilitating the seamless integration and management of agents. This document provides an extensive overview of the MASTERMIND Controller's components, functionalities, and usage.

Components:
-----------
- `AgentInterface`: An abstract base class that defines the essential methods each agent must implement. These methods include `initialize`, `execute_task`, `fetch_data`, and `terminate`.
- `MASTERMIND`: The core class that orchestrates the loading, execution, and management of agents. It handles directory setup, dynamic agent loading, and concurrent agent execution.

Key Functionalities:
-------------------
1. **Directory Setup**: The `MASTERMIND` class automatically creates and manages three key directories: `agents`, `tools`, `executor`, and `./mindx/agency`. These directories are essential for organizing agent scripts based on their development stage and functionality.
2. **Dynamic Agent Loading**: Agents are dynamically loaded from the `agents` and `tools` directories. This allows for the addition or removal of agent scripts without modifying the core controller code.
3. **Concurrent Agent Execution**: Agents are executed concurrently, each in its own thread, enabling efficient utilization of system resources and parallel task processing.

Usage Guide:
------------
1. Implement agent classes in Python files and place them in the `agents` or `tools` directories. Ensure each agent class inherits from `AgentInterface` and implements all abstract methods.
2. Run the `MASTERMINDcontroller.py` script. The controller will automatically load and execute all agents found in the designated directories.

AgentInterface Methods:
-----------------------
- `initialize()`: Prepares the agent for execution. This might involve setting up necessary resources or configurations.
- `execute_task(language, task)`: Contains the main logic of the agent. This is where the agent performs its designated task.
- `fetch_data()`: Retrieves any data or results produced during the agent's execution.
- `terminate()`: Cleans up resources and performs any necessary teardown activities post-execution.

Example:
--------
Below is an example of how to implement a simple agent that conforms to the `AgentInterface`:

    class SimpleAgent(AgentInterface):
        def initialize(self):
            print("Initializing SimpleAgent.")
            
        def execute_task(self, language, task):
            print("Executing task in SimpleAgent.")
            
        def fetch_data(self):
            return "Data from SimpleAgent."
            
        def terminate(self):
            print("Shutting down SimpleAgent.")

To execute this agent, place its script in the `agents` directory and run the `MASTERMINDcontroller.py` script.

"""

import os
import json
import logging
import threading
from abc import ABC, abstractmethod
import importlib.util
import sys

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

    def __init__(self, autonomous=True):
        self.agents = {}
        self.directories = ["agents", "tools", "executor", "./mindx/agency"]
        self.autonomous = autonomous
        self._setup_directories()
        self._load_agents_from_directory("agents")
        self._load_agents_from_directory("tools")

    def _setup_directories(self):
        """Ensures the existence of required directories and sets appropriate permissions."""
        for directory in self.directories:
            os.makedirs(directory, exist_ok=True)
            os.chmod(directory, 0o700)

    def _load_agents_from_directory(self, directory):
        """Dynamically loads and initializes agents from the specified directory."""
        for filename in os.listdir(directory):
            if filename.endswith('.py'):
                agent_name = filename[:-3]  # Strip off '.py'
                module_path = os.path.join(directory, filename)
                self._load_agent_module(agent_name, module_path)

    def _load_agent_module(self, agent_name, module_path):
        """Loads an agent module and initializes its class if it implements AgentInterface."""
        try:
            spec = importlib.util.spec_from_file_location(agent_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[agent_name] = module
            spec.loader.exec_module(module)
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type) and issubclass(attribute, AgentInterface) and attribute != AgentInterface:
                    self.agents[agent_name] = attribute()
                    logging.info(f"Loaded agent: {agent_name}")
        except Exception as e:
            logging.error(f"Failed to load agent module {agent_name}: {e}")

    def execute_agents(self):
        """Executes all loaded agents concurrently in separate threads."""
        threads = []
        for agent_name, agent_instance in self.agents.items():
            thread = threading.Thread(target=self._execute_single_agent, args=(agent_name, agent_instance,))
            threads.append(thread)
            thread.start()

        for thread in threads:
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

    def toggle_autonomous(self, state):
        """Toggle the autonomous mode on or off."""
        self.autonomous = state
        mode = "ON" if state else "OFF"
        logging.info(f"Autonomous mode is now {mode}")

if __name__ == "__main__":
    mastermind = MASTERMIND()
    mastermind.execute_agents()
    logging.info("All agents have been executed.")
