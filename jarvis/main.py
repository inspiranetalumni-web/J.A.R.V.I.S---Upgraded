"""
jarvis/main.py — Central FastAPI Core Spine Server v3.0 (Stark Horizon Standard)
Binds to http://127.0.0.1:8765. Manages core life-cycle, health telemetry, and system spec endpoints.
"""

import time
import os
import sys
import json
import psutil
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from jarvis.config import config
from jarvis.system.spec_loader import audit_hardware

START_TIME = time.time()

def set_process_pcore_affinity():
    """
    Pins the main FastAPI spine process to P-Cores (Threads 0-3 / Mask 0x00F) on Windows x86_64
    to prevent E-Core scheduler latency overhead.
    """
    try:
        proc = psutil.Process(os.getpid())
        if hasattr(proc, "cpu_affinity"):
            # Set affinity mask to first 4 logical cores if available
            available_cores = list(range(min(4, psutil.cpu_count(logical=True) or 1)))
            proc.cpu_affinity(available_cores)
            print(f"[SPINE] Process PID {os.getpid()} pinned to P-Core threads: {available_cores}")
    except Exception as e:
        print(f"[SPINE] CPU affinity pin skipped/deferred: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager handling startup and graceful shutdown.
    """
    print("============================================================")
    print("   J.A.R.V.I.S. v3.0 STARK HORIZON CORE SPINE INITIALIZING  ")
    print("============================================================")
    print(f"[SPINE] Endpoint: {config.to_dict()['fastapi_endpoint']}")
    print(f"[SPINE] Root Directory: {config.root_dir}")
    print(f"[SPINE] Data Directory: {config.data_dir}")
    
    set_process_pcore_affinity()

    # Initialize Perception Audio Engine & Laptop Microphone Listener
    try:
        from jarvis.audio.manager import AudioManager
        from jarvis.agents.conversational import ConversationalAgent
        audio_mgr = AudioManager()
        conv_agent = ConversationalAgent()

        def _on_transcript(text: str):
            print(f"[LAPTOP VOICE INTAKE] Transcribed: '{text}'")
            # Stream clause-buffered responses into the audio manager
            clauses = conv_agent.stream_response(text, cancel_event=audio_mgr.cancel_token)
            audio_mgr.speak_stream(clauses)

        audio_mgr.register_on_utterance_callback(_on_transcript)
        audio_mgr.start_mic_listener()
        print("[SPINE] Perception Audio Pipeline & Laptop Microphone intake initialized.")
    except Exception as err:
        print(f"[SPINE] Audio Pipeline initialization note: {err}")
    
    yield
    
    print("[SPINE] Gracefully shutting down J.A.R.V.I.S. Core Spine Server...")

app = FastAPI(
    title="J.A.R.V.I.S. Core Spine API",
    description="Central Orchestrator for J.A.R.V.I.S. v3.0 Multi-Agent Horizon System",
    version="3.0.0",
    lifespan=lifespan
)

# Enable CORS for PySide6 HUD, WebSockets, and Local Frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import HTMLResponse
from fastapi import WebSocket, WebSocketDisconnect
from jarvis.mobile.mobile_gateway import MobileGateway

mobile_gateway = MobileGateway()

@app.get("/mobile", response_class=HTMLResponse)
async def get_mobile_dashboard():
    """Mobile Companion Web PWA Interface for iOS and Android devices."""
    return mobile_gateway.get_mobile_pwa_html()

@app.websocket("/ws/mobile")
async def websocket_mobile_endpoint(websocket: WebSocket):
    """Real-time WebSocket endpoint for paired mobile device communication."""
    await websocket.accept()
    await mobile_gateway.register_connection(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            response_data = mobile_gateway.handle_mobile_message(data)
            await mobile_gateway.broadcast_state(response_data)
    except WebSocketDisconnect:
        await mobile_gateway.unregister_connection(websocket)
    except Exception:
        await mobile_gateway.unregister_connection(websocket)

@app.get("/")
async def root_status():
    """Root Endpoint returning core spine identification."""
    return {
        "system": "J.A.R.V.I.S. v3.0 Stark Horizon Core Spine",
        "status": "online",
        "version": "3.0.0",
        "endpoint": config.to_dict()["fastapi_endpoint"],
        "docs": f"{config.to_dict()['fastapi_endpoint']}/docs"
    }

@app.get("/health")
async def health_check():
    """System Health Check returning uptime, CPU load, and RAM telemetry."""
    uptime_seconds = round(time.time() - START_TIME, 2)
    proc = psutil.Process(os.getpid())
    mem_info = proc.memory_info()
    
    return {
        "status": "healthy",
        "uptime_seconds": uptime_seconds,
        "process_pid": os.getpid(),
        "process_memory_mb": round(mem_info.rss / (1024 * 1024), 2),
        "system_cpu_percent": psutil.cpu_percent(interval=None),
        "system_ram_percent": psutil.virtual_memory().percent
    }

@app.post("/api/v1/system/shutdown")
@app.get("/shutdown")
async def shutdown_system():
    """Triggers graceful system shutdown protocol."""
    def _do_shutdown():
        time.sleep(0.5)
        os._exit(0)

    import threading
    threading.Thread(target=_do_shutdown, daemon=True).start()
    return {
        "status": "shutting_down",
        "message": "Shutting down core systems, sir. Goodnight.",
        "protocol": "GRACEFUL_HALT"
    }

@app.post("/api/v1/system/command")
async def execute_system_command(payload: dict):
    """Executes command payload through MobileGateway and ConversationalAgent."""
    cmd = payload.get("command", "")
    return mobile_gateway.handle_mobile_message(json.dumps({"type": "remote_command", "command": cmd}))

@app.get("/specs")
@app.get("/api/v1/system/specs")
async def get_system_specs():
    """Returns dynamic hardware audit information (CPU, GPU, RAM, Accelerators)."""
    return audit_hardware()

@app.get("/config")
@app.get("/api/v1/system/config")
async def get_system_config():
    """Returns runtime directory topologies and service configurations."""
    return config.to_dict()

@app.get("/api/v1/frontier/models")
async def get_frontier_models():
    """Returns August 2026 Frontier Models benchmark matrix."""
    from jarvis.agents.frontier_evaluator import FrontierModelEvaluator
    evaluator = FrontierModelEvaluator()
    return evaluator.get_benchmark_matrix()

@app.get("/api/v1/frontier/breakdown")
async def get_frontier_breakdown():
    """Returns August 2026 model breakdown, live sassy roast, and local PC actuation proof."""
    from jarvis.agents.frontier_evaluator import FrontierModelEvaluator
    evaluator = FrontierModelEvaluator()
    return evaluator.generate_live_breakdown_script()

@app.post("/api/v1/workflows/generate")
async def generate_dynamic_workflow(payload: dict):
    """
    Executes 10 dynamic development workflow modes:
    01. write_prd (feature)
    02. generate_agents_md ()
    03. ultra_plan (task)
    04. spec_driven_dev (feature)
    05. ui_ux_brief (screen_or_flow)
    06. implementation_plan (spec_or_prd)
    07. wire_mcp_server (service_or_api)
    08. connect_database (db_type)
    09. find_security_gaps (focus_areas)
    10. debug_error_fast (error_trace)
    """
    from jarvis.agents.dynamic_workflows import DynamicWorkflowEngine
    engine = DynamicWorkflowEngine()
    mode = str(payload.get("mode", "")).lower()
    
    if mode in ["write_prd", "prd", "01", "1"]:
        feature = payload.get("feature", "unnamed_feature")
        return engine.write_prd(feature)
    elif mode in ["generate_agents_md", "agents_md", "jarvis_md", "02", "2"]:
        return engine.generate_agents_md()
    elif mode in ["ultra_plan", "plan", "03", "3"]:
        task = payload.get("task", "unnamed_task")
        return engine.ultra_plan(task)
    elif mode in ["spec_driven_dev", "spec", "04", "4"]:
        feature = payload.get("feature", "unnamed_feature")
        return engine.spec_driven_development(feature)
    elif mode in ["ui_ux_brief", "design_brief", "05", "5"]:
        screen = payload.get("screen", "main_screen")
        return engine.ui_ux_design_brief(screen)
    elif mode in ["implementation_plan", "build_sequence", "06", "6"]:
        spec = payload.get("spec", "unnamed_spec")
        return engine.implementation_plan(spec)
    elif mode in ["wire_mcp_server", "mcp_server", "mcp", "07", "7"]:
        service = payload.get("service", "custom_mcp")
        return engine.wire_mcp_server(service)
    elif mode in ["connect_database", "database", "db", "08", "8"]:
        db_type = payload.get("db_type", "ChromaDB + KùzuDB")
        return engine.connect_database(db_type)
    elif mode in ["find_security_gaps", "security_audit", "security", "09", "9"]:
        focus = payload.get("focus", "AUTH / USER DATA")
        return engine.find_security_gaps(focus)
    elif mode in ["debug_error_fast", "debug_error", "debug", "10"]:
        error_trace = payload.get("error_trace", "unspecified_error")
        return engine.debug_error_fast(error_trace)
    elif mode in ["e2e_test_app", "e2e_test", "e2e", "11"]:
        flow = payload.get("flow", "Core Mobile & FastAPI Spine Interaction")
        return engine.e2e_test_app(flow)
    elif mode in ["cleanup_dead_code", "dead_code", "12"]:
        scope = payload.get("scope", "whole_repo")
        return engine.cleanup_dead_code(scope)
    elif mode in ["write_clean_commits", "clean_commits", "commit", "13"]:
        return engine.write_clean_commits()
    elif mode in ["hooks_as_guardrails", "guardrail_hooks", "hooks", "14"]:
        return engine.hooks_as_guardrails()
    elif mode in ["turn_task_into_skill", "task_to_skill", "skill", "15"]:
        name = payload.get("task_name", "new_task")
        desc = payload.get("description", "Custom task skill")
        triggers = payload.get("trigger_phrases", [name])
        return engine.turn_task_into_skill(name, desc, triggers)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown workflow mode '{mode}'. Available modes: 01_write_prd, 02_generate_agents_md, 03_ultra_plan, 04_spec_driven_dev, 05_ui_ux_brief, 06_implementation_plan, 07_wire_mcp_server, 08_connect_database, 09_find_security_gaps, 10_debug_error_fast, 11_e2e_test_app, 12_cleanup_dead_code, 13_write_clean_commits, 14_hooks_as_guardrails, 15_turn_task_into_skill"
        )

# --- MCP Auto-Detection & Online Permission Guardrail ---
from jarvis.mcp.auto_detector import MCPAutoDetector
mcp_detector = MCPAutoDetector()

@app.post("/api/v1/mcp/detect")
async def detect_mcp_tools(payload: dict):
    """Auto-detects required MCP tools and checks online permission state."""
    task = payload.get("task", "")
    return mcp_detector.auto_detect_tools(task)

@app.post("/api/v1/mcp/permission")
async def set_online_mcp_permission(payload: dict):
    """Grants or revokes online network access permission."""
    approved = payload.get("approved", False)
    mcp_detector.set_online_permission(approved)
    return {
        "online_access_approved": mcp_detector.online_access_approved,
        "message": "Online network access AUTHORIZED by user." if approved else "System operating in 100% OFFLINE mode."
    }

# --- Time Complexity Profiler ---
from jarvis.system.time_complexity import TimeComplexityProfiler
complexity_profiler = TimeComplexityProfiler()

@app.post("/api/v1/system/complexity")
async def profile_time_complexity(payload: dict):
    """Profiles code snippet against the 10 Time Complexity Patterns (O(1) to O(n!))."""
    code = payload.get("code", "")
    return complexity_profiler.profile_code(code)

# --- Processing Pipeline Manager (Batch vs Stream) ---
from jarvis.system.processing_mode import ProcessingPipelineManager
pipeline_manager = ProcessingPipelineManager()

@app.get("/api/v1/system/processing")
async def select_processing_pipeline(task_type: str = "audio_voice"):
    """Selects Batch Processing vs Stream Processing pipeline."""
    return pipeline_manager.select_processing_mode(task_type)

# --- AI Mastery Curriculum Engine ---
from jarvis.learning.curriculum_engine import AICurriculumEngine
curriculum_engine = AICurriculumEngine()

@app.get("/api/v1/learning/curriculum")
async def get_ai_curriculum():
    """Returns the 7-Stage AI Mastery Building Roadmap."""
    return curriculum_engine.get_full_curriculum()

# --- Skill Knowledge Engine (Understand, Learn, Connect, Work on Skills) ---
from jarvis.learning.skill_knowledge_engine import SkillKnowledgeEngine
skill_knowledge_engine = SkillKnowledgeEngine()

@app.post("/api/v1/skills/understand")
async def understand_cs_term(payload: dict):
    """1. UNDERSTAND: Explains any CS, AI, Web, DB, or DevOps term & J.A.R.V.I.S implementation."""
    term = payload.get("term", "")
    return skill_knowledge_engine.understand(term)

@app.post("/api/v1/skills/learn")
async def learn_cs_term(payload: dict):
    """2. LEARN: Auto-indexes new technical concept into J.A.R.V.I.S. Memory Vault."""
    term = payload.get("term", "")
    desc = payload.get("description", "")
    return skill_knowledge_engine.learn(term, desc)

@app.post("/api/v1/skills/connect")
async def connect_cs_term(payload: dict):
    """3. CONNECT: Maps query to J.A.R.V.I.S. code module, skill file, and MCP tool."""
    query = payload.get("query", "")
    return skill_knowledge_engine.connect(query)

@app.post("/api/v1/skills/execute")
async def work_on_skills(payload: dict):
    """4. WORK ON SKILLS: Dynamically executes the connected skill or code tool."""
    task = payload.get("task", "")
    return skill_knowledge_engine.work_on_skills(task)

# --- Cognitive Tier Classifier & Self-Upgrade Engine (LLM vs RAG vs AI Agent) ---
from jarvis.system.self_upgrade_engine import CognitiveTierClassifier, SelfUpgradeEngine
tier_classifier = CognitiveTierClassifier()
upgrade_engine = SelfUpgradeEngine()

@app.post("/api/v1/system/classify_tier")
async def classify_cognitive_tier(payload: dict):
    """Classifies task into LLM, RAG, AI Agent, or Hybrid cognitive mode."""
    task = payload.get("task", "")
    return tier_classifier.classify_task(task)

@app.get("/api/v1/system/upgrade_proposal")
async def get_upgrade_proposal():
    """Generates J.A.R.V.I.S. v3.1 self-upgrade proposal."""
    return upgrade_engine.generate_upgrade_proposal()

@app.post("/api/v1/system/upgrade_authorize")
async def authorize_self_upgrade(payload: dict):
    """Executes J.A.R.V.I.S. self-upgrade upon explicit user permission (approved: True)."""
    approved = payload.get("approved", False)
    return upgrade_engine.execute_upgrade(user_permission=approved)

# --- Tony Stark System Philosophy Engine (Recon -> Access -> Analyze -> Adapt -> Control) ---
from jarvis.system.stark_mindset_engine import StarkMindsetEngine
stark_engine = StarkMindsetEngine()

@app.get("/api/v1/stark/recon")
async def stark_recon():
    """Stage 1: RECON — Maps hardware, network, and system surface area."""
    return stark_engine.recon()

@app.post("/api/v1/stark/access")
async def stark_access(payload: dict):
    """Stage 2: ACCESS — Evaluates OS actuation & hardware interface access."""
    target = payload.get("target", "local_pc")
    return stark_engine.access(target)

@app.post("/api/v1/stark/analyze")
async def stark_analyze(payload: dict):
    """Stage 3: ANALYZE — Deep code analysis, complexity profiling, & system security audit."""
    target = payload.get("target", "system_code")
    return stark_engine.analyze(target)

@app.post("/api/v1/stark/adapt")
async def stark_adapt(payload: dict):
    """Stage 4: ADAPT — Dynamic routing, fallback execution, and self-learning adaptation."""
    intent = payload.get("intent", "status")
    return stark_engine.adapt(intent)

@app.post("/api/v1/stark/control")
async def stark_control(payload: dict):
    """Stage 5: CONTROL — Hands-free execution with user permission escrow & Protocol VERONICA."""
    action = payload.get("action", "status_check")
    permission = payload.get("user_permission", True)
    return stark_engine.control(action, user_permission=permission)

# --- Tony Stark Hacking Techniques & AI Cyber Ops Engine (5 MCU Case Studies) ---
from jarvis.security.stark_hacking_techniques import StarkHackingTechniquesEngine
stark_hacking_engine = StarkHackingTechniquesEngine()

@app.post("/api/v1/stark/technique/display_hijack")
async def stark_display_hijack(payload: dict):
    """Technique 01: Display / Video-Feed Hijack (Iron Man 2)."""
    channel = payload.get("channel", "DISPLAY-01")
    feed = payload.get("feed", "STARK_HUD")
    return stark_hacking_engine.display_video_hijack(channel, feed)

@app.post("/api/v1/stark/technique/ghost_drive")
async def stark_ghost_drive(payload: dict):
    """Technique 02: The Ghost Drive Enumeration (Iron Man 1)."""
    target = payload.get("target_dir", None)
    return stark_hacking_engine.ghost_drive_enumeration(target)

@app.post("/api/v1/stark/technique/physical_implant")
async def stark_physical_implant(payload: dict):
    """Technique 03: Social Engineering & Physical Implant Bridge (The Avengers 2012)."""
    device_id = payload.get("device_id", "STARK_DEVICE_01")
    return stark_hacking_engine.physical_implant_bridge(device_id)

@app.post("/api/v1/stark/technique/ai_cyber_ops")
async def stark_ai_cyber_ops(payload: dict):
    """Technique 04: AI-Assisted Cyber Operations & Triage (Age of Ultron 2015)."""
    logs = payload.get("logs", None)
    return stark_hacking_engine.ai_assisted_cyber_ops(logs)

@app.post("/api/v1/stark/technique/human_validation")
async def stark_human_validation(payload: dict):
    """Technique 05: Human Validation Escrow."""
    op = payload.get("operation", "system_change")
    approved = payload.get("approved", False)
    return stark_hacking_engine.human_validation_escrow(op, approved)

# --- Lightweight Fast Command Router (< 1ms Intent Matching) ---
from jarvis.system.command_router import command_router

@app.post("/api/v1/system/command/fast")
async def execute_fast_command(payload: dict):
    """Executes sub-millisecond intent matching for common voice and system commands."""
    cmd = payload.get("command", "")
    confirmed = payload.get("confirmed", False)
    return command_router.execute(cmd, user_confirmed=confirmed)

# --- CPU Survival & Performance Mode Governor ---
from jarvis.system.cpu_survival import cpu_survival_manager

@app.get("/api/v1/system/survival")
async def get_survival_telemetry():
    """Returns CPU Survival telemetry, active performance profile, and CPU utilization."""
    return cpu_survival_manager.get_telemetry()

@app.post("/api/v1/system/survival/set_mode")
async def set_survival_mode(payload: dict):
    """Sets performance mode: TURBO, BALANCED, or SURVIVAL."""
    mode = payload.get("mode", "BALANCED")
    success = cpu_survival_manager.set_mode(mode)
    if not success:
        raise HTTPException(status_code=400, detail=f"Invalid performance mode '{mode}'. Choose from TURBO, BALANCED, SURVIVAL.")
    return {
        "status": "mode_updated",
        "mode": cpu_survival_manager.mode,
        "profile": cpu_survival_manager.get_profile()
    }

# --- AST Code Graph & Graphify Engine Endpoints ---
from jarvis.analysis.code_graph import code_graph_engine

@app.get("/api/v1/graph/topology")
async def get_graph_topology():
    """Returns high-level graph topology metrics, clusters, and total AST nodes."""
    return code_graph_engine.get_topological_summary()

@app.get("/api/v1/graph/nodes")
async def get_graph_nodes():
    """Returns all extracted AST code nodes in the repository."""
    return [node.to_dict() for node in code_graph_engine.nodes.values()]

@app.get("/api/v1/graph/blast_radius")
async def get_node_blast_radius(node_id: str):
    """Calculates downstream dependencies and incoming callers for impact analysis."""
    if node_id not in code_graph_engine.nodes:
        # Try finding prefix/partial match
        for n in code_graph_engine.nodes:
            if node_id.lower() in n.lower():
                node_id = n
                break
    return code_graph_engine.get_blast_radius(node_id)

@app.post("/api/v1/graph/rebuild")
async def rebuild_code_graph():
    """Triggers real-time AST re-scanning and graphification of the repository."""
    code_graph_engine.rebuild_graph()
    return {
        "status": "rebuilt",
        "topology": code_graph_engine.get_topological_summary()
    }

def _perform_shutdown():
    time.sleep(1)
    os._exit(0)

@app.post("/api/v1/system/shutdown_bg")
async def shutdown_system_bg(background_tasks: BackgroundTasks):
    """Triggers graceful shutdown of the FastAPI Spine server."""
    background_tasks.add_task(_perform_shutdown)
    return {"status": "shutting_down", "message": "J.A.R.V.I.S. Core Spine is terminating..."}

if __name__ == "__main__":
    uvicorn.run(
        "jarvis.main:app",
        host="0.0.0.0",
        port=config.fastapi_port,
        reload=False,
        log_level="info"
    )
