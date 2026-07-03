# lineage — the road to easy Augmented Generative Intelligence

ezAGI (c) 2024–2026 PYTHAI · Gregory L. Magnusson (Professor Codephreak) · MIT

This document records two things: **where ezAGI comes from** (the PYTHAI project
lineage) and **how ezAGI works** (the full workflow from input to trained memory).

---

## Part 1 — the lineage

```
AUTOMINDx → aGLM → MASTERMIND → RAGE → funAGI → ezAGI → mindX
```

### AUTOMINDx
[pythaiml/automindx](https://github.com/pythaiml/automindx) — the Professor
Codephreak persona as a local, persona-driven language-model environment. It
introduced the persona console (streaming chat, reasoning traces, token counters,
sampling controls — the fashion the ezAGI v1.0.0 console follows), swappable
memory/model services, and prompt-space self-improvement from live feedback.
**Carried forward:** the automindx agency environment lives on as ezAGI's
`automindx/` package, and in mindX as `agents/automindx_agent.py` (persona/prompt
generation).

### aGLM — Autonomous General Learning Model
The augmentation layer, not a model: autonomous decision-making from belief systems
and feedback loops. **Carried forward:** the belief/decision discipline behind
`automindx/bdi.py` and the confidence-scored truths of SocraticReasoning.

### MASTERMIND
[mastermindML/mastermind](https://github.com/mastermindML/mastermind) — the
orchestrator of agency: agent lifecycle, configuration, monitoring.
**Carried forward:** ezAGI's `mastermind/controller.py` (MASTERMIND + SimpleCoder),
and in mindX the `mastermind_agent.py` strategic orchestrator.

### RAGE — Retrieval Augmented Generative Engine
The memory doctrine of the GATERAGE ecosystem: *RAGE remembers · aGLM decides ·
MASTERMIND orchestrates*. **Carried forward:** ezAGI's `memory/` package ("all logs
are memories"), and in mindX the MemoryAgent and pgvector memory.

### funAGI — fundamental AGI
[pythaiml/funAGI](https://github.com/pythaiml/funAGI) ·
[autoGLM/funAGI](https://github.com/autoGLM/funAGI) — the point of departure:
SocraticReasoning and logic tables. Modular memory + logic + reasoning + comms with
CLI and GUI. **Carried forward:** `agi.py`, `SocraticReasoning.py`, `logic.py`,
`memory.py`, `chatter.py`, `api.py` — the exact spine of ezAGI's automind/webmind.

### ezAGI — easy Augmented Generative Intelligence (this project)
[easyGLM/ezAGI](https://github.com/easyGLM/ezAGI) (current direction) ·
[easyAGI/ezAGI](https://github.com/easyAGI/ezAGI) (frozen minimal snapshot) — the
integrated framework: internal reasoning with conclusion logging. The Llama-3
hackathon entry that grew into the complete easy AGI system: multi-provider
reasoning, validated truths, the console UI, MASTERMIND agency, and **SimpleMind** —
the minimalist JAX neural network trained by **coach** on accumulated conversation
memory, giving the system a learning long-term memory of its own.

### mindX — augmentic intelligence
The successor: an augmentic-intelligence orchestration platform, a protocol-based
Darwin-Gödel machine with sovereign agents (BDI cognitive cores, the AGInt
Perceive→Orient→Decide→Act loop, strategic evolution, an improvement journal).
**Borrowed back into ezAGI v1.0.0:**
- resilient cloud-first provider resolution with local Ollama failsafe
  (mindX `llm/llm_factory.py` → ezAGI `webmind/chatter.py:resolve_chatter`)
- "all logs are memories" (mindX `agents/memory_agent.py` → ezAGI memory-routed logging)
- confidence-scored belief validation (mindX `belief_system.py` → SocraticReasoning
  LLM-judged validation with confidence)
- stuck-loop guarding of the autonomous reasoning loop (mindX AGInt → OpenMind)

### The wider family
- [openmindx/OpenMind](https://github.com/openmindx/OpenMind) — the native desktop
  AI workspace for local models (Tauri 2, boardroom consensus, dojo evaluation);
  the desktop evolution of ezAGI's `openmind`
- [openmindx/agi](https://github.com/openmindx/agi) — open AGI components
- [llamagi/lmagi](https://github.com/llamagi/lmagi) — the Ollama/llama departure point
- [autoGLM/easyAGI](https://github.com/autoGLM/easyAGI) — the original
  non-integrated module framework
- [Professor-Codephreak](https://github.com/Professor-Codephreak) ·
  [pythaiml](https://github.com/pythaiml) · [autoGLM](https://github.com/autoGLM) —
  the author and organizations

---

## Part 2 — the full workflow

The complete path of a thought through ezAGI v1.0.0, with the file for each stage:

```
                         ┌───────────────────────────────┐
   user input ──────────►│ ezAGI.py — the ezAGI console  │
                         │  chat = production interaction │
                         │  reasoning = internal trace    │
                         └──────────────┬────────────────┘
                                        │
                         ┌──────────────▼────────────────┐
                         │ automind/openmind.py OpenMind │
                         │  keys (webmind/api.py .env)   │
                         │  resolve_chatter cloud-first  │
                         │  autonomous reasoning_loop    │
                         └──────────────┬────────────────┘
                                        │
              ┌─────────────────────────▼─────────────────────────┐
              │ automind/automind.py FundamentalAGI → agi.py AGI  │
              └─────────────────────────┬─────────────────────────┘
                                        │
              ┌─────────────────────────▼─────────────────────────┐
              │ automind/SocraticReasoning.py                     │
              │  add_premise → generate premises → challenge      │
              │  → draw_conclusion (streamed to the chat window)  │
              │  → validate: truth tables (automind/logic.py)     │
              │    for propositional statements, LLM judgment     │
              │    with confidence for natural language           │
              └─────────────────────────┬─────────────────────────┘
                                        │
              ┌─────────────────────────▼─────────────────────────┐
              │ memory/memory.py — all logs are memories          │
              │  stm/{t}memory.json   conversation memory         │
              │  logs/premises.json   logs/thoughts.json          │
              │  logs/truth.json      logs/notpremise.json        │
              │  truth/               validated truths            │
              └─────────────────────────┬─────────────────────────┘
                                        │
              ┌─────────────────────────▼─────────────────────────┐
              │ simplemind/coach.py Coach                         │
              │  loads accumulated stm memories → trains          │
              │  simplemind/SimpleMind.py (JAX MLP) → saved model │
              │  learning as long-term memory                     │
              └─────────────────────────┬─────────────────────────┘
                                        │
              ┌─────────────────────────▼─────────────────────────┐
              │ mastermind/controller.py MASTERMIND               │
              │  orchestrates agency from ./mindx/agency          │
              │  mastermind/SimpleCoder.py generates agents       │
              │  automindx/ BDI · THOT reasoning styles ·         │
              │  self_healing keeps the system alive              │
              └───────────────────────────────────────────────────┘
```

Step by step:

1. **Perceive** — the console (`ezAGI.py`) takes input; the chat tab is the
   production interaction from ezAGI, the reasoning tab is the internal trace.
2. **Resolve** — `OpenMind` resolves a provider from stored keys cloud-first
   (openai → groq → together → anthropic → ollama-cloud) with the local Ollama
   daemon as failsafe (`webmind/chatter.py`).
3. **Reason** — `FundamentalAGI` adds the input as a premise; `SocraticReasoning`
   generates supporting premises, challenges weak ones, and draws a conclusion,
   streaming tokens to the chat window and trace events (premise / challenge /
   validation / conclusion) to the reasoning panel.
4. **Validate** — propositional statements go through `LogicTables` truth tables
   (a safe AST evaluator, never `eval`); natural language is judged VALID/INVALID
   by the LLM; every conclusion carries a confidence (1.0 truth-table, 0.9 judged
   valid, 0.4 judged invalid, 0.3 unvalidated), and only validated conclusions are
   saved as truth.
5. **Remember** — every dialog is stored to short-term memory, every conclusion to
   the thoughts/truth logs: all logs are memories.
6. **Learn** — `coach` featurizes accumulated stm memories and trains `SimpleMind`,
   the minimalist JAX neural network — the trained weights are the system's
   long-term learned memory.
7. **Act** — `MASTERMIND` orchestrates agents from `./mindx/agency`; `SimpleCoder`
   writes them; `automindx` provides BDI practical reasoning, THOT reasoning styles
   and self-healing.
8. **Loop** — the autonomous `reasoning_loop` keeps reasoning about the latest
   input (at most three passes per prompt, idling when there is nothing new),
   so ezAGI thinks between questions, not only when asked.
