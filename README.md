# ezAGI (c) 2024–2026 PYTHAI
# Augmented Generative Intelligence
a framework for enhancing LLM with reasoning — **v1.0.0**

ezAGI is the easy Augmented Generative Intelligence system: human-like reasoning,
decision-making, self-healing and learning as output from existing LLM. Every input
becomes a premise, every conclusion is validated, every log is a memory.

```
ezAGI/
├── ezAGI.py           # the ezAGI console (canonical entry point)
├── easyAGI.py         # compatibility shim launching the same console
├── automind/          # reasoning core
│   ├── openmind.py         # OpenMind hub: providers, chat, autonomous reasoning loop
│   ├── automind.py         # FundamentalAGI wrapper
│   ├── agi.py              # AGI + EasyAGI (CLI orchestrator)
│   ├── SocraticReasoning.py# premises -> challenge -> conclusion -> validation
│   └── logic.py            # LogicTables: truth tables, safe propositional evaluator
├── automindx/         # agency environment: BDI, reasoning styles, self-healing
│   ├── bdi.py, reasoning.py (THOT), make_decision.py
│   └── epistemic / fuzzy / nonmonotonic / deductive / abduction / prediction
├── mastermind/        # orchestrator of agency: controller.py, SimpleCoder, easyAGIcli
├── simplemind/        # SimpleMind JAX neural network + coach trainer
├── webmind/           # api keys (.env), chatter model wrappers, ollama handling
├── memory/            # stm / ltm / episodic / truth / logs — all logs are memories
├── docs/              # module documentation + lineage.md
├── tests/             # offline smoke suite (no API keys, no network)
└── gfx/               # easystyle.css and graphics
```

## INSTALL

python >= 3.10

```bash
git clone https://github.com/easyGLM/ezAGI/
cd ezAGI
python3 -m venv agi
source agi/bin/activate
pip install -r requirements.txt
# optional extras
pip install -e ".[anthropic]"   # Claude provider
pip install -e ".[learn]"       # SimpleMind/coach (jax, optax, numpy, sklearn, pandas)
# run the ezAGI console
python3 ezAGI.py                # or: pip install -e . && ezagi
```

The console serves at http://localhost:8080

## Providers

Add keys in the **APIk** tab (stored in `.env` via python-dotenv) or start a local
Ollama — ezAGI resolves providers cloud-first with the local daemon as failsafe.

| provider | service name (APIk) | default model | notes |
|---|---|---|---|
| OpenAI | `openai` | gpt-4.1 | |
| Groq | `groq` | llama-3.3-70b-versatile | |
| together.ai | `together` | meta-llama/Llama-3.3-70B-Instruct-Turbo | |
| Anthropic | `anthropic` | claude-opus-4-8 | `pip install "ezagi[anthropic]"` |
| Ollama Cloud | `ollama` | gpt-oss:120b | key from https://ollama.com |
| Ollama local | — (no key) | first installed model | daemon at localhost:11434 |

## The ezAGI console

- **chat** — the production interaction from ezAGI: your queries and the streamed
  answers, nothing else
- **reasoning** — the live internal SocraticReasoning trace, clearly separated from
  production output: premises as they are added, generated premises, challenges,
  validation verdicts with confidence, conclusions, and the autonomous reasoning loop
- **header** — provider + model selectors (live local Ollama model list and Ollama
  Cloud models included), live token counters (last response and session), reasoning
  state chip, sampling controls (temperature / max tokens), dark mode
- **logs** — the reasoning artifacts on disk (premises, thoughts, truth, conclusions)
- **APIk** — API key management

## Components

MASTERMIND — the central controller of agency: loads agents, orchestrates execution,
monitors health (mastermind/controller.py)

SimpleCoder — the coding agent generating python, javascript, markdown and bash
(execution is gated behind an explicit opt-in)

BDI — Belief-Desire-Intention model for human-like practical reasoning (automindx/bdi.py)

Self-Healing — CPU, memory and disk monitoring with recovery actions (automindx/self_healing.py)

Reasoning — deductive, inductive, abductive, analogical and more, dispatched by THOT
(automindx/reasoning.py)

LogicTables — logical variables, expressions and truth tables with a safe (eval-free)
propositional evaluator (automind/logic.py)

SocraticReasoning — every input is a premise; conclusions are validated by LLM
judgment (with truth tables as the fast path for propositional statements) and
recorded with confidence to ./memory/logs/truth.json

SimpleMind — the minimalist JAX neural network for learning and long-term memory
(simplemind/SimpleMind.py)

Coach — trains SimpleMind from accumulated conversation memory in ./memory/stm
(simplemind/coach.py)

## Integration

Initialization: OpenMind resolves a provider and initializes FundamentalAGI.
Execution: queries stream into the chat window while SocraticReasoning traces into
the reasoning panel. Monitoring: the autonomous reasoning loop keeps reasoning about
the latest input (idling when there is nothing new). Learning: coach trains SimpleMind
on stored memories. Decision-Making: validated truths accumulate with confidence for
informed decisions. See [docs/lineage.md](docs/lineage.md) for the full workflow.

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -q        # offline: no API keys, no network required
```

## Security notes

- API keys are stored in a local `.env` (gitignored) — local single-user tool
- SimpleCoder `execute` is disabled by default (`allow_execute=False`)
- LogicTables evaluates expressions with an AST whitelist, never `eval`
- ezAGI never pipes install scripts to a shell; Ollama installs print the official
  command for you to run

## the PYTHAI project family

ezAGI is a [PYTHAI](https://github.com/pythaiml) project by Gregory L. Magnusson
(Professor Codephreak). The lineage — documented in
[docs/lineage.md](docs/lineage.md):

**AUTOMINDx → aGLM → MASTERMIND → RAGE → funAGI → ezAGI → mindX**

- [easyGLM/ezAGI](https://github.com/easyGLM/ezAGI) — this repository, the current direction
- [easyAGI/ezAGI](https://github.com/easyAGI/ezAGI) — frozen historical snapshot of the minimal reasoning-as-logs version
- [pythaiml/automindx](https://github.com/pythaiml/automindx) — the Professor Codephreak local language model environment; aGLM, memory services, the console whose fashion this UI follows
- [pythaiml/funAGI](https://github.com/pythaiml/funAGI) / [autoGLM/funAGI](https://github.com/autoGLM/funAGI) — fundamental AGI: SocraticReasoning + logic tables, the point of departure
- [autoGLM/easyAGI](https://github.com/autoGLM/easyAGI) — the original non-integrated module framework
- [mastermindML/mastermind](https://github.com/mastermindML/mastermind) — agency creation and control
- [openmindx/OpenMind](https://github.com/openmindx/OpenMind) — the native desktop AI workspace for local models (Tauri 2); the desktop evolution of openmind
- [openmindx/agi](https://github.com/openmindx/agi) — open AGI components
- [llamagi/lmagi](https://github.com/llamagi/lmagi) — the Ollama/llama departure point
- [Professor-Codephreak](https://github.com/Professor-Codephreak) — the author
- mindX — the successor: augmentic intelligence orchestration (Darwin-Gödel machine)

[easyAGI](https://rage.pythai.net) — a PYTHAI project · MIT license
