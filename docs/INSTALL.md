# ezAGI install — python >= 3.10

```bash
git clone https://github.com/easyGLM/ezAGI/
cd ezAGI
python3 -m venv agi
source agi/bin/activate
pip install -r requirements.txt
# start the ezAGI console
python3 ezAGI.py
```

The console serves at http://localhost:8080 — add an API key in the **APIk** tab
or just start a local Ollama and ezAGI uses it as the failsafe provider.

## optional extras

```bash
pip install -e ".[anthropic]"   # Anthropic Claude provider
pip install -e ".[learn]"       # SimpleMind + coach (jax, optax, numpy, sklearn, pandas, matplotlib)
pip install -e ".[dev]"         # pytest for the offline test suite
pip install -e .                # installs the `ezagi` console command
```

## providers and keys

Keys are stored in a local `.env` (gitignored) via the APIk tab or by hand:

```
OPENAI_API_KEY=...
GROQ_API_KEY=...
TOGETHER_API_KEY=...
ANTHROPIC_API_KEY=...
OLLAMA_API_KEY=...        # Ollama Cloud (https://ollama.com)
```

## Ollama

- **local**: install from https://ollama.com/download, `ollama pull llama3`,
  keep the daemon running — ezAGI detects it at http://localhost:11434 and uses
  it automatically when no cloud key is stored.
- **Ollama Cloud**: create a key at https://ollama.com and add it as service
  `ollama` in the APIk tab; cloud models (gpt-oss:120b, deepseek-v3.1:671b,
  qwen3-coder:480b) appear in the model selector.

## windows

```powershell
git clone https://github.com/easyGLM/ezAGI/
cd ezAGI
python -m venv agi
agi\Scripts\activate
pip install -r requirements.txt
python ezAGI.py
```

## tests

```bash
pytest tests/ -q    # offline — no API keys, no network
```
