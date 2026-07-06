# The AGI layer — `agi.py` and `automind.py`

(c) 2024 Gregory L. Magnusson · MIT

This document explains the reasoning core that sits below
[`OpenMind`](openmind.md): the `AGI` class, the `FundamentalAGI` wrapper, and
the `EasyAGI` terminal front end — and how "AGI" is the shared brain that both
easyAGI (CLI) and the ezAGI console reason with.

---

## The three classes at a glance

```
FundamentalAGI (automind/automind.py)   ← OpenMind holds this as agi_instance
   └── agi : AGI (automind/agi.py)       ← the reasoning core
          ├── chatter   (webmind/chatter.py)      the LLM provider
          └── reasoning : SocraticReasoning       premise → conclusion → validation

EasyAGI (automind/agi.py)                ← standalone terminal front end
   └── agi : AGI                          ← the same core, driven from stdin
```

`AGI` is the seat of intelligence: it pairs an LLM `chatter` with a
`SocraticReasoning` engine. Everything else is a way to *feed input into* an
`AGI` and *get a conclusion out* — the web console (`OpenMind`), the historic
terminal (`EasyAGI`), and the wrapper the console uses (`FundamentalAGI`).

---

## `AGI` (automind/agi.py)

```python
class AGI:
    def __init__(self, chatter):
        self.chatter = chatter
        self.reasoning = SocraticReasoning(self.chatter)
```

The core. Constructed with a resolved `chatter` and builds its own
`SocraticReasoning` over that same chatter, so both the model and the reasoner
share one provider.

- **`learn_from_data(data)` → `(proposition_p, proposition_q)`**
  Treats the input `data` as the primary proposition `p`, and asks the chatter
  for one concise **supporting contextual premise** `q`
  (`"State one concise factual premise that provides context for: …"`). If that
  call fails, `q` falls back to the input itself. This is the "learn" step: the
  model enriches raw input with a contextual premise before reasoning.

- **`make_decisions(proposition_p, proposition_q)` → conclusion**
  Adds both propositions to the reasoner as premises and calls
  `draw_conclusion()`, returning `reasoning.logical_conclusion`. This is the
  "decide" step: Socratic reasoning turns premises into a validated conclusion.

## `EasyAGI` (automind/agi.py) — the terminal front end

```python
class EasyAGI:
    def __init__(self):
        self.api_manager = APIManager()
        self.api_manager.manage_api_keys()
        chatter = resolve_chatter(self.api_manager)
        if chatter is None:
            raise RuntimeError("no chatter available: add an API key or start Ollama")
        self.agi = AGI(chatter)
        self.initialize_memory()
```

`EasyAGI` is the **original command-line** application and the namesake of the
project. It resolves a chatter from stored keys, wraps it in an `AGI`, and runs
a perceive → learn → decide → respond loop:

- `main_loop()` — read input, then `learn_from_data` → `make_decisions` →
  `communicate_response`, storing each exchange in short-term memory.
- `perceive_environment()` — input from an empty stdin prompt (the "environment").
- `communicate_response(decision)` — log and print the conclusion.

**Role of AGI in easyAGI:** `EasyAGI` does not think on its own — it is a thin
harness that hands input to an `AGI` and prints what the `AGI` concludes. The
same `AGI` core is what the modern ezAGI console drives through
[`OpenMind`](openmind.md); `EasyAGI` is simply the terminal skin, `OpenMind`/
`ezAGI.py` the NiceGUI skin, over one shared brain.

---

## `FundamentalAGI` (automind/automind.py) — the wrapper OpenMind uses

```python
class FundamentalAGI:
    def __init__(self, chatter):
        self.agi = self.initialize_agi(chatter)   # AGI(chatter)
        self.initialize_memory()                  # create_memory_folders()

    def get_conclusion_from_agi(self, prompt):
        self.agi.reasoning.add_premise(prompt)
        conclusion = self.agi.reasoning.draw_conclusion()
        return conclusion
```

`FundamentalAGI` is the object the console holds as `agi_instance`. It exists to
give `OpenMind` **one blocking call** — `get_conclusion_from_agi(prompt)` — that
adds the prompt as a premise and returns a drawn conclusion, plus memory
initialization. `OpenMind` runs this in a thread executor and streams tokens out
of the reasoner via callbacks (see [openmind.md](openmind.md#send_messagequestion-interactive-called-from-the-ui)).

Note the two reasoning entry points differ slightly:
- `AGI.make_decisions` adds **two** premises (`p` and the generated `q`).
- `FundamentalAGI.get_conclusion_from_agi` adds **just the prompt** as a premise.
Both end in `SocraticReasoning.draw_conclusion()`.

---

## One turn = several LLM calls

Whichever entry point is used, `SocraticReasoning.draw_conclusion()` issues
multiple calls to the `chatter` per turn:

1. optional supporting-premise / new-premise generation (`generate_response`),
2. the streamed **conclusion** (`generate_response_with_tokens`),
3. a **validation judgment** (`generate_response`), and
4. a retry loop with a fresh premise if the conclusion is not validated.

Validated conclusions are stored as truths (higher confidence); unvalidated ones
are kept as lower-confidence beliefs. This multi-call structure is what the
[token accounting](openmind.md#token-accounting) in `OpenMind` measures via the
chatter's cumulative-usage delta.

---

## The chatter (webmind/chatter.py)

`AGI` is provider-agnostic: `resolve_chatter(api_manager)` picks a provider
**cloud-first with local Ollama as failsafe** (openai → groq → together →
anthropic → ollama-cloud → ollama) and returns a `BaseChatter` subclass. All
subclasses share sync `generate_response` / streaming
`generate_response_with_tokens`, per-provider usage capture (`last_usage`), and
the monotonic `cumulative_usage` counter used for token accounting.

## See also

- [openmind.md](openmind.md) — how the console drives this AGI layer.
- [SocraticReasoning.md](SocraticReasoning.md) — the reasoning engine internals.
- [lineage.md](lineage.md) — how AGI/AUTOMINDx/MASTERMIND fit the project lineage.
