# ollama_install.py
import subprocess
import sys
import platform
import ollama
import logging
import os

class OllamaInstaller:
    def __init__(self):
        self.client = ollama.Client(host='http://localhost:11434')
        self.default_model = "llama3"
        self.installation_dir = './mindx'
        self.ensure_installation_dir()

    def ensure_installation_dir(self):
        if not os.path.exists(self.installation_dir):
            os.makedirs(self.installation_dir)

    def generate_response(self, knowledge, model=None):
        if model is None:
            model = self.default_model
        prompt = [{'role': 'user', 'content': knowledge}]
        try:
            response = self.client.chat(model=model, messages=prompt)
            decision = response['message']['content']
            return decision.lower()
        except ollama.ResponseError as e:
            logging.error(f"Ollama API error: {e}")
            return "error: unable to generate a response due to an issue with the Ollama API."

    def install_ollama(self):
        system = platform.system().lower()
        if system == 'windows':
            self.install_ollama_windows()
        elif system == 'darwin':  # macOS
            self.install_ollama_mac()
        elif system == 'linux':
            self.install_ollama_linux()
        else:
            raise EnvironmentError(f"Unsupported operating system: {system}")
        self.run_deepseek_coder()

    def install_ollama_windows(self):
        url = "https://ollama.com/download/OllamaSetup.exe"
        exe_path = os.path.join(self.installation_dir, 'OllamaSetup.exe')
        self.download_file(url, exe_path)
        subprocess.run(exe_path, check=True)
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
        try:
            import requests
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            logging.info(f"Downloaded file from {url} to {dest}")
        except ImportError:
            raise ImportError("Please install the requests library to download files.")

    def run_deepseek_coder(self):
        command = "ollama run deepseek-coder"
        subprocess.run(command, shell=True, check=True)
        logging.info("Ran deepseek-coder using Ollama")

if __name__ == "__main__":
    installer = OllamaInstaller()
    installer.install_ollama()

