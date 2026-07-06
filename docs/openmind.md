# openmind.py — the reasoning core of easyAGI / ezAGI

`openmind.py` (c) 2024 Gregory L. Magnusson · MIT

`OpenMind` is the module that binds the **user interface** (`ezAGI.py`, the
NiceGUI console) to the **AGI reasoning stack** (`automind/`) and the **LLM
provider layer** (`webmind/`). It owns application state — API keys, the active
provider/model, sampling controls, token accounting, and the reasoning-trace
feed — and it runs two cooperating asyncio loops: one that answers user input
and one that reasons continuously on its own.

> Naming: `ezAGI.py` is the canonical entry point; `easyAGI.py` is a thin
> `runpy` shim that launches the same console (the project was originally named
> *easyAGI*, hence the name still appears in the UI title and this module's
> comments). See [the AGI layer](agi.md) for the class stack below `OpenMind`.

---

## Where OpenMind sits

```
ezAGI.py  (NiceGUI console: tabs, footer input, header controls)
   │  holds a single shared OpenMind instance
   ▼
OpenMind  (automind/openmind.py)  ── this document
   │  owns state + two async loops; talks to:
   ├──────────────► FundamentalAGI ─► AGI ─► SocraticReasoning   (automind/*)  the reasoning stack
   │                                    └─► chatter               (webmind/chatter.py)  LLM providers
   ├──────────────► APIManager        (webmind/api.py)            key storage (.env)
   ├──────────────► OllamaHandler     (webmind/ollama_handler.py) local / cloud Ollama
   └──────────────► memory.*          (memory/memory.py)          STM + logs-as-memories
```

A single `OpenMind` is created once at startup in `ezAGI.py` and shared across
all page visits — there is one internal reasoning loop for the whole app, not
one per browser client.

---

## The AGI stack, and the role of AGI in easyAGI

`OpenMind` never calls an LLM directly. It delegates all reasoning to an **AGI
instance**, which is where "easyAGI" actually *thinks*. Three classes matter,
each documented in full in [agi.md](agi.md):

- **`FundamentalAGI`** (`automind/automind.py`) — the object `OpenMind` holds as
  `self.agi_instance`. It is a thin wrapper that owns an `AGI` (`self.agi`) and
  exposes `get_conclusion_from_agi(prompt)`: it adds the prompt to the reasoner
  as a premise and returns a drawn conclusion. This is the single method
  `OpenMind` calls to answer anything.
- **`AGI`** (`automind/agi.py`) — holds the `chatter` (the LLM provider) and a
  `SocraticReasoning` engine (`self.reasoning`). It is the seat of the AGI: the
  reasoner and the model live here together.
- **`EasyAGI`** (`automind/agi.py`) — the original **terminal** front end for
  the same `AGI`. Its `main_loop()` reads from stdin (`perceive_environment`),
  runs `learn_from_data` → `make_decisions`, and prints the result. `OpenMind`
  is the web-console successor to `EasyAGI`: both drive the identical `AGI`
  reasoning core, one over NiceGUI, the other over a prompt. This is "the role
  of AGI in easyAGI" — `AGI` is the shared brain; `EasyAGI` (CLI) and
  `OpenMind`/`ezAGI.py` (console) are two skins over it.

### What one "turn" actually does

When `OpenMind` asks for a conclusion, `SocraticReasoning.draw_conclusion()`
makes **several** LLM calls, not one:

1. (optional) a supporting-premise generation,
2. the **streamed conclusion** (`generate_response_with_tokens`),
3. a **validation judgment** (`generate_response` with a verdict prompt), and
4. if unvalidated, a new premise is generated and the loop retries.

