# 🧠 AGENTS.md — J.A.R.V.I.S. Multi-Agent System Architecture & Operating Rules Map

> **Repository Standard:** Stark Horizon v3.0 / v3.1 Upgrade Ready  
> **System Architecture:** 100% Local Sovereign Multi-Agent Operating System  
> **Hardware Target:** Intel Core i7-1255U (2 P-Cores, 8 E-Cores / 12 Threads) + Intel Iris Xe Graphics  
> **Core Spine:** FastAPI (`http://127.0.0.1:8765`) pinned to P-Cores (`0x00F` Affinity Mask)

---

## 1. Project Overview & Sovereign AI Philosophy

J.A.R.V.I.S. (Just A Rather Very Intelligent System) is a sovereign, 100% local, multi-agent AI assistant engineered to run directly on the host computer without cloud dependencies, external API keys, or remote subscriptions. 

### Core Operating Directives:
1. **"Don't just use the tool. Understand the system."** — Tony Stark Mindset.
2. **Cognitive Tiering:**
   - **LLM Mode:** *LLM thinks. It generates.* (Generative answers from model weights)
   - **RAG Mode:** *RAG reads + thinks. It retrieves & generates.* (ChromaDB + Knowledge Triples)
   - **AI Agent Mode:** *AI Agent thinks + acts. It plans, uses tools, and executes.* (Win32, MCP, Playwright)
   - **Hybrid Mode:** Complete integrated pipeline (Reads, Thinks & Acts).
3. **Zero Hardcoded Paths:** Always resolve via `config.root_dir`, `config.data_dir`, or environment variables (`JARVIS_ROOT`, `JARVIS_DATA_DIR`).
4. **Strict Error Isolation:** Every subsystem handles exceptions locally with graceful fallback; the central FastAPI spine must never crash.
5. **P-Core Affinity:** AI compute and audio perception threads are pinned to Performance Cores (P-Cores) to bypass Windows E-Core scheduler latency.
6. **User Permission Escrow:** All online connections, system upgrades, and critical actions require explicit user sign-off (`approved: True` or voice `"YES"`).

---

## 2. System Architecture & Component Inventory

```
                                  ┌─────────────────────────────────────────────────┐
                                  │      J.A.R.V.I.S. Central Spine (FastAPI)       │
                                  │           http://127.0.0.1:8765 (P-Core)        │
                                  └────────────────────────┬────────────────────────┘
                                                           │
       ┌────────────────────────┬──────────────────────────┼─────────────────────────┬────────────────────────┐
       ▼                        ▼                          ▼                         ▼                        ▼
 🎙️ Audio Perception     🧠 Cognitive & LLM       ⚡ Agents & Workflows     🛡️ Security & OS Act     💾 Tiered Memory
 • DualGate VAD         • Ollama (OpenVINO)       • 15 Task Workflows        • 4-Layer Guardrails     • ChromaDB Vector
 • openWakeWord         • Token Budget (10/15/25) • Frontier Evaluator       • Protocol VERONICA      • SQLite Triples
 • Whisper STT          • Sassy Persona Core      • Stark Mindset Engine     • Win32 SendInput / UI   • AES-256-GCM Vault
 • Kokoro-82M TTS       • 3-Stage Intent Router   • CS Skill Knowledge       • 512MB RAM Capping      • Episodic Graph
```

---

## 3. Registered Agents & Specialized Engines

### A. Dynamic Workflow Engine (`jarvis/agents/dynamic_workflows.py`)
Implements 15 autonomous task workflows:
- **Mode 01 — PRD Engine:** Generates Product Requirement Documents with Problem, User, Features, Tech Stack, & Acceptance.
- **Mode 02 — AGENTS.md Generator:** Maps repository architectures, conventions, commands, and rules.
- **Mode 03 — Ultra Plan:** Multi-phase engineering roadmaps with risk matrices and dependencies.
- **Mode 04 — Spec-Driven Dev:** Translates human requirements into deterministic API/interface specifications.
- **Mode 05 — UI/UX Design Brief:** Produces Stark HUD design specs, color tokens, and layout guidelines.
- **Mode 06 — Implementation Plan:** Generates component-by-component implementation plans.
- **Mode 07 — Wire MCP Tool:** Discovers, generates JSON-RPC schemas, and attaches stdio MCP tools.
- **Mode 08 — Connect Database:** Generates ChromaDB, SQLite, and vector database schemas.
- **Mode 09 — Security Gaps Audit:** Scans AST for hardcoded credentials, buffer overflow, and injection vectors.
- **Mode 10 — Debug Error:** Systematic root-cause debugging with stack trace parsing.
- **Mode 11 — E2E Test Suite:** Produces comprehensive pytest test suites for all subsystems.
- **Mode 12 — Clean Dead Code:** Safely identifies unused imports, uncalled functions, and obsolete files.
- **Mode 13 — Clean Git Commits:** Generates Conventional Commits with semantic changelog entries.
- **Mode 14 — Guardrail Hooks:** Configures pre-execution HMAC security hooks and memory limits.
- **Mode 15 — Task into Skill:** Turns executed workflows into reusable skill documentation files in `skills/`.

