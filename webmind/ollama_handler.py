import logging
import subprocess
import asyncio

class OllamaModel:
    """
    Class to interact with Llama3 model via the Ollama service.
    """
    def __init__(self):
        self.api_url = "http://localhost:11434/api"

    async def generate_response_async(self, knowledge, model="llama3"):
        """
        Generate a response from the Llama3 model based on the given knowledge prompt using streaming.
        """
        try:
            response_content = ""
            stream = ollama.chat(model=model, messages=[{'role': 'user', 'content': knowledge}], stream=True)
            async for chunk in stream:
                response_content += chunk['message']['content']
            return response_content
        except Exception as e:
            logging.error(f"ollama api error: {e}")
            return "error: unable to generate a response due to an issue with the ollama api."

    async def show_ollama_info_async(self):
        """
        Show information about the Ollama service.
        """
        command = "ollama show"
        try:
            result = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await result.communicate()
            if result.returncode == 0:
                return stdout.decode().strip()
            else:
                logging.error(f"ollama api error: {stderr.decode().strip()}")
                return ""
        except Exception as e:
            logging.error(f"ollama api error: {e}")
            return ""

    def list_models(self):
        """
        List all available models in the Ollama service.
        """
        command = "ollama list"
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().splitlines()
            else:
                logging.error(f"ollama api error: {result.stderr}")
                return []
        except Exception as e:
            logging.error(f"ollama api error: {e}")
            return []

    def install_ollama(self):
        """
        Install Ollama using the provided installation script.
        """
        command = "curl -fsSL https://ollama.com/install.sh | sh"
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return "Ollama installation successful."
            else:
                logging.error(f"ollama install error: {result.stderr}")
                return "error: unable to install ollama."
        except Exception as e:
            logging.error(f"ollama install error: {e}")
            return "error: unable to install ollama."

def check_ollama_installation():
    command = "ollama list"
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("Ollama is installed and accessible.")
            return True
        else:
            logging.error("Ollama is not accessible.")
            return False
    except Exception as e:
        logging.error(f"Failed to check Ollama installation: {e}")
        return False