This multi-call shape is why token accounting reads a *cumulative delta* rather
than the last call — see [Token accounting](#token-accounting) below.

---

## OpenMind state (`__init__`)

| Field | Purpose |
|---|---|
| `api_manager` | `APIManager` — reads/writes provider keys in `.env`. |
| `agi_instance` | the active `FundamentalAGI`, or `None` until a provider resolves. |
| `message_container` | the chat tab's NiceGUI column (production output). |
| `ollama_handler` | local Ollama endpoint probe/handler. |
| `internal_queue` | user inputs handed from the UI to `main_loop`. |
| `prompt` | the current thing being reasoned about. |
| `keys_container`, `log` | UI containers for the API-keys and logs tabs. |
| `current_provider`, `current_model` | active selection, shown in the header. |
| `temperature`, `max_tokens` | sampling controls (`None` = provider default). |
| `session_tokens` | `{last_in, last_out, total}` shown in the header. |
| `_usage_baseline` | snapshot of the chatter's `cumulative_usage` after the last accounted turn. |
| `_live_out` | live output-token estimate during interactive streaming (`None` when idle); kept out of `session_tokens` so the header total stays coherent. |
| `trace_queue`, `reasoning_state` | reasoning-trace event feed and `idle`/`thinking` state. |
| `_last_reasoned_prompt`, `_same_prompt_count` | guard so the autonomous loop stops re-reasoning the same prompt after three passes. |

---

## Lifecycle: the two loops

`ezAGI.py` schedules `main_loop()` once at startup
(`app.on_startup(lambda: asyncio.create_task(openmind.main_loop()))`).

### `main_loop()`
Records the running event loop (`_ui_loop`, needed for thread-safe callbacks
from the executor), starts the autonomous `reasoning_loop()` as a background
task, then blocks on `internal_queue`. Each dequeued prompt becomes `self.prompt`
and resets the autonomous guard. `'exit'` breaks the loop.

### `reasoning_loop()` (autonomous)
Runs forever: if no provider is available it waits and retries; if there is a
prompt it hasn't already reasoned to rest (fewer than three identical passes),
it sets `reasoning_state = "thinking"`, calls `get_conclusion_from_agi`, routes
the conclusion to the reasoning-trace panel and thought logs, accounts token
usage, and persists the internal reasoning. This is the "thinking on its own"
behavior — distinct from the production chat.

### `send_message(question)` (interactive, called from the UI)
The production path, with **live streaming**:

1. Renders the user's `query` bubble and an empty `ezAGI` response bubble + spinner.
2. Creates an `asyncio.Queue` and installs `on_token` / `on_event` callbacks on
   the reasoner. `on_token` forwards each streamed chunk to the queue via
   `loop.call_soon_threadsafe` (the reasoner runs in an executor thread).
3. Runs `agi_instance.get_conclusion_from_agi` in a thread executor while the
   coroutine drains the queue, re-rendering the partial answer roughly every
   0.1 s. A `STREAM_RESET` sentinel (pushed when a conclusion attempt restarts)
   clears the accumulated text so a retry doesn't concatenate onto the old one.
4. On completion, renders the final conclusion, calls `_account_usage`, scrolls
   to the bottom, and stores the dialog in STM + conversation memory.
5. `finally` clears the callbacks, resets `reasoning_state`, and removes the spinner.

### `get_conclusion_from_agi(prompt)`
Async wrapper that runs the (blocking) `FundamentalAGI.get_conclusion_from_agi`
in a thread executor so the event loop is never blocked; returns a guidance
string if no provider is initialized.

---

## Providers, models, and sampling

- `available_providers()` / `models_for(provider)` — enumerate what keys/daemons
  are usable and their model lists (`KNOWN_MODELS`, live Ollama tags).
- `select_model(provider, model)` — switch the active provider/model, rebuilding
  the chatter through `resolve_chatter`.
- `initialize_agi()` — resolve a chatter **cloud-first with local Ollama as
  failsafe**, wrap it in `FundamentalAGI`, apply sampling, and **reset
  `_usage_baseline`** (a fresh chatter starts its cumulative usage at zero).
- `set_sampling` / `_apply_sampling` — push `temperature` / `max_tokens` onto the
  chatter; `None` leaves a control at the provider default.

Keys are managed with `add_api_key`, `list_api_keys`, `delete_api_key`, and
`use_api_key`, all backed by `APIManager` (stored in `.env`).

---

## Token accounting

The header shows `in / out` for the **last turn** and a **session** total. Because
a turn spans several LLM calls, correct accounting can't read the chatter's
`last_usage` (that holds only the final sub-call — historically this made the
counter show, e.g., a tiny `460/135` validation call as if it were the whole
turn).

Instead:

- `BaseChatter` (`webmind/chatter.py`) keeps a **monotonic** `cumulative_usage`
  (`{input_tokens, output_tokens}`), folded in after **every** call via
  `_fold_usage()` from both `generate_response_async` and the streaming
  `generate_response_with_tokens`.
- `_account_usage(response_text)` reads the **delta** of `cumulative_usage` since
  `_usage_baseline`, records that as the turn's `last_in`/`last_out`, adds it to
  the session `total`, and advances the baseline. If a provider reports no usage
  (e.g. local Ollama), it falls back to a length estimate (`len(text) // 4`).

### Live estimate while streaming

While a turn streams, `send_message` writes a running output estimate
(`len(streamed) // 4`) to a **separate** field, `self._live_out` (not into
`session_tokens`), and clears it to `None` when the turn finishes. Keeping the
estimate apart from the committed counters is what makes the header coherent:

- the interactive display shows the live estimate as the turn's `out` (marked
  with `≈` and a pulse) while `in` reads `0` — the provider has not reported
  input yet;