### B. Frontier Models Evaluator & Sassy Roast Engine (`jarvis/agents/frontier_evaluator.py`)
- Evaluates 11+ August 2026 frontier models live (Gemini 3.7 Flash, Grok 4.6, GLM-5.3, Qwen 3.8, DeepSeek R1/V4, Kimi K3).
- Features Tony Stark's sassy roasting persona: roasts cloud AI dependencies while praising 100% sovereign local execution.

### C. Skill Knowledge Engine (`jarvis/learning/skill_knowledge_engine.py`)
Indexes **100+ Core Computer Science Acronyms** across 5 domains:
1. **Programming & Software:** `API`, `SDK`, `IDE`, `CLI`, `GUI`, `OOP`, `DSA`, `DBMS`, `ORM`, `MVC`, `CRUD`, `REPL`, `JDK`, `JRE`, `JVM`, `VCS`, `SRS`, `UML`, `TDD`, `SDLC`.
2. **Web Development:** `HTML`, `CSS`, `JS`, `DOM`, `URL`, `URI`, `HTTP`, `HTTPS`, `REST`, `JSON`, `XML`, `AJAX`, `CDN`, `CORS`, `SSR`, `CSR`, `SPA`, `PWA`, `SEO`, `WWW`.
3. **Database & Cloud:** `SQL`, `NoSQL`, `RDBMS`, `DB`, `ACID`, `PK`, `FK`, `ER`, `OLTP`, `OLAP`, `DDL`, `DML`, `DQL`, `AWS`, `GCP`, `VM`, `VPS`, `DNS`, `IP`, `VPN`, `NAT`.
4. **DevOps, Git & Networking:** `CI`, `CD`, `IaC`, `SSH`, `SSL`, `TLS`, `TCP`, `UDP`, `SCM`, `PR`, `MR`, `CI/CD`, `PAT`, `SHA`, `README`, `LAN`, `WAN`, `FTP`, `SMTP`.
5. **AI, ML & Hardware:** `AI`, `ML`, `DL`, `NLP`, `CV`, `LLM`, `RAG`, `GAN`, `CNN`, `RNN`, `RL`, `GPU`, `TPU`, `BERT`, `CPU`, `RAM`, `ROM`, `OS`, `BIOS`, `USB`.
- **4 Execution Pillars:** `UNDERSTAND`, `LEARN`, `CONNECT`, `WORK ON SKILLS`.

### D. Tony Stark Mindset & Hacking Techniques Engine (`jarvis/system/stark_mindset_engine.py` & `jarvis/security/stark_hacking_techniques.py`)
- **5-Stage System Mastery Loop:** `RECON` ➔ `ACCESS` ➔ `ANALYZE` ➔ `ADAPT` ➔ `CONTROL`.
- **5 MCU Hacking Techniques:**
  1. **Display Hijack (Iron Man 2):** Access ➔ Control ➔ Redirect ➔ Replace.
  2. **The Ghost Drive (Iron Man 1):** Discover ➔ Enumerate ➔ Extract ➔ Expose.
  3. **Physical Implant Bridge (The Avengers 2012):** Engage ➔ Distract ➔ Approach ➔ Plant ➔ Access.
  4. **AI Cyber Operations (Age of Ultron 2015):** Raw Data ➔ Decrypt ➔ Classify ➔ Correlate ➔ Infer ➔ Respond.
  5. **Human Validation Escrow:** High-stakes operations pause for explicit operator sign-off.

### E. Cognitive Tiering & Permission-Gated Self-Upgrade Engine (`jarvis/system/self_upgrade_engine.py`)
- Automatically classifies tasks into LLM, RAG, AI Agent, or Hybrid mode.
- Generates `v3.1.0` self-upgrade proposals with permission escrow (`AWAITING_USER_APPROVAL`).

### F. Performance & Curriculum Engines
- **Time Complexity Profiler (`jarvis/system/time_complexity.py`):** Identifies 10 Big-O patterns (`O(1)` to `O(n!)`) with AST inspection.
- **Batch vs Stream Processing Selector (`jarvis/system/processing_mode.py`):** Selects between scheduled batch windows and real-time streaming (<200ms latency).
- **7-Stage AI Mastery Curriculum (`jarvis/learning/curriculum_engine.py`):** Guided learning path from RAG foundations to Fine-Tuning and Autonomous Swarms.
- **MCP Auto-Detector (`jarvis/mcp/auto_detector.py`):** Scans tool registries with 100% offline privacy guardrail.

---

## 4. Complete REST API Reference (FastAPI Spine `:8765`)

