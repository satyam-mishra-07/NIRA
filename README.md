# NIRA — Neural Intelligence & Reasoning Architecture

> **A modular, Python-based AI companion built around cognitive science principles.**
> This is a passion project — actively under development. Expect rough edges, evolving architecture, and occasional moments of genuine magic.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)](https://python.org)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)]()
[![GitHub](https://img.shields.io/badge/GitHub-satyam--mishra--07%2FNIRA-black?style=flat-square&logo=github)](https://github.com/satyam-mishra-07/NIRA)

---

## What is NIRA?

NIRA is not a chatbot wrapper. It's an attempt to build an AI assistant the right way — with real separation of concerns, a multi-layered memory system, dual-model orchestration, and a personality engine that keeps it feeling consistent regardless of which underlying model is responding.

The core idea: intelligence shouldn't live in a single prompt. It should emerge from a well-orchestrated system of specialized components — mood analysis, habit learning, intent classification, memory layers, and model routing — all working together.

Built by [Satyam Mishra](https://github.com/satyam-mishra-07) as a personal exploration of agentic AI systems architecture.

---

## Features

- **Dual-model hybrid cognition** — Routes reasoning tasks to DeepSeek-R1 and conversational tasks to Qwen, transparently
- **8-layer memory architecture** — Short-term, working, emotional, habit, summary, profile, conversation, and behavioral memory
- **CognitionAssessor** — Multi-dimensional intent classification (what, how hard, what tools, how long)
- **MoodAnalyzer** — Detects emotional state from input and calibrates tone accordingly
- **HabitObserver** — Learns behavioral patterns over time through a confidence-weighted reinforcement loop
- **PersonalityEngine** — Keeps NIRA's identity stable across model switches and long sessions; includes immutable identity core and homeostasis
- **Behavioral Alignment System** — Real-time behavioral signal extraction, contextual reinforcement, contradiction detection, and bounded adaptation
- **Self Reflection Cognition** — Post-response evaluation across 9 dimensions; advisory-only reflection that subtly influences behaviour without rewriting identity
- **Hinglish support** — Handles English, Hindi, and mixed Hinglish naturally
- **Typed signal architecture** — `CognitionSignal` as a typed contract between cognition and routing; no string parsing
- **Clean dependency injection** — Every component is swappable and testable in isolation

### Under Active Development 🚧

- **Tool integrations** — Browser/web search, file system operations, terminal execution, code runner (scaffolded, not yet wired)
- **Voice pipeline** — STT (Whisper) + TTS (Piper) + wake word detection
- **Desktop UI** — PyQt6-based interface with avatar/expression system
- **Async architecture** — Non-blocking model calls and parallel tool execution
- **Vector memory** — Semantic retrieval via FAISS/ChromaDB (ChromaStore scaffolded)
- **Agentic loop** — Multi-step tool chaining with goal state in WorkingMemory

---

## Architecture Overview

NIRA separates every cognitive concern into its own package. A change in routing doesn't break memory. A new model doesn't break personality. Each layer communicates via typed signals.

```
NIRA/
├── core/               # Orchestration spine
│   ├── cognition/      # CognitiveLoop — the 16-stage pipeline
│   ├── orchestration/  # ExecutionRouter, ToolPlanner, OrchestrationRouter
│   ├── runtime/        # RuntimeLifecycle, EventBus, ContextManager
│   └── state/          # RuntimeState, WorkspaceState
│
├── cognition/          # Intelligence layer
│   ├── intent/         # CognitionAssessor, CognitionSignal, IntentPredictor
│   ├── mood/           # MoodAnalyzer, MoodStateTracker, EmotionalMemory bridge
│   ├── habits/         # HabitObserver, PatternDetector, ConfidenceEngine, HabitStore
│   ├── context/        # ActivityContext, UserContext, WorkspaceContext
│   ├── behavioral/     # BehavioralSignalExtractor, BehavioralMemory, PersonalityStabilizer, IdentityCore
│   └── reflection/     # SelfReflectionEngine, ReflectionMemory, MemoryReflection, ConversationSummarizer
│
├── memory/             # 8-layer memory system
│   ├── short_term/     # Sliding window conversation buffer (RAM only)
│   ├── working/        # Active task scratchpad (RAM only)
│   ├── emotional/      # Affective history (disk, decay-based)
│   ├── habits/         # Behavioral patterns with confidence scores (disk)
│   ├── summaries/      # Compressed long-term context (disk)
│   ├── profile/        # Persistent user profile (disk, permanent)
│   ├── conversation/   # Append-only turn log with auto-pruning (disk)
│   ├── behavioral/     # Behavioral preferences + reflection observations (disk, JSON)
│   └── embeddings/     # Vector store scaffold (ChromaDB, not yet active)
│
├── personality/        # PersonalityEngine — identity anchor
│   └── templates/      # casual.json, coding.json, productivity.json
│
├── providers/          # LLM and I/O abstraction
│   ├── llm/            # ModelRouter, ConversationModel (Qwen), ReasoningModel (DeepSeek)
│   ├── stt/            # Whisper STT (scaffolded)
│   ├── tts/            # Piper TTS (scaffolded)
│   └── embeddings/     # BGE embedding provider (scaffolded)
│
├── security/           # InputValidator, Guardrails, Sandbox, Permissions
├── agents/             # Future agentic extension points (scaffolded)
├── tools/              # ToolPlanner targets — browser, filesystem, terminal, coding
├── voice/              # Voice pipeline — recorder, VAD, wake word (scaffolded)
├── ui/                 # Desktop interface — chat widget, avatar (scaffolded)
├── config/             # settings.py, constants.py, prompts.py
├── scripts/            # Dev/test utilities
└── tests/              # Test suite
```

---

## Cognitive Pipeline

Every user message flows through a deterministic pipeline:

```
User Input
    │
    ▼
[1]  InputValidator + Guardrails     → Sanitize, check safety
    │
    ▼
[2]  MoodAnalyzer                    → Detect emotional state → MoodSignal
    │
    ▼
[3]  HabitObserver                   → Detect behavioral patterns → HabitStore
    │
    ▼
[4]  CognitionAssessor               → Assess 4 dimensions → CognitionSignal
    │   (intent, reasoning depth, tool need, response depth)
    ▼
[5]  IntentPredictor                 → Enrich with working memory context
    │
    ▼
[6]  ExecutionRouter                 → Map signal → RouteDecision
    │   (which model track, whether to activate tools)
    ▼
[7]  ModelRouter                     → Select actual LLM endpoint
    │   (DeepSeek-R1 for reasoning, Qwen for conversation)
    ▼
[8]  ToolPlanner (if needed)         → Execute tools, package results as context
    │
    ▼
[9]  PersonalityEngine               → Assemble system prompt + inject memory layers
    │   (identity core + behavioral context + ShortTermMemory + WorkingMemory)
    ▼
[10] Model API Call                  → Generate response (streaming or full)
    │
    ▼
[11] BehavioralSignalExtractor (deferred) → Extract user reaction from next input
    │   (sentiment, repetition, verbosity match, emotional appropriateness)
    ▼
[12] BehavioralMemory                → Update preference confidence, detect contradictions
    │   (temporary session layer + persistent long-term layer)
    ▼
[13] PersonalityStabilizer (periodic)→ Compute adjustments, apply session modifiers,
    │   promote confident preferences to persistent, record meta-stability snapshot
    ▼
[14] SelfReflectionEngine (periodic) → 9-dimension post-response evaluation
    │   (coherence, awkwardness, drift, grounding, verbosity match, etc.)
    ▼
[15] ReflectionMemory + Decay        → Store evaluation; reflection influence decays
    │   3x faster than behavioral memory; advisory-only behavioral hints
    ▼
[16] Memory Storage + Decay          → ConversationStore + EmotionalMemory + HabitStore
         └── MemoryReflection        → Summarize if threshold reached
```

Phases 11–15 run at configurable intervals, not every turn. Behavioral extraction is deferred — the system evaluates user reactions to the *previous* response when processing the next input. Reflection is advisory only and never directly modifies identity core traits or persistent modifiers without repeated confirmation.

---

## Behavioral Alignment System

NIRA's behavioral layer enables real-time adaptation to user interaction patterns without fine-tuning or prompt rewriting. It operates as a closed-loop feedback system running alongside the core cognitive pipeline.

### Behavioral Signal Extraction

Each user message is analyzed as a reaction to NIRA's previous response. `BehavioralSignalExtractor` computes:

- **User sentiment** — Positive/negative signal from word-level sentiment analysis
- **Response coherence** — Lexical diversity as a proxy for response quality
- **Repetition score** — Lexical overlap between user input and previous response
- **Verbosity match** — Ratio of response length to input length
- **Humor appropriateness** — Whether humor is present and whether the mood supports it
- **Emotional appropriateness** — Whether the response matches the user's emotional state

Signals below a configurable strength threshold (`0.1`) are ignored to avoid noise amplification.

### Contextual Reinforcement Memory

`BehavioralMemory` maintains a set of `ContextualPreference` entries keyed by mood, task, and time period. Each preference tracks:

- **Confidence** — Ranges 0–0.9, updated via confidence-weighted reinforcement
- **Observation count** — Number of times this preference was reinforced
- **Context key** — Composite of mood + task + time period for situational specificity

Preferences become active only after 3+ observations and confidence ≥ 0.5.

### Temporary vs Persistent Adaptation

Adaptation is split into two layers:

- **Session modifiers** — Applied immediately, reset on session boundary. Handles within-conversation tuning (e.g., "keep it brief" → lower verbosity for the session).
- **Persistent modifiers** — Only updated when a preference has 10+ observations and confidence ≥ 0.7. Survives session resets. Represents genuine user preferences confirmed across multiple interactions.

This split prevents a single bad conversation from reshaping NIRA's identity.

### Contradiction Detection

When conflicting preferences appear in sequence (e.g., "be more playful" followed by "stop joking"), `BehavioralMemory` detects the contradiction and reduces the reinforcement delta by 70%. This prevents oscillation between opposite behavioral states and keeps adaptation stable.

Contradiction pairs are configurable: `(concise, detailed)`, `(playful, supportive)`, `(playful, clear)`.

### Homeostasis

All modifiers — both session and persistent — drift gradually toward zero at a configurable rate (`HOMEOSTASIS_RATE = 0.005` per prompt). Session modifiers drift twice as fast. This means adaptation requires active reinforcement: modifiers that are not repeatedly confirmed naturally decay, preventing long-term drift accumulation.

---

## Self Reflection Cognition

After generating a response, `SelfReflectionEngine` performs a post-hoc evaluation across 9 dimensions:

| Dimension | What it measures | Purpose |
|---|---|---|
| Coherence | Lexical diversity, sentence structure | Avoids repetitive or garbled output |
| Emotional appropriateness | Empathy/playfulness alignment with mood | Keeps tone context-sensitive |
| Personality drift | Formal/poetic language that deviates from identity | Prevents style mutation |
| Awkwardness | Filler words, hedging | Maintains natural conversation flow |
| Repetitiveness | Lexical overlap with recent history | Avoids repeating the same content |
| Verbosity match | Word count relative to expected depth | Matches response length to query depth |
| Humor appropriateness | Humor presence vs mood appropriateness | Avoids inappropriate levity |
| Grounding | Ungrounded claims ("I searched...", "I found...") | Prevents hallucinated agency |
| Routing appropriateness | Content match to intent category | Validates routing decision quality |

### Advisory-Only Architecture

Reflection is explicitly **advisory**. It influences behavioural memory through two mechanisms:

1. **Decayed influence** — Reflection suggestions decay 3x faster than direct behavioral signals (`REFLECTION_DECAY_MULTIPLIER = 3.0`). A reflection-suggested adjustment fades quickly unless confirmed by actual user behavior.
2. **Half-weight application** — Reflection-driven confidence changes are applied at 50% strength. Behavioral signals from user interaction always dominate.

This ensures that self-critique subtly shapes future behavior without overriding what the user actually communicates.

### Creative Tolerance Windows

All 9 evaluation dimensions use graduated scoring instead of binary pass/fail. For example, grounding scoring:

- 0 ungrounded phrases → score 0.9
- 1 ungrounded phrase → score 0.6
- 2+ ungrounded phrases → score 0.3

This allows moderate expressiveness without penalty. Only extreme mismatch triggers correction. A bounded random jitter (±0.05) is applied to every score to prevent deterministic convergence.

### Reflection Memory

`ReflectionMemory` stores the last 50 observations with automatic compression. Older observations are aggregated into compressed entries preserving average scores. The `get_insights()` method aggregates actionable suggestions from recent observations, which `BehavioralMemory.apply_reflection_insights()` consumes at half-weight with 3x faster decay.

---

## Personality System

NIRA's personality is structured as three distinct layers with different mutability guarantees:

### 1. Identity Core (Immutable)

The `IdentityCore` maintains 6 traits that are **never modified** by any adaptive mechanism:

- Grounded, Calm, Observant, Subtle Humor, Emotionally Stable, Non Theatrical

These traits are injected into every system prompt as hard constraints, positioned after the behavioral context section. Behavioral modifiers can influence expression style, but the identity core ensures NIRA remains recognizably itself regardless of accumulated adaptation.

### 2. Controlled Personality Variance

A deterministic hash-based jitter (±3% range) is applied to all threshold comparisons in prompt assembly. This prevents robotic convergence — the same modifier values produce slightly different tone selections each time — while remaining deterministic for the same input.

### 3. Bounded Stabilization

`PersonalityStabilizer` combines multiple safeguards:

- **Per-modifier caps** — Each modifier is clamped to ±0.3
- **Total drift reset** — If total drift exceeds 0.8, all adjustments are zeroed
- **Homeostasis** — Gradual return-to-baseline pulls all modifiers toward zero
- **Contradiction dampening** — Conflicting signals are penalized before they reach the stabilizer
- **Meta-stability monitoring** — Internal telemetry tracks drift history, drift trend, contradiction count, and adaptation intensity. Exposed as a diagnostic-only report via `get_meta_report()`

### Anti-Sycophancy Design

The layered architecture prevents the most common failure modes of adaptive systems:

- A user cannot browbeat NIRA into abandoning its identity (identity core is immutable)
- A single conversation cannot reshape long-term behavior (requires 10+ confirmations)
- Conflicting demands do not cause oscillation (contradiction detection dampens reinforcement)
- Unreinforced adaptations decay naturally (homeostasis)

---

## Memory System

NIRA's memory is modeled after Atkinson-Shiffrin and Baddeley's cognitive memory models:

| Layer | Class | Storage | Scope | Eviction |
|---|---|---|---|---|---|
| Short-term | `ShortTermMemory` | RAM | Per turn | FIFO sliding window |
| Working | `WorkingMemory` | RAM | Current task | Task completion |
| Emotional | `EmotionalMemory` | Disk (JSON) | Sessions | Decay-based |
| Habit | `HabitMemory` | Disk (JSON) | Weeks/months | Confidence-based |
| Behavioral | `BehavioralMemory` + `BehavioralMemoryStore` | Disk (JSON) | Sessions–persistent | Confidence threshold (< 0.01) + hard cap (100) |
| Reflection | `ReflectionMemory` + `ReflectionMemoryStore` | Disk (JSON) | Recent 50 observations | Compression (older entries aggregated) |
| Summary | `SummaryMemory` | Disk (JSON) | Long-term | Summarization triggers |
| Profile | `ProfileManager` | Disk (JSON) | Permanent | Manual/learned |
| Conversation | `ConversationStore` | Disk (JSON) | Permanent | Explicit delete + auto-prune |

---

## Model Routing

NIRA routes based on cognitive demand, not intent labels:

| `requires_reasoning` | `requires_tools` | Decision |
|---|---|---|
| `True` | `False` | DeepSeek-R1 (reasoning track) |
| `True` | `True` | DeepSeek-R1 + ToolPlanner |
| `False` | `True` | Qwen + ToolPlanner |
| `False` | `False` | Qwen (conversational track) |
| confidence < 0.35 | any | Qwen (safe downgrade) |

The router reads only `CognitionSignal.requires_reasoning` — never intent category strings. This means adding a new intent category never requires touching routing logic.

---

## Installation

### Prerequisites

- Python 3.10+
- An [OpenRouter](https://openrouter.ai) API key (free tier works for getting started)

### 1. Clone the repository

```bash
git clone https://github.com/satyam-mishra-07/NIRA.git
cd NIRA
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy the example env file and fill in your API key:

```bash
cp .env.example .env
```

Open `.env` and set:

```env
OPENROUTER_API_KEY=your_api_key_here

# Models (these are the defaults — change if you prefer others)
CONVERSATION_MODEL=qwen/qwen3-32b
REASONING_MODEL=deepseek/deepseek-chat-v3-0324
```

Everything else in `.env.example` has sensible defaults. You don't need to change anything else to get started.

### 5. Run NIRA

```bash
python main.py
```

You should see:

```
[runtime] NIRA cognitive runtime booting...
[runtime] Event bus active.
[runtime] Runtime state: IDLE
[runtime] Cognitive loop ready.

NIRA is online. Type 'exit' to quit.

You:
```

---

## Configuration

Key settings in `.env`:

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | — | **Required.** Your OpenRouter API key |
| `CONVERSATION_MODEL` | `qwen/qwen3-32b` | Model for conversational responses |
| `REASONING_MODEL` | `deepseek/deepseek-chat-v3-0324` | Model for deep reasoning tasks |
| `DEBUG` | `true` | Enables routing/model debug logs |
| `STREAM_OUTPUT` | `true` | Token-by-token streaming output |
| `SAFE_MODE` | `true` | Enables security guardrails |
| `ALLOW_TERMINAL_EXECUTION` | `false` | Gate for terminal tool (keep false until tools are wired) |
| `MAX_CONTEXT_MESSAGES` | `15` | Short-term memory window size |

---

## Development Status

NIRA is a passion project built in spare time. Here's an honest breakdown of what works, what's scaffolded, and what's planned:

| Component | Status |
|---|---|---|
| Cognitive pipeline (16 stages) | ✅ Working |
| CognitionAssessor + CognitionSignal | ✅ Working |
| ExecutionRouter (typed routing) | ✅ Working |
| Dual-model orchestration (Qwen + DeepSeek) | ✅ Working |
| PersonalityEngine + IdentityCore | ✅ Working |
| 8-layer memory architecture | ✅ Working |
| MoodAnalyzer | ✅ Working |
| HabitObserver (pattern detection) | ✅ Working |
| Behavioral Alignment System | ✅ Working |
| Contradiction Detection + Dampening | ✅ Working |
| Personality Homeostasis + Meta-Stability | ✅ Working |
| Self Reflection Cognition (9-dimension) | ✅ Working |
| Temporary vs Persistent Adaptation | ✅ Working |
| Hinglish normalization | ✅ Working |
| ConversationStore with auto-pruning | ✅ Working |
| InputValidator + Guardrails | ✅ Working |
| Tool integrations (browser, filesystem, terminal) | 🚧 Scaffolded, not wired |
| Voice pipeline (STT/TTS/wake word) | 🚧 Scaffolded |
| Vector memory (ChromaDB/FAISS) | 🚧 Scaffolded |
| Async architecture | 📋 Planned (Phase 2) |
| Full agentic loop | 📋 Planned (Phase 3) |
| Desktop UI (PyQt6) | 🚧 Scaffolded |

---

## Roadmap

**Phase 1 — Semantic Memory**
Replace keyword-based `SummaryMemory` with vector embeddings (FAISS or ChromaDB). Every memory chunk gets an embedding; retrieval becomes cosine similarity search.

**Phase 2 — Async Architecture**
Refactor `CognitiveLoop` to `async/await`. Model calls, tool execution, and memory writes run concurrently.

**Phase 3 — Full Agentic Loop**
Wire `AgentLoop` in `agents/`. When `CognitionSignal.is_agentic=True`, route to multi-step tool execution with goal state in `WorkingMemory`.

**Phase 4 — Deep Self-Reflection**
Post-generation quality pass with conditional regeneration: if reflection scores fall below threshold, regenerate with corrective context. Current self-reflection is advisory-only; this phase adds a re-generation loop with max iterations.

**Phase 5 — Multi-Model Ensemble**
Add a creative model track. Confidence-weighted ensemble mode for low-confidence routing decisions.

**Phase 6 — Graph Memory**
Replace flat `ConversationStore` with a knowledge graph. Entities become nodes, relationships become edges, retrieval becomes graph traversal.

---

## Philosophy

> *Intelligence is an emergent property of well-orchestrated information processing.*

None of NIRA's components is intelligent in isolation. The model is a text sampler. Memory is a database. Routing is a classifier. Personality is a string template. But when these components work together with well-designed information flow, the system produces outputs that feel intelligent, coherent, and aware.

The architecture is the bottleneck — not the model. A better `CognitionAssessor` improves every routing decision. Better memory retrieval gives the model more relevant context. A stronger `PersonalityEngine` reduces identity drift. The model is already more capable than NIRA currently lets it be.

NIRA's design philosophy prioritizes **stable adaptive cognition** over reward optimization. Learning is bounded, adaptation is reversible, and identity is immutable. The behavioral layer learns from real interaction patterns rather than RLHF signals. Reflection is advisory — it informs but never overrides. This means NIRA can adapt to individual users without drifting into sycophancy or losing its core identity.

---

## Contributing

This is a personal project and not currently open for external contributors, but if you find bugs, have ideas, or want to discuss architecture — open an issue. Always happy to talk about AI systems design.

---

## License

MIT — do whatever you want, just don't claim you built it.

---

*Built with curiosity by Satyam Mishra. NIRA is an ongoing experiment in what it takes to make an AI feel genuinely present.*
