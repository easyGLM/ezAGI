# webmind — external web functions of the ezAGI project

- **chatter.py** — input/response model wrappers with streaming and sampling
  controls: `GPT4o` (openai, default gpt-4.1), `GroqModel`
  (llama-3.3-70b-versatile), `TogetherModel` (Llama-3.3-70B-Instruct-Turbo),
  `AnthropicModel` (claude-opus-4-8, optional `pip install "ezagi[anthropic]"`),
  `OllamaModel` (local daemon or Ollama Cloud), plus `resolve_chatter` — the
  cloud-first provider resolution with local Ollama failsafe
- **ollama_handler.py** — dual-endpoint Ollama integration: the local daemon at
  http://localhost:11434 or Ollama Cloud at https://ollama.com with
  `OLLAMA_API_KEY` (Bearer auth); /api/chat streaming, /api/tags model listing
- **api.py** — APIManager: add/remove/list API keys stored in a local `.env`
- **html_head.py** — browser head controls (meta tags, styles)
- **ollama_install.py** — Ollama install helper (prints official instructions;
  never pipes scripts to a shell unless explicitly confirmed)
