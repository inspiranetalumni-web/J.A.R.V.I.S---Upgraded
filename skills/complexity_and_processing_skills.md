# ⏱️ J.A.R.V.I.S. Time Complexity, Processing Modes & AI Mastery Skill Standard

This skill establishes the performance optimization rules, processing model selection, offline privacy guardrails, and AI building roadmap for J.A.R.V.I.S.

---

## 1. Auto-Detecting MCP Tools & Offline Permission Guardrail
* **Default Mode:** 100% Offline / Local Operation.
* **Auto-Detection:** Automatically indexes local tools (`filesystem`, `database`, `os_actuation`) vs online tools (`playwright_browser`, `github`).
* **Privacy Guardrail:** If a task requires online access, J.A.R.V.I.S. halts network initiation until the operator explicitly confirms:
  `[ONLINE MCP TOOL DETECTED]: Do you authorize J.A.R.V.I.S. to connect online? (Reply YES to proceed)`

---

## 2. 10 Must-Know Time Complexity Patterns
When analyzing, generating, or refactoring code, J.A.R.V.I.S. profiles operations against the 10 Big-O complexity patterns:

1. **Hash Lookup — `O(1)`**: `value = map.get(key)` (Sub-0.1ms instant jump).
2. **Halving Loop — `O(log n)`**: `while (n > 1) n = n / 2` (<0.5ms logarithmic halving).
3. **Single Loop — `O(n)`**: `for (i=0; i<n; i++)` (~1-5ms linear single-pass).
4. **Sequential Loops — `O(n + m)`**: `for(...) for(...)` (~2-10ms linear multi-pass).
5. **Loop + Binary Search / Divide & Conquer — `O(n log n)`**: `for(...) binarySearch(a, x)` (~10-30ms quasilinear).
6. **Divide & Conquer — `O(n log n)`**: `T(n) = 2T(n/2) + n` (MergeSort / Timsort).
7. **Nested Loop / Triangular Loop — `O(n^2)`**: `for(...) for(...)` (~100-500ms quadratic). Refactor with Hash Maps `O(1)`.
8. **Branching Recursion — `O(2^n)`**: `T(n) = T(n-1) + T(n-2)` (>5,000ms exponential). Refactor with Dynamic Programming `O(n)`.
9. **Permutations — `O(n!)`**: `for(c : choices) permute(rest)` (>60,000ms factorial explosion). Apply heuristic pruning.

---

## 3. Batch vs Stream Processing Strategy

```
                          ┌─────────────────────────────────────────┐
                          │     J.A.R.V.I.S. Task Intent Router    │
                          └───────────────────┬─────────────────────┘
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     ▼                                                 ▼
     ⚡ STREAM PROCESSING (~195ms)                       📦 BATCH PROCESSING (Scheduled)
   • Unbounded real-time event streams                 • Bounded data sets
   • Silero VAD + faster-whisper STT                   • ChromaDB index compaction
   • Kokoro-82M ONNX voice streaming                   • KùzuDB graph entity consolidation
   • PySide6 Ghost HUD WebSocket telemetry             • Daily 02:00 AM memory maintenance
```

---

## 4. 7-Stage AI Building Roadmap (Learn & Build in Order)

> *"The real advantage in AI is understanding what to build, why it works, and how the pieces connect."*

1. **Prompting** ➔ System Prompts, In-Context Rules, Schema Enforcement (`jarvis/agents/conversational.py`).
2. **LLMs** ➔ Inference Engine, Ollama / OpenVINO local core, Sub-50ms TTFT (`jarvis/llm/engine.py`).
3. **Embeddings** ➔ Dense Vector Space, Cosine Similarity Indexing (`jarvis/memory/semantic.py`).
4. **RAG** ➔ Retrieval-Augmented Generation, Context Token Budgeting, ChromaDB + KùzuDB (`jarvis/context/budget.py`).
5. **AI Agents** ➔ Multi-Agent Swarm Orchestration, Tool Calling, Hybrid Intent Router (`jarvis/mcp/router.py`).
6. **Fine-Tuning** ➔ LoRA Adapters, Synthetic Data Alignment (`jarvis/llm/finetune_adapter.py`).
7. **AI Coding** ➔ Autonomous Code Generation, AST Validation, Refactoring Engines (`jarvis/agents/frontier_evaluator.py`).
