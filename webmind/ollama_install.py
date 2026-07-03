# ollama_install.py
# cross-platform Ollama install helper — prints official instructions by default
# and only performs an installation when explicitly confirmed
import subprocess
import platform
import logging
import os

from webmind.ollama_handler import OllamaHandler


class OllamaInstaller:
    def __init__(self):
        self.handler = OllamaHandler()
        self.default_model = "llama3"
        self.installation_dir = './mindx'
        self.ensure_installation_dir()

    def ensure_installation_dir(self):
        if not os.path.exists(self.installation_dir):
            os.makedirs(self.installation_dir)

    def generate_response(self, knowledge, model=None):
        import asyncio
        return asyncio.run(self.handler.generate_response_async(
            knowledge, model=model or self.default_model))

    def install_ollama(self, confirm=False):
        """
        Print (or with confirm=True run) the official install steps for this platform.
        """
        system = platform.system().lower()
        instructions = {
            'windows': "Download and run https://ollama.com/download/OllamaSetup.exe",
            'darwin': "Download https://ollama.com/download/Ollama-darwin.zip and unzip it",
            'linux': "Run: curl -fsSL https://ollama.com/install.sh | sh",
        }
        if system not in instructions:
            raise EnvironmentError(f"Unsupported operating system: {system}")
        if not confirm:
            message = (f"Ollama install on {system}:\n    {instructions[system]}\n"
                       "then rerun ezAGI. (call install_ollama(confirm=True) to let ezAGI run it)")
            logging.info(message)
            print(message)
            return message
        if system == 'windows':
            self.install_ollama_windows()
        elif system == 'darwin':
            self.install_ollama_mac()
        elif system == 'linux':
            self.install_ollama_linux()
        return "Ollama installation attempted — verify with `ollama list`."

    def install_ollama_windows(self):
        url = "https://ollama.com/download/OllamaSetup.exe"
        exe_path = os.path.join(self.installation_dir, 'OllamaSetup.exe')
        self.download_file(url, exe_path)
        subprocess.run([exe_path], check=True)
        logging.info("Ollama installed on Windows")

    def install_ollama_mac(self):
        url = "https://ollama.com/download/Ollama-darwin.zip"
        zip_path = os.path.join(self.installation_dir, 'Ollama-darwin.zip')
        self.download_file(url, zip_path)
        subprocess.run(['unzip', zip_path, '-d', self.installation_dir], check=True)
        logging.info("Ollama installed on macOS")

    def install_ollama_linux(self):
        command = "curl -fsSL https://ollama.com/install.sh | sh"
        subprocess.run(command, shell=True, check=True)
        logging.info("Ollama installed on Linux")

    def download_file(self, url, dest):
        import httpx
        with httpx.stream("GET", url, follow_redirects=True) as r:
            r.raise_for_status()
            with open(dest, 'wb') as f:
                for chunk in r.iter_bytes(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"Downloaded file from {url} to {dest}")

    def pull_model(self, model=None):
        model = model or self.default_model
        subprocess.run(["ollama", "pull", model], check=True)
        logging.info(f"Pulled {model} using Ollama")


if __name__ == "__main__":
    installer = OllamaInstaller()
    installer.install_ollama()