- the displayed session total is `session_tokens["total"] + (_live_out or 0)`,
  so the cumulative figure is **never smaller than the turn in progress**
  (the earlier bug let a long answer's `out` exceed the shown `session`);
- the autonomous `reasoning_loop` never sets `_live_out`, so its turns display
  the committed numbers with no double-counting.

When the turn completes, `_account_usage` folds the exact per-turn delta into
`session_tokens` and `_live_out` is cleared, so the header snaps from estimate
to the reconciled totals.

---

## Reasoning trace and "logs are memories"

- `_trace(event_type, payload)` queues a timestamped event (thread-safe via
  `_ui_loop`) onto `trace_queue`; `ezAGI.py`'s reasoning tab consumes it to show
  the live SocraticReasoning trace, kept strictly separate from the chat tab.
- Conclusions and non-premises are written to memory logs
  (`./memory/logs/thoughts.json`, `notpremise.json`), and dialog turns to
  `./memory/stm/{timestamp}memory.json` — in this project **every log is a
  memory**.
- `read_log_file(path)` backs the logs tab. A missing or empty log renders as
  `(no entries yet)` rather than an error, since files like `errorlogs.txt` are
  created lazily the first time the reasoner writes to them.

---

## UI helpers

- `run_javascript_with_retry(script, retries, timeout)` — awaits
  `ui.run_javascript` directly (it returns an `AwaitableResponse`, which is
  awaitable but **not** a coroutine, so it must not be wrapped in
  `asyncio.create_task`), retrying on `TimeoutError`.
- `_handle_task_result(task)` — done-callback that surfaces exceptions from the
  background `reasoning_loop` task without treating cancellation as an error.

---

## Dependencies

`os`, `time`, `datetime`, `asyncio`, `logging`, `ujson`, `httpx`, `nicegui`;
and internally `memory.memory`, `automind.automind` (`FundamentalAGI`),
`webmind.chatter`, `webmind.api`, `webmind.ollama_handler`.

## See also

- [agi.md](agi.md) — the `AGI` / `FundamentalAGI` / `EasyAGI` stack in full.
- [SocraticReasoning.md](SocraticReasoning.md) — the reasoning engine.
- [reasoning.md](reasoning.md), [logic.md](logic.md), [memory.md](memory.md).