| Category | HTTP Method | Endpoint | Description |
|---|---|---|---|
| **Health & Spec** | `GET` | `/health` | Live system CPU, RAM, & uptime status |
| | `GET` | `/system/spec` | Hardware auditor & GPU/CPU topology |
| **Frontier Models** | `GET` | `/api/v1/frontier/models` | List of 11+ August 2026 frontier models |
| | `GET` | `/api/v1/frontier/breakdown` | Full model benchmarks & sassy roast |
| **Dynamic Workflows** | `POST` | `/api/v1/workflows/generate` | Generate workflows for Modes 01-15 |
| **Skill Knowledge** | `POST` | `/api/v1/skills/understand` | 1. UNDERSTAND: Acronym & term lookup |
| | `POST` | `/api/v1/skills/learn` | 2. LEARN: Auto-index concept into Memory Vault |
| | `POST` | `/api/v1/skills/connect` | 3. CONNECT: Map query to code module & tool |
| | `POST` | `/api/v1/skills/execute` | 4. WORK ON SKILLS: Autonomous task execution |
| **Cognitive Tiers** | `POST` | `/api/v1/system/classify_tier` | Classify task (LLM / RAG / Agent / Hybrid) |
| | `GET` | `/api/v1/system/upgrade_proposal`| Generate v3.1 self-upgrade proposal |
| | `POST` | `/api/v1/system/upgrade_authorize`| Execute upgrade under user permission |
| **Stark Mindset** | `GET` | `/api/v1/stark/recon` | Stage 1: RECON hardware & network map |
| | `POST` | `/api/v1/stark/access` | Stage 2: ACCESS local OS & interfaces |
| | `POST` | `/api/v1/stark/analyze` | Stage 3: ANALYZE code complexity & security |
| | `POST` | `/api/v1/stark/adapt` | Stage 4: ADAPT hybrid routing & intent |
| | `POST` | `/api/v1/stark/control` | Stage 5: CONTROL with Protocol VERONICA |
| **Stark Techniques** | `POST` | `/api/v1/stark/technique/display_hijack` | Technique 01: Video-feed display hijack |
| | `POST` | `/api/v1/stark/technique/ghost_drive` | Technique 02: Ghost drive file enumeration |
| | `POST` | `/api/v1/stark/technique/physical_implant` | Technique 03: Implant bridge connection |
| | `POST` | `/api/v1/stark/technique/ai_cyber_ops` | Technique 04: AI-assisted cyber ops triage |
| | `POST` | `/api/v1/stark/technique/human_validation` | Technique 05: Human validation escrow |
| **Performance** | `POST` | `/api/v1/system/profile_complexity` | Big-O time complexity code profiler |
| | `POST` | `/api/v1/system/processing_mode` | Batch vs Stream processing selector |
| | `POST` | `/api/v1/mcp/auto_detect` | Auto-detect online MCP tools with prompt |
| | `GET` | `/api/v1/learning/curriculum` | 7-Stage AI Mastery Building Roadmap |

---

## 5. Master Skill Documents Index (`skills/`)

| File | Domain / Topic |
|---|---|
| [`skills/dynamic_task_workflows_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/dynamic_task_workflows_skills.md) | 15 Dynamic Task Workflow Modes (PRD to Task-to-Skill) |
| [`skills/cs_foundations_and_skills_engine.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/cs_foundations_and_skills_engine.md) | 100+ CS/AI/Web/DB/DevOps Acronyms & 4 Execution Pillars |
| [`skills/llm_rag_agent_upgrade_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/llm_rag_agent_upgrade_skills.md) | Cognitive Tiering & Permission-Gated Self-Upgrade Protocol |
| [`skills/stark_cybersecurity_and_jarvis_mindset_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/stark_cybersecurity_and_jarvis_mindset_skills.md) | Tony Stark 5-Stage System Mastery Loop (`RECON` to `CONTROL`) |
| [`skills/stark_hacking_techniques_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/stark_hacking_techniques_skills.md) | 5 MCU Hacking Techniques & AI Cyber Ops Standard |
| [`skills/complexity_and_processing_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/complexity_and_processing_skills.md) | 10 Big-O Complexity Patterns & Batch vs Stream Selection |
| [`skills/audio_pipeline_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/audio_pipeline_skills.md) | Silero VAD, Whisper INT8, Kokoro-82M Voice Synthesis |
| [`skills/security_microvm_guardrails_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/security_microvm_guardrails_skills.md) | 4-Layer Defense, 512MB RAM Cap, & Protocol VERONICA |
| [`skills/context_working_memory_budget_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/context_working_memory_budget_skills.md) | 10/15/25/35/15 Token Budgeting & 3-Ring Compaction |
| [`skills/autonomous_git_cicd_pipeline_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/autonomous_git_cicd_pipeline_skills.md) | Autonomous Git, CI/CD, and Version Control Operations |
| [`skills/agentic-awesome-skills/`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/agentic-awesome-skills/) | 2,005+ Agentic Awesome Skills Core Library |

---

## 6. Developer Commands & Execution Guide

```powershell
# 1. Start Dev Core Spine Server (FastAPI :8765)
python -m jarvis.main

# 2. Boot Full System (Spine + HUD + Audio + System Tray)
powershell -ExecutionPolicy Bypass -File .\jarvis_boot.ps1

# 3. Run Pytest Test Suite (29 Subsystem Tests)
python -m pytest tests/

# 4. Compile Standalone Executable (dist/jarvis.exe)
powershell -ExecutionPolicy Bypass -File .\scripts\build_jarvis_exe.ps1

# 5. Graceful Full Stack Shutdown
powershell -ExecutionPolicy Bypass -File .\jarvis_shutdown.ps1
```
