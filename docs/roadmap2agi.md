# Roadmap to AGI — from the ezAGI console

(c) 2024 Gregory L. Magnusson · MIT

**Read this first.** ezAGI is *not* an AGI, and no roadmap turns an LLM console
into one. AGI is the integration of many hard capabilities — transfer learning,
world models, memory, reasoning, planning, curiosity, multimodality, and (the
bottleneck) alignment — and the timeline for it is genuinely uncertain. See the
[AGI background in agi.md](agi.md#background-what-agi-means) for that framing.

What this document *is*: a concrete, repo-grounded plan of engineering steps
that move ezAGI from "reasoning over an LLM" toward a more general, more
autonomous reasoning system. Every phase references code that already exists or
a specific, buildable extension of it. Aspirational items are labelled as such.

---

## Phase 0 — Where we are today (shipped)

The console is a transparent reasoning-over-LLM skeleton:

- **Reasoning:** `SocraticReasoning` — premise → conclusion → **LLM-judged
  validation** with a retry loop; validated results become higher-confidence
  *truths*, unvalidated ones stay lower-confidence *beliefs*
  ([SocraticReasoning.md](SocraticReasoning.md)).
- **Providers:** `resolve_chatter` picks a `chatter` cloud-first with local
  Ollama failsafe; streaming + usage accounting ([agi.md](agi.md#the-chatter-webmindchatterpy)).
- **Memory:** append-only logs-as-memories + short-term memory ([memory.md](memory.md)).
- **Autonomy (seed):** `OpenMind.reasoning_loop` re-reasons a prompt on its own
  with a three-pass stop-guard ([openmind.md](openmind.md)).
- **Observability:** a live reasoning-trace panel separate from chat output.

**Known gap that shapes the whole roadmap:** the `automindx/` package already
contains a rich set of reasoning modules — `abduction`, `deductive`,
`nonmonotonic`, `fuzzy`, `epistemic`, `prediction`, `bdi`, `make_decision`,
`self_healing`, `autonomize` — but **none of them is imported by the console
path** (`ezAGI.py` → `openmind` → `automind/agi.py`). The nearest-term wins are
about *connecting what already exists*, not inventing from scratch.

---

## Phase 1 — Deepen reasoning (wire in `automindx`)

Goal: move from a single Socratic strategy to a **portfolio of reasoning modes**,
selected per problem.

- Introduce a reasoning-strategy interface and route `draw_conclusion` through a
  selector that can call `deductive`, `abduction` (best-explanation),
  `nonmonotonic` (defeasible), and `fuzzy` (graded truth) alongside the current
  Socratic flow.
- Add `epistemic` tracking (what the system knows / believes / is uncertain
  about) so confidence is first-class, not just the truth/belief split.
- Surface `prediction` so the system can state expectations and later check them.

Why it matters for generality: a single reasoning template overfits to one
problem shape; a selectable portfolio is a step toward *domain-transfer* reasoning.

**Status:** modules exist, unwired — this phase is integration work.

---

## Phase 2 — Memory that informs reasoning (retrieval)

Goal: turn the append-only JSON logs into **retrieval-augmented memory** so past
truths shape new conclusions.

- Add embeddings + vector recall over `memory/` (truths, thoughts, STM) and feed
  the top-k relevant memories into premise construction (RAG over the agent's
  own history).
- Deduplicate and consolidate truths over time (belief revision), rather than
  only appending.

Why it matters: continual, cumulative learning across sessions — a prerequisite
for anything "general" — instead of restarting cold each turn.

**Status:** aspirational; today memory is written but not retrieved into reasoning.

---

## Phase 3 — Tools & action (grounding)

Goal: let the reasoner *act*, not only talk.

- Add tool/function-calling through the `chatter` layer (web search, code
  execution, calculators, file/RAG lookups) with results fed back as premises.
- Treat tool outputs as observations, closing a perceive → reason → act → observe
  loop.

Why it matters: grounding predictions in real feedback is the seed of a **world
model**; ungrounded LLM reasoning drifts.

**Status:** aspirational; no tool layer today.

---

## Phase 4 — Autonomy & self-improvement

Goal: promote the seed autonomous loop into a genuine agent.

- Wire `bdi` (Belief–Desire–Intention) so the loop pursues intentions and
  sub-goals rather than re-reasoning one prompt.
- Wire `self_healing` and `autonomize` for error recovery and self-directed
  operation; keep an improvement journal of what changed and why.
- Preserve the existing three-pass stop-guard as the minimum safety brake and
  extend it with explicit budgets and human check-ins.

Why it matters: sub-goal formation and self-correction are core to the "general"
in AGI — and also where risk concentrates, hence the guards.

**Status:** `bdi`/`self_healing`/`autonomize` exist, unwired.

---

## Phase 5 — Multi-agent & multimodality

Goal: beyond a single text reasoner.

- MASTERMIND-style orchestration of multiple specialized agents (this is the
  direction the project lineage already points — see [lineage.md](lineage.md);
  the successor system **mindX** explores multi-agent BDI, vector memory, and
  governance).
- Multimodal `chatter` (vision/audio) so perception isn't text-only.

**Status:** aspirational for ezAGI; partially realized downstream in the lineage.

---

## Cross-cutting tracks (every phase, not a phase)

- **Safety & alignment.** The hard problem, and it does not wait for a later
  phase. Concretely for ezAGI: keep validation/confidence honest, gate
  side-effectful tools (Phase 3) behind explicit permission, bound autonomy
  (Phase 4) with budgets and human oversight, and never let capability outrun the
  guardrails. Alignment here means *modest, local* safety — not a solution to the
  research alignment problem.
- **Evaluation.** Add a benchmark/test harness that measures reasoning quality
  across many problem types (planning, abstraction, consistency), so "progress"
  is demonstrated, not asserted.
- **Observability.** Extend the reasoning-trace panel as capabilities grow — an
  inspectable system is a safer and more debuggable one.

---

## What this roadmap does *not* claim

- It does not claim ezAGI will "become AGI" by completing these phases.
- It does not put dates on AGI; expert forecasts disagree widely and this doc
  intentionally avoids false precision.
- Each phase is an engineering increment with clear, testable value on its own,
  independent of the AGI framing.

## See also

- [agi.md](agi.md) — the AGI layer and the AGI-concepts background.
- [openmind.md](openmind.md) — the console that drives reasoning.
- [SocraticReasoning.md](SocraticReasoning.md), [memory.md](memory.md), [lineage.md](lineage.md).
