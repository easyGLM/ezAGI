# mastermind.py (c) 2024 Gregory L. Magnusson MIT licence
# mastermind provides orchestration for agency

import os
import json
import logging
import threading
from abc import ABC
from typing import Dict, Type, Union, Any
import psutil
from datetime import datetime
from bdi import Belief, Desire, Intention, BDIModel
from self_healing import resilient_function, monitor_system_health, perform_self_healing_procedure
from memory import create_memory_folders, store_in_stm, DialogEntry

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Auto-Configuration for config.json
def auto_configure():
    config_dir = './mindx'
    config_path = os.path.join(config_dir, 'config.json')
    default_config = {
        'agents': ['SimpleCoder.py', 'autonomize.py'],
        'settings': {
            'max_cpu_usage': 80,  # Maximum CPU usage percentage
            'max_memory_usage': 80,  # Maximum memory usage percentage
            'self_healing': True  # Enable self-healing
        }
    }
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

    if not os.path.exists(config_path):
        with open(config_path, 'w') as config_file:
            json.dump(default_config, config_file, indent=4)
        logging.info(f'{config_path} created with default settings.')
    else:
        logging.info(f'{config_path} already exists. Skipping auto-configuration.')

# Calling auto-configuration function during the initialization
auto_configure()

class AgentBase(ABC):
    """Base class defining the essential methods for agents managed by MASTERMIND."""

    def __init__(self):
        self.bdi_model = BDIModel()
        self.memory_initialized = False

    def initialize_agent(self):
        """Prepare the agent for execution."""
        create_memory_folders()
        self.memory_initialized = True
        logging.info("Memory folders created and initialized.")
        self.bdi_model.add_belief(Belief("Agent is initialized"))
        self.bdi_model.add_desire(Desire("Agent desires to execute"))
        self.bdi_model.add_intention(Intention("Agent intends to complete its task"))

    def execute_agent(self):
        """Core logic of the agent."""
        raise NotImplementedError("The method execute_agent() must be implemented by the subclass.")

    def get_agent_data(self):
        """Retrieve execution results or data."""
        raise NotImplementedError("The method get_agent_data() must be implemented by the subclass.")

    def shutdown_agent(self):
        """Clean up resources post-execution."""
        if self.memory_initialized:
            logging.info("Shutting down agent and saving short-term memory.")
            store_in_stm()

class MASTERMIND:
    """Core class responsible for managing agent lifecycles within the MASTERMIND framework."""

    def __init__(self):
        self.agent_store: Dict[str, AgentBase] = {}
        self.data_store: Dict[str, Union[str, Dict]] = {}
        self.bdi_model = BDIModel()
        self.load_config()
        
    def load_config(self):
        try:
            with open("./mindx/config.json", "r") as f:
                self.config = json.load(f)
        except Exception as e:
            logging.error(f"Could not load config: {e}")

    def load_agent(self, agent_name: str, agent_class: Type[AgentBase]):
        # Security Check
        if not self.validate_agent(agent_name):
            logging.error(f"Agent {agent_name} failed the security validation.")
            return

        try:
            agent_instance = agent_class()
            agent_instance.initialize_agent()
            self.agent_store[agent_name] = agent_instance
        except Exception as e:
            logging.error(f"Failed to load agent {agent_name}: {e}")

    def unload_agent(self, agent_name: str):
        try:
            agent_instance = self.agent_store.pop(agent_name)
            agent_instance.shutdown_agent()
        except KeyError:
            logging.error(f"Agent {agent_name} not found.")
        except Exception as e:
            logging.error(f"Failed to unload agent {agent_name}: {e}")

    def execute_agents(self):
        threads = []
        for agent_name, agent_instance in self.agent_store.items():
            thread = threading.Thread(target=self.execute_single_agent, args=(agent_name, agent_instance,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def execute_single_agent(self, agent_name: str, agent_instance: AgentBase):
        try:
            agent_instance.execute_agent()
            agent_data = agent_instance.get_agent_data()
            self.accumulate_data(agent_name, agent_data)
        except Exception as e:
            logging.error(f"Failed to execute agent {agent_name}: {e}")

    def accumulate_data(self, agent_name: str, data: Union[str, Dict]):
        # Data Validation
        if not self.validate_data(data):
            logging.error(f"Data from agent {agent_name} failed the validation check.")
            return
        self.data_store[agent_name] = data

    def get_data(self, agent_name: str):
        return self.data_store.get(agent_name, "Data not found.")

    def validate_agent(self, agent_name: str) -> bool:
        # For now, a simple validation to check if the agent is in the allowed list
        return agent_name in self.config.get("agents", [])

    def validate_data(self, data: Union[str, Dict]) -> bool:
        # Placeholder for more complex data validation
        return True

    def monitor_resources(self):
        """Monitor system resources and perform self-healing if necessary."""
        # Simple resource monitoring using psutil
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        logging.info(f"CPU Usage: {cpu_percent}%")
        logging.info(f"Memory Usage: {memory_info.percent}%")
        
        # Call self-healing functions if resources are under pressure
        if not monitor_system_health():
            logging.warning("System health is compromised. Initiating self-healing procedures.")
            perform_self_healing_procedure()

    def integrate_with_simplecoder(self, coder_instance):
        """
        Integrates a SimpleCoder instance with the MASTERMIND framework.
        
        :param coder_instance: An instance of SimpleCoder.
        """
        logging.info("Integrating SimpleCoder with MASTERMIND...")
        self.agent_store["SimpleCoder"] = coder_instance
        logging.info("SimpleCoder integrated successfully.")

# Save data store to JSON file
def save_data_store(mastermind_instance: MASTERMIND):
    """Save data store to ./mindx/agency."""
    try:
        os.makedirs('./mindx/agency', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_store_path = f"./mindx/agency/data_store_{timestamp}.json"
        with open(data_store_path, "w") as f:
            json.dump(mastermind_instance.data_store, f, indent=4)
        logging.info(f"Data store saved to {data_store_path}")
    except Exception as e:
        logging.error(f"Failed to save data store: {e}")

# Example of a simple agent that implements the AgentBase
class SimpleAgent(AgentBase):

    def initialize_agent(self):
        super().initialize_agent()
        self.data = "Initialized"

    def execute_agent(self):
        self.data = "Executed"

    def get_agent_data(self):
        return self.data

    def shutdown_agent(self):
        super().shutdown_agent()
        self.data = "Shutdown"

if __name__ == "__main__":
    mastermind = MASTERMIND()
    mastermind.load_agent("SimpleAgent", SimpleAgent)

    # Integrate SimpleCoder with MASTERMIND
    from SimpleCoder import SimpleCoder
    simple_coder = SimpleCoder()
    mastermind.integrate_with_simplecoder(simple_coder)

    mastermind.execute_agents()
    save_data_store(mastermind)
    mastermind.monitor_resources()
    logging.info("All agents have been executed.")

