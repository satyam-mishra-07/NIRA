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
- **7-layer memory architecture** — Short-term, working, emotional, habit, summary, profile, and conversation store
- **CognitionAssessor** — Multi-dimensional intent classification (what, how hard, what tools, how long)
- **MoodAnalyzer** — Detects emotional state from input and calibrates tone accordingly
- **HabitObserver** — Learns behavioral patterns over time through a confidence-weighted reinforcement loop
- **PersonalityEngine** — Keeps NIRA's identity stable across model switches and long sessions
- **Hinglish support** — Handles English, Hindi, and mixed Hinglish naturally
- **Typed signal architecture** — `CognitionSignal` as a typed contract between cognition and routing; no string parsing
- **Clean dependency injection** — Every component is swappable and testable in isolation

### Under Active Development 🚧

- **Tool integrations** — Browser/web search, file system operations, terminal execution, code runner (scaffolded, not yet wired)
- **Behavioural memory** — Full habit reinforcement loop with long-term pattern persistence
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
│   ├── cognition/      # CognitiveLoop — the 11-stage pipeline
│   ├── orchestration/  # ExecutionRouter, ToolPlanner, OrchestrationRouter
│   ├── runtime/        # RuntimeLifecycle, EventBus, ContextManager
│   └── state/          # RuntimeState, WorkspaceState
│
├── cognition/          # Intelligence layer
│   ├── intent/         # CognitionAssessor, CognitionSignal, IntentPredictor
│   ├── mood/           # MoodAnalyzer, MoodStateTracker, EmotionalMemory bridge
│   ├── habits/         # HabitObserver, PatternDetector, ConfidenceEngine, HabitStore
│   ├── context/        # ActivityContext, UserContext, WorkspaceContext
│   └── reflection/     # MemoryReflection, ConversationSummarizer
│
├── memory/             # 7-layer memory system
│   ├── short_term/     # Sliding window conversation buffer (RAM only)
│   ├── working/        # Active task scratchpad (RAM only)
│   ├── emotional/      # Affective history (disk, decay-based)
│   ├── habits/         # Behavioral patterns with confidence scores (disk)
│   ├── summaries/      # Compressed long-term context (disk)
│   ├── profile/        # Persistent user profile (disk, permanent)
│   ├── conversation/   # Append-only turn log with auto-pruning (disk)
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

Every user message flows through an 11-stage deterministic pipeline:

```
User Input
    │
    ▼
[1] InputValidator + Guardrails      → Sanitize, check safety
    │
    ▼
[2] MoodAnalyzer                     → Detect emotional state → MoodSignal
    │
    ▼
[3] HabitObserver                    → Detect behavioral patterns → HabitStore
    │
    ▼
[4] CognitionAssessor                → Assess 4 dimensions → CognitionSignal
    │   (intent, reasoning depth, tool need, response depth)
    ▼
[5] IntentPredictor                  → Enrich with working memory context
    │
    ▼
[6] ExecutionRouter                  → Map signal → RouteDecision
    │   (which model track, whether to activate tools)
    ▼
[7] ModelRouter                      → Select actual LLM endpoint
    │   (DeepSeek-R1 for reasoning, Qwen for conversation)
    ▼
[8] ToolPlanner (if needed)          → Execute tools, package results as context
    │
    ▼
[9] PersonalityEngine                → Assemble system prompt + inject all memory layers
    │   (ShortTermMemory + WorkingMemory + ProfileManager + SummaryMemory)
    ▼
[10] Model API Call                  → Generate response (streaming or full)
    │
    ▼
[11] Memory Storage                  → ConversationStore + EmotionalMemory + HabitStore
         └── MemoryReflection        → Summarize if threshold reached
```

---

## Memory System

NIRA's memory is modeled after Atkinson-Shiffrin and Baddeley's cognitive memory models:

| Layer | Class | Storage | Scope | Eviction |
|---|---|---|---|---|
| Short-term | `ShortTermMemory` | RAM | Per turn | FIFO sliding window |
| Working | `WorkingMemory` | RAM | Current task | Task completion |
| Emotional | `EmotionalMemory` | Disk (JSON) | Sessions | Decay-based |
| Habit | `HabitMemory` | Disk (JSON) | Weeks/months | Confidence-based |
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
|---|---|
| Cognitive pipeline (11 stages) | ✅ Working |
| CognitionAssessor + CognitionSignal | ✅ Working |
| ExecutionRouter (typed routing) | ✅ Working |
| Dual-model orchestration (Qwen + DeepSeek) | ✅ Working |
| PersonalityEngine | ✅ Working |
| 7-layer memory architecture | ✅ Working |
| MoodAnalyzer | ✅ Working |
| HabitObserver (pattern detection) | ✅ Working |
| Hinglish normalization | ✅ Working |
| ConversationStore with auto-pruning | ✅ Working |
| InputValidator + Guardrails | ✅ Working |
| Behavioural memory (full reinforcement loop) | 🚧 In progress |
| Tool integrations (browser, filesystem, terminal) | 🚧 Scaffolded, not wired |
| Voice pipeline (STT/TTS/wake word) | 🚧 Scaffolded |
| Vector memory (ChromaDB/FAISS) | 🚧 Scaffolded |
| Async architecture | 📋 Planned (Phase 2) |
| Full agentic loop | 📋 Planned (Phase 3) |
| Self-reflection pass | 📋 Planned (Phase 4) |
| Desktop UI (PyQt6) | 🚧 Scaffolded |

---

## Roadmap

**Phase 1 — Semantic Memory**
Replace keyword-based `SummaryMemory` with vector embeddings (FAISS or ChromaDB). Every memory chunk gets an embedding; retrieval becomes cosine similarity search.

**Phase 2 — Async Architecture**
Refactor `CognitiveLoop` to `async/await`. Model calls, tool execution, and memory writes run concurrently.

**Phase 3 — Full Agentic Loop**
Wire `AgentLoop` in `agents/`. When `CognitionSignal.is_agentic=True`, route to multi-step tool execution with goal state in `WorkingMemory`.

**Phase 4 — Self-Reflection**
Post-generation quality pass: did the response match intent? Is it coherent? Conditional regeneration loop with max iterations.

**Phase 5 — Multi-Model Ensemble**
Add a creative model track. Confidence-weighted ensemble mode for low-confidence routing decisions.

**Phase 6 — Graph Memory**
Replace flat `ConversationStore` with a knowledge graph. Entities become nodes, relationships become edges, retrieval becomes graph traversal.

---

## Philosophy

> *Intelligence is an emergent property of well-orchestrated information processing.*

None of NIRA's components is intelligent in isolation. The model is a text sampler. Memory is a database. Routing is a classifier. Personality is a string template. But when these components work together with well-designed information flow, the system produces outputs that feel intelligent, coherent, and aware.

The architecture is the bottleneck — not the model. A better `CognitionAssessor` improves every routing decision. Better memory retrieval gives the model more relevant context. A stronger `PersonalityEngine` reduces identity drift. The model is already more capable than NIRA currently lets it be.

---

## Contributing

This is a personal project and not currently open for external contributors, but if you find bugs, have ideas, or want to discuss architecture — open an issue. Always happy to talk about AI systems design.

---

## License

MIT — do whatever you want, just don't claim you built it.

---

*Built with curiosity by Satyam Mishra. NIRA is an ongoing experiment in what it takes to make an AI feel genuinely present.*
