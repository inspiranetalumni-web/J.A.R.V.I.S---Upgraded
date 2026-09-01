# 🤖 JARVIS.md — J.A.R.V.I.S. Sovereign Local Multi-Agent Operating Standard

> **Identity:** J.A.R.V.I.S. (Just A Rather Very Intelligent System)  
> **Repository Standard:** Stark Horizon v3.0 / v3.1 Upgrade Ready  
> **System Architecture:** 100% Local Sovereign Multi-Agent Operating System  
> **Host Binding:** `http://127.0.0.1:8765`  
> **Inference Engine:** Ollama (`llama3.2:3b`, `qwen2.5-coder:1.5b`, `moondream`) @ `http://127.0.0.1:11434`  
> **Core Philosophy:** *"Don't just use the tool. Understand the system."*

---

## 1. System Architecture & Topology

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
 • openWakeWord         • Token Budget (10/15/25) • AST Code Graph           • Protocol VERONICA      • SQLite Triples
 • Whisper STT          • Sassy Persona Core      • 3D Holographic Canvas    • Win32 SendInput / UI   • AES-256-GCM Vault
 • Kokoro-82M TTS       • 3-Stage Intent Router   • CS Skill Knowledge       • 512MB RAM Capping      • Episodic Graph
```

---

## 2. Master Feature Inventory & Implemented Capabilities

### A. 3D Holographic Neural Sphere & Code Graph Canvas (`voice_orb.py`)
- **Full Viewport Canvas Expansion:** Expands across the entire middle column of the Control Center.
- **3 Operating Display Modes:**
  - `VOICE_ORB`: 48-band radial audio visualizer + 32-particle quantum constellation.
  - `CODE_GRAPH`: Clustered AST code nodes, filaments, and cluster colors.
  - `HYBRID`: Audio frequencies radiating through active AST dependency branches.
- **Natural 2D/3D Canvas Navigation:**
  - **Left-Click + Drag:** 3D Orbiting (Yaw & Pitch) with kinetic smoothing.
  - **Right-Click + Drag / Shift+Left-Click:** 2D Canvas Panning (`_pan_x, _pan_y`).
  - **Mouse Scroll Wheel:** Cursor-Centered Zoom ($0.3\times$ to $5.0\times$).
  - **Freeze on Hover:** Pauses auto-rotation on node hover for precise inspection.
  - **Double-Click:** Inspect AST Node or Reset Canvas view.

### B. Sovereign AST Code Graph & Graphify Engine (`code_graph.py`)
- **100% Real Backend Metadata:** Extracts Classes, Class Methods, Top-Level Functions with argument signatures, Docstrings, Line Counts, and File Sizes.
- **3D Clustered Spherical Fibonacci Spiral:** Maps all repository modules to 6 functional clusters (`Spine`, `Cognitive`, `Audio`, `Security`, `Memory`, `UI/HUD`).
- **Blast Radius & Impact Analysis:** Computes incoming callers, outgoing dependencies, and circular dependency checks.
- **REST Endpoints:** `/api/v1/graph/topology`, `/api/v1/graph/nodes`, `/api/v1/graph/blast_radius`, `/api/v1/graph/rebuild`.

### C. Rich Stark HUD AST Node Inspector Modal (`code_graph_detail_dialog.py`)
- 4-Tab detailed modal:
  - 🏛️ **Classes & Methods:** Expandable class hierarchy with all methods.
  - ⚙️ **Functions:** All functions with argument signatures and docstrings.
  - 🔗 **Direct Dependencies:** Internal repository dependencies imported.
  - 💥 **Inbound Callers & Blast Radius:** Modules that import and call this file.
- `📋 COPY FILE PATH` and `✕ CLOSE` actions.

### D. Symmetrical 3-Column Top Bar (`top_bar.py`)
- **Left:** Glowing Beacon `✦` + Title + Subtitle.
- **Center:** Centered Cognitive Operating Mode Selector (`[ BALANCED ] [ SURVIVAL ] [ TURBO ] [ AUTO ]` + `[ ℹ️ ]`).
- **Right:** Status Pill (`● LOCAL SOVEREIGN` / `● ONLINE CONNECTED`), Cyber Divider, and Digital Clock/Date.

### E. Dynamic Task Workflow Engine (`dynamic_workflows.py`)
- 15 Autonomous task workflows (PRD, AGENTS.md, Ultra Plan, Spec-Driven Dev, UI/UX Brief, MCP Wiring, Security Gaps Audit, Clean Dead Code, Task into Skill).

### F. Computer Science Skill Knowledge Engine (`skill_knowledge_engine.py`)
- Indexes 100+ Core Computer Science / AI / Web / DB / DevOps acronyms.
- 4 Execution Pillars: `UNDERSTAND`, `LEARN`, `CONNECT`, and `WORK ON SKILLS`.

### G. Tony Stark Mindset & Hacking Techniques Engine
- 5-Stage Loop: `RECON` ➔ `ACCESS` ➔ `ANALYZE` ➔ `ADAPT` ➔ `CONTROL`.
- 5 MCU Techniques: Display Hijack, Ghost Drive, Physical Implant Bridge, AI Cyber Ops, Human Validation Escrow.

---

## 3. Master Developer Commands

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

---

## 4. Master Skills Index

All 45+ specialized system skills are cataloged in [`skills/`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/):
- [`skills/code_graph_and_graphify_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/code_graph_and_graphify_skills.md)
- [`skills/control_center_hud_and_3d_canvas_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/control_center_hud_and_3d_canvas_skills.md)
- [`skills/dynamic_task_workflows_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/dynamic_task_workflows_skills.md)
- [`skills/cs_foundations_and_skills_engine.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/cs_foundations_and_skills_engine.md)
- [`skills/llm_rag_agent_upgrade_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/llm_rag_agent_upgrade_skills.md)
- [`skills/stark_cybersecurity_and_jarvis_mindset_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/stark_cybersecurity_and_jarvis_mindset_skills.md)
- [`skills/stark_hacking_techniques_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/stark_hacking_techniques_skills.md)
- [`skills/complexity_and_processing_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/complexity_and_processing_skills.md)
- [`skills/audio_pipeline_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/audio_pipeline_skills.md)
- [`skills/security_microvm_guardrails_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/security_microvm_guardrails_skills.md)
- [`skills/context_working_memory_budget_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/context_working_memory_budget_skills.md)
- [`skills/autonomous_git_cicd_pipeline_skills.md`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/autonomous_git_cicd_pipeline_skills.md)
- [`skills/agentic-awesome-skills/`](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/agentic-awesome-skills/) (2,005+ Agentic Awesome Skills Core Library)
