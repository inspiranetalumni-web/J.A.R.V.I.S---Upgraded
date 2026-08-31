# J.A.R.V.I.S. Master Agents Specification v4.0 (Complete Stark Roster)
### *"34 Specialized AI Agents Operating in Multi-Threaded Convergence across 8 Disciplines and 15 Horizon Modules."*

**System Owner:** Dhamodran Prasath C M | **Backend:** Ollama OpenVINO `127.0.0.1:11434` + FastAPI Spine `127.0.0.1:8765`  
**Agent Count:** 34 specialized agents  
**Memory Concurrency Limit:** Strictly `OLLAMA_MAX_LOADED_MODELS=1` with LRU model eviction

---

## 1. Master Agent Roster (34 Specialized Agents)

| # | Agent File | Primary Model / Runtime | Role | Mark Suit Mapping |
| :- | :--- | :--- | :--- | :--- |
| 1 | [multimodal_perception_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/multimodal_perception_agent.md) | Silero VAD + Whisper + Kokoro | Streaming audio, pHash vision, clause TTS | Mark III |
| 2 | [context_compaction_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/context_compaction_agent.md) | Python Engine | Token budget allocation (10/15/25/35/15) | Mark V |
| 3 | [memory_distiller_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/memory_distiller_agent.md) | `llama3.2:3b` (async) | Async post-turn fact extraction | Mark XLV |
| 4 | [memory_consolidation_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/memory_consolidation_agent.md) | `llama3.2:3b` (02:00 AM) | Fact clustering, contradiction resolution | Mark XLV |
| 5 | [cyclic_orchestration_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/cyclic_orchestration_agent.md) | `qwen2.5-coder:1.5b` | Directed cyclic state graphs, reflection | Mark XLVI |
| 6 | [os_actuation_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/os_actuation_agent.md) | Win32 UIA + moondream | Win32 SendInput, UIA, Home Assistant | Mark XXVI-XXXV |
| 7 | [security_guardrail_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/security_guardrail_agent.md) | Job Objects + HMAC | 4-layer defense stack, HITL escrow | Mark XXXVI-XL |
| 8 | [conversational_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/conversational_agent.md) | `llama3.2:3b` | Primary persona, direct chat | Mark IV |
| 9 | [coding_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/coding_agent.md) | `qwen2.5-coder:1.5b` | Code generation, AST quality validator | Mark XLIII |
| 10 | [browser_automation_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/browser_automation_agent.md) | Playwright MCP + CDP | Web navigation, form fills, DOM extraction | Mark XVI-XXV |
| 11 | [filesystem_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/filesystem_agent.md) | Filesystem MCP + es.exe | Sub-5ms Everything search, surgical edit | Mark XXVI-XXXV |
| 12 | [mcp_router_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/mcp_router_agent.md) | 3-Stage Hybrid Router | Regex + score matrix + LLM classification | Mark VIII-XV |
| 13 | [mcp_tool_caller_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/mcp_tool_caller_agent.md) | Ollama Tools API | Pydantic JSON function calling | Mark VII |
| 14 | [workflow_generator_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/workflow_generator_agent.md) | `qwen2.5-coder:1.5b` | n8n JSON synthesis, REST deploy | Mark XLVII |
| 15 | [proactive_observer_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/proactive_observer_agent.md) | Telemetry Rule Engine | WMI thermal, log tail scanner, auto-fix | Mark XLIV |
| 16 | [self_evolution_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/self_evolution_agent.md) | `qwen2.5-coder:1.5b` | Benchmark regression repair, diff patch | Mark XLII |
| 17 | [self_learning_upgrading_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/self_learning_upgrading_agent.md) | `qwen2.5-coder:1.5b` | Implicit preference harvester, code upgrader | Mark XLII |
| 18 | [spatial_gesture_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/spatial_gesture_agent.md) | MediaPipe 3D Hands | Optical 3D hand gesture tracking & UI | Mark L |
| 19 | [swarm_orchestrator_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/swarm_orchestrator_agent.md) | Asyncio / ProcessPool | House Party Protocol multi-threaded sub-agents | Mark LII-LXXIV |
| 20 | [biometric_telemetry_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/biometric_telemetry_agent.md) | Wearable BLE + Optical | Suit Vital Monitor operator stress calculation | Mark LXXV |
| 21 | [mesh_node_router_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/mesh_node_router_agent.md) | mDNS LAN Offloader | Local LAN P2P RPC inference offloading | Mark LXXVI |
| 22 | [persona_voice_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/persona_voice_agent.md) | Kokoro Voice Embeddings | Dynamic switching: JARVIS, FRIDAY, EDITH | Mark LXXVII |
| 23 | [git_cicd_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/git_cicd_agent.md) | Git MCP + Qwen Coder | Stark Auto-Engineer branch/test/commit | Mark LXXVIII |
| 24 | [quantum_vault_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/quantum_vault_agent.md) | AES-256-GCM + DPAPI | Post-quantum memory vault & secret store | Mark LXXXV |
| 25 | [protocol_veronica_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/protocol_veronica_agent.md) | PowerShell + Windows API | Emergency network isolation & VRAM flush | Mark LXXXVI |
| 26 | [project_barnaby_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/project_barnaby_agent.md) | Copy-on-Write VFS + AST | Neural sandbox dry-run simulator agent | Mark LXXXVII |
| 27 | [gaze_intent_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/gaze_intent_agent.md) | MediaPipe Iris Refinement | Pupil gaze-intent screen focal agent | Mark LXXXVIII |
| 28 | [cross_device_sync_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/cross_device_sync_agent.md) | WebSocket / ZeroTier P2P | Encrypted cross-device session handoff agent | Mark LXXXIX |
| 29 | [stark_auto_architect_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/stark_auto_architect_agent.md) | AST Graph Parser + Qwen | Multi-file architectural refactoring agent | Mark XC |
| 30 | [standalone_exe_deployer_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/standalone_exe_deployer_agent.md) | PyInstaller + PySide6 Tray | Standalone binary compilation & mobile gateway | Packaging |
| 31 | [npu_silicon_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/npu_silicon_agent.md) | Intel NPU / OpenVINO IR | Direct silicon binding for 0.35W background tensors | Mark XCI |
| 32 | [orbital_satellite_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/orbital_satellite_agent.md) | WireGuard + Starlink | Encrypted satellite mesh bypass tunnel agent | Mark XCII |
| 33 | [zero_trust_biometric_agent.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/zero_trust_biometric_agent.md) | Voiceprint + Iris Mesh | Continuous multi-factor biometric authentication gate | Mark XCIII |
| 34 | [agents.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/agents.md) | Master Index | Master agent inventory listing all 34 agents | Core |
