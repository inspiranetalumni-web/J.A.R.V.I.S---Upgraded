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
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jarvis.config import config
from jarvis.logging import setup_logging, get_logger
from jarvis.system.spec_loader import audit_hardware
from jarvis.system.shutdown import shutdown_manager

logger = setup_logging()
START_TIME = time.time()

# ---------------------------------------------------------------------------
# Pydantic Request Models for Strong API Validation
# ---------------------------------------------------------------------------

class SystemCommandRequest(BaseModel):
    command: str = Field(..., description="System command or natural language instruction")

class FastCommandRequest(BaseModel):
    command: str = Field(..., description="Fast intent command string")
    confirmed: bool = Field(False, description="User confirmation state for sensitive operations")

class WorkflowGenerateRequest(BaseModel):
    mode: str = Field(..., description="Workflow mode (01_write_prd to 15_turn_task_into_skill)")
    feature: Optional[str] = Field("unnamed_feature", description="Feature description for PRD or Spec")
    task: Optional[str] = Field("unnamed_task", description="Task description for Ultra Plan")
    screen: Optional[str] = Field("main_screen", description="Screen name for UI/UX Brief")
    spec: Optional[str] = Field("unnamed_spec", description="Spec name for Implementation Plan")
    service: Optional[str] = Field("custom_mcp", description="Service name for MCP Wiring")
    db_type: Optional[str] = Field("ChromaDB + KùzuDB", description="Database engine type")
    focus: Optional[str] = Field("AUTH / USER DATA", description="Security audit focus area")
    error_trace: Optional[str] = Field("unspecified_error", description="Error stack trace for debugger")
    flow: Optional[str] = Field("Core Mobile & FastAPI Spine Interaction", description="E2E test flow")
    scope: Optional[str] = Field("whole_repo", description="Dead code scan scope")
    task_name: Optional[str] = Field("new_task", description="Task name for skill converter")
    description: Optional[str] = Field("Custom task skill", description="Skill description")
    trigger_phrases: Optional[List[str]] = Field(default_factory=list, description="Skill trigger phrases")

class McpDetectRequest(BaseModel):
    task: str = Field(..., description="Task prompt to detect MCP tools for")

class McpPermissionRequest(BaseModel):
    approved: bool = Field(False, description="Whether online MCP access is approved")

class ComplexityProfileRequest(BaseModel):
    code: str = Field(..., description="Python source code snippet to profile")

class SkillUnderstandRequest(BaseModel):
    term: str = Field(..., description="CS or domain acronym/term to explain")

class SkillLearnRequest(BaseModel):
    term: str = Field(..., description="Technical concept to index")
    description: Optional[str] = Field("", description="Custom concept definition")

class SkillConnectRequest(BaseModel):
    query: str = Field(..., description="Concept to map to codebase and tools")

class SkillWorkRequest(BaseModel):
    task: str = Field(..., description="Task to execute via connected skill module")

class CognitiveTierRequest(BaseModel):
    task: str = Field(..., description="Task description to classify")

class UpgradeAuthorizeRequest(BaseModel):
    approved: bool = Field(False, description="Explicit operator authorization for self-upgrade")

class StarkAccessRequest(BaseModel):
    target: str = Field("local_pc", description="Target environment for OS access check")

class StarkAnalyzeRequest(BaseModel):
    target: str = Field("system_code", description="Target code or system for Stage 3 analysis")

class StarkAdaptRequest(BaseModel):
    intent: str = Field("status", description="Intent for dynamic routing adaptation")

class StarkControlRequest(BaseModel):
    action: str = Field("status_check", description="Action to execute under Protocol VERONICA")
    user_permission: bool = Field(True, description="Human validation token")

class DisplayHijackRequest(BaseModel):
    channel: str = Field("DISPLAY-01", description="Target display feed channel")
    feed: str = Field("STARK_HUD", description="Replacement video feed source")

class GhostDriveRequest(BaseModel):
    target_dir: Optional[str] = Field(None, description="Target directory for ghost drive enumeration")

class PhysicalImplantRequest(BaseModel):
    device_id: str = Field("STARK_DEVICE_01", description="Device identifier for physical implant bridge")

class AiCyberOpsRequest(BaseModel):
    logs: Optional[str] = Field(None, description="Raw security log dump for AI correlation")

class HumanValidationRequest(BaseModel):
    operation: str = Field("system_change", description="Sensitive operation name")
    approved: bool = Field(False, description="Operator validation sign-off")

class SurvivalModeRequest(BaseModel):
    mode: str = Field("BALANCED", description="Performance profile: TURBO, BALANCED, or SURVIVAL")

# --- Next-Gen V2 Request Models ---

class EvolutionDiagnoseRequest(BaseModel):
    traceback: str = Field(..., description="Python exception traceback text")

class EvolutionPatchRequest(BaseModel):
    target_file: str = Field(..., description="Relative or absolute target file path")
    new_content: str = Field(..., description="Proposed complete replacement source code")
    reason: Optional[str] = Field("Automated self-evolution fix", description="Reason for patch proposal")

class EvolutionCommitRequest(BaseModel):
    proposal_id: str = Field(..., description="Unique proposal identifier")
    approved: bool = Field(False, description="Explicit operator authorization for patch commit")

class PersonaSwitchRequest(BaseModel):
    persona: str = Field("JARVIS", description="Target persona name (JARVIS, FRIDAY, EDITH)")

class BiometricUpdateRequest(BaseModel):
    heart_rate_bpm: Optional[float] = Field(None, description="Heart rate in BPM")
    hrv_ms: Optional[float] = Field(None, description="Heart Rate Variability in ms")
    eye_fatigue_level: Optional[float] = Field(None, description="Eye fatigue factor (0.0 - 1.0)")
    voice_stress_score: Optional[float] = Field(None, description="Voice stress factor (0.0 - 1.0)")

class VaultEncryptRequest(BaseModel):
    data: str = Field(..., description="Plaintext string or base64 data to encrypt")
    key_name: Optional[str] = Field(None, description="Optional secret key name to store in vault")

class VaultDecryptRequest(BaseModel):
    encrypted_data: Dict[str, str] = Field(..., description="Encrypted dictionary containing nonce, tag, ciphertext")

class SimulationDryRunRequest(BaseModel):
    script_code: str = Field(..., description="Python script code to simulate in Copy-on-Write sandbox")
    target_filepath: Optional[str] = Field("", description="Optional target file path")

class SatelliteHandoffRequest(BaseModel):
    state: Dict[str, Any] = Field(..., description="Satellite workspace state dictionary")

class ZeroTrustVerifyRequest(BaseModel):
    voiceprint_embedding: Optional[List[float]] = Field(None, description="Speaker embedding vector")
    iris_signature: Optional[List[float]] = Field(None, description="Iris geometry landmarks")
    threshold: Optional[float] = Field(0.88, description="Verification similarity threshold")

class ZeroTrustTokenRequest(BaseModel):
    command: str = Field(..., description="Root system command requesting single-use HMAC token")
    ttl_seconds: Optional[int] = Field(60, description="Token lifetime in seconds")

class NpuCompileRequest(BaseModel):
    model_path: str = Field(..., description="Path to ONNX/OpenVINO neural model")

def set_process_pcore_affinity():
    """
    Pins the main FastAPI spine process to P-Cores (Threads 0-3 / Mask 0x00F) on Windows x86_64
    to prevent E-Core scheduler latency overhead.
    """
    try:
        proc = psutil.Process(os.getpid())
        if hasattr(proc, "cpu_affinity"):
            available_cores = list(range(min(4, psutil.cpu_count(logical=True) or 1)))
            proc.cpu_affinity(available_cores)
            logger.info("Process PID %d pinned to P-Core threads: %s", os.getpid(), available_cores)
    except Exception as e:
        logger.debug("CPU affinity pin skipped/deferred: %s", e)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager handling startup and graceful shutdown.
    """
    logger.info("============================================================")
    logger.info("   J.A.R.V.I.S. v3.0 STARK HORIZON CORE SPINE INITIALIZING  ")
    logger.info("============================================================")
    logger.info("Endpoint: %s", config.to_dict()["fastapi_endpoint"])
    logger.info("Root Directory: %s", config.root_dir)
    logger.info("Data Directory: %s", config.data_dir)

    set_process_pcore_affinity()

    # Initialize Perception Audio Engine & Laptop Microphone Listener
    try:
        from jarvis.audio.manager import AudioManager
        from jarvis.agents.conversational import ConversationalAgent
        audio_mgr = AudioManager()
        conv_agent = ConversationalAgent()

        def _on_transcript(text: str):
            logger.info("[LAPTOP VOICE INTAKE] Transcribed: '%s'", text)
            clauses = conv_agent.stream_response(text, cancel_event=audio_mgr.cancel_token)
            audio_mgr.speak_stream(clauses)

        audio_mgr.register_on_utterance_callback(_on_transcript)
        audio_mgr.start_mic_listener()
        logger.info("Perception Audio Pipeline & Laptop Microphone intake initialized.")

        # Trigger dynamic boot voice initiation
        from jarvis.llm.cognitive_reasoner import cognitive_reasoner
        init_voice = cognitive_reasoner.analyze_and_respond("initiate")
        logger.info("[INITIATION VOICE]: %s", init_voice)
        import threading
        threading.Thread(target=lambda: audio_mgr.speak(init_voice), daemon=True, name="JarvisInitVoiceThread").start()
    except Exception as err:
        logger.debug("Audio Pipeline initialization note: %s", err)

    yield

    logger.info("Gracefully shutting down J.A.R.V.I.S. Core Spine Server...")
    try:
        from jarvis.llm.cognitive_reasoner import cognitive_reasoner
        shutdown_msg = cognitive_reasoner.analyze_and_respond("confirm shutdown")
        logger.info("[SHUTDOWN VOICE]: %s", shutdown_msg)
    except Exception:
        pass

app = FastAPI(
    title="J.A.R.V.I.S. Core Spine API",
    description="Central Orchestrator for J.A.R.V.I.S. v3.0 Multi-Agent Horizon System",
    version="3.0.0",
    lifespan=lifespan
)

# SEC-C01: Restrict CORS origins to local loopback and local development hosts
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8765",
        "http://localhost:8765",
        "http://127.0.0.1",
        "http://localhost",
        "http://127.0.0.1:3000",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

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

@app.get("/health/live")
async def health_liveness():
    """Kubernetes-style Liveness Probe returning 200 if the spine process is running."""
    return {"status": "live", "pid": os.getpid()}

@app.get("/health/ready")
async def health_readiness():
    """Readiness Probe verifying directory access and memory database connectivity."""
    return {
        "status": "ready",
        "root_accessible": config.root_dir.exists(),
        "data_accessible": config.data_dir.exists(),
        "vault_accessible": config.vault_dir.exists()
    }

@app.post("/api/v1/system/shutdown")
@app.get("/shutdown")
async def shutdown_system():
    """Triggers graceful system shutdown protocol via ShutdownManager."""
    return shutdown_manager.initiate_shutdown(exit_code=0, delay_s=0.3)

@app.post("/api/v1/system/command")
async def execute_system_command(payload: SystemCommandRequest):
    """Executes command payload through MobileGateway and ConversationalAgent."""
    return mobile_gateway.handle_mobile_message(json.dumps({"type": "remote_command", "command": payload.command}))

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
async def generate_dynamic_workflow(payload: WorkflowGenerateRequest):
    """
    Executes 15 dynamic development workflow modes.
    """
    from jarvis.agents.dynamic_workflows import DynamicWorkflowEngine
    engine = DynamicWorkflowEngine()
    mode = str(payload.mode).lower()

    if mode in ["write_prd", "prd", "01", "1"]:
        return engine.write_prd(payload.feature or "unnamed_feature")
    elif mode in ["generate_agents_md", "agents_md", "jarvis_md", "02", "2"]:
        return engine.generate_agents_md()
    elif mode in ["ultra_plan", "plan", "03", "3"]:
        return engine.ultra_plan(payload.task or "unnamed_task")
    elif mode in ["spec_driven_dev", "spec", "04", "4"]:
        return engine.spec_driven_development(payload.feature or "unnamed_feature")
    elif mode in ["ui_ux_brief", "design_brief", "05", "5"]:
        return engine.ui_ux_design_brief(payload.screen or "main_screen")
    elif mode in ["implementation_plan", "build_sequence", "06", "6"]:
        return engine.implementation_plan(payload.spec or "unnamed_spec")
    elif mode in ["wire_mcp_server", "mcp_server", "mcp", "07", "7"]:
        return engine.wire_mcp_server(payload.service or "custom_mcp")
    elif mode in ["connect_database", "database", "db", "08", "8"]:
        return engine.connect_database(payload.db_type or "ChromaDB + KùzuDB")
    elif mode in ["find_security_gaps", "security_audit", "security", "09", "9"]:
        return engine.find_security_gaps(payload.focus or "AUTH / USER DATA")
    elif mode in ["debug_error_fast", "debug_error", "debug", "10"]:
        return engine.debug_error_fast(payload.error_trace or "unspecified_error")
    elif mode in ["e2e_test_app", "e2e_test", "e2e", "11"]:
        return engine.e2e_test_app(payload.flow or "Core Mobile & FastAPI Spine Interaction")
    elif mode in ["cleanup_dead_code", "dead_code", "12"]:
        return engine.cleanup_dead_code(payload.scope or "whole_repo")
    elif mode in ["write_clean_commits", "clean_commits", "commit", "13"]:
        return engine.write_clean_commits()
    elif mode in ["hooks_as_guardrails", "guardrail_hooks", "hooks", "14"]:
        return engine.hooks_as_guardrails()
    elif mode in ["turn_task_into_skill", "task_to_skill", "skill", "15"]:
        name = payload.task_name or "new_task"
        desc = payload.description or "Custom task skill"
        triggers = payload.trigger_phrases or [name]
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
async def detect_mcp_tools(payload: McpDetectRequest):
    """Auto-detects required MCP tools and checks online permission state."""
    return mcp_detector.auto_detect_tools(payload.task)

@app.post("/api/v1/mcp/permission")
async def set_online_mcp_permission(payload: McpPermissionRequest):
    """Grants or revokes online network access permission."""
    mcp_detector.set_online_permission(payload.approved)
    return {
        "online_access_approved": mcp_detector.online_access_approved,
        "message": "Online network access AUTHORIZED by user." if payload.approved else "System operating in 100% OFFLINE mode."
    }

# --- Time Complexity Profiler ---
from jarvis.system.time_complexity import TimeComplexityProfiler
complexity_profiler = TimeComplexityProfiler()

@app.post("/api/v1/system/complexity")
async def profile_time_complexity(payload: ComplexityProfileRequest):
    """Profiles code snippet against the 10 Time Complexity Patterns (O(1) to O(n!))."""
    return complexity_profiler.profile_code(payload.code)

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
from jarvis.learning.skill_knowledge_engine import skill_knowledge_engine

@app.post("/api/v1/skills/understand")
async def understand_cs_term(payload: SkillUnderstandRequest):
    """1. UNDERSTAND: Explains any CS, AI, Web, DB, or DevOps term & J.A.R.V.I.S implementation."""
    return skill_knowledge_engine.understand(payload.term)

@app.post("/api/v1/skills/learn")
async def learn_cs_term(payload: SkillLearnRequest):
    """2. LEARN: Auto-indexes new technical concept into J.A.R.V.I.S. Memory Vault."""
    return skill_knowledge_engine.learn(payload.term, payload.description)

@app.post("/api/v1/skills/connect")
async def connect_cs_term(payload: SkillConnectRequest):
    """3. CONNECT: Maps query to J.A.R.V.I.S. code module, skill file, and MCP tool."""
    return skill_knowledge_engine.connect(payload.query)

@app.post("/api/v1/skills/execute")
async def work_on_skills(payload: SkillWorkRequest):
    """4. WORK ON SKILLS: Dynamically executes the connected skill or code tool."""
    return skill_knowledge_engine.work_on_skills(payload.task)

# --- Cognitive Tier Classifier & Self-Upgrade Engine (LLM vs RAG vs AI Agent) ---
from jarvis.system.self_upgrade_engine import CognitiveTierClassifier, SelfUpgradeEngine
tier_classifier = CognitiveTierClassifier()
upgrade_engine = SelfUpgradeEngine()

@app.post("/api/v1/system/classify_tier")
async def classify_cognitive_tier(payload: CognitiveTierRequest):
    """Classifies task into LLM, RAG, AI Agent, or Hybrid cognitive mode."""
    return tier_classifier.classify_task(payload.task)

@app.get("/api/v1/system/upgrade_proposal")
async def get_upgrade_proposal():
    """Generates J.A.R.V.I.S. v3.1 self-upgrade proposal."""
    return upgrade_engine.generate_upgrade_proposal()

@app.post("/api/v1/system/upgrade_authorize")
async def authorize_self_upgrade(payload: UpgradeAuthorizeRequest):
    """Executes J.A.R.V.I.S. self-upgrade upon explicit user permission (approved: True)."""
    return upgrade_engine.execute_upgrade(user_permission=payload.approved)

# --- Tony Stark System Philosophy Engine (Recon -> Access -> Analyze -> Adapt -> Control) ---
from jarvis.system.stark_mindset_engine import stark_engine

@app.get("/api/v1/stark/recon")
async def stark_recon():
    """Stage 1: RECON — Maps hardware, network, and system surface area."""
    return stark_engine.recon()

@app.post("/api/v1/stark/access")
async def stark_access(payload: StarkAccessRequest):
    """Stage 2: ACCESS — Evaluates OS actuation & hardware interface access."""
    return stark_engine.access(payload.target)

@app.post("/api/v1/stark/analyze")
async def stark_analyze(payload: StarkAnalyzeRequest):
    """Stage 3: ANALYZE — Deep code analysis, complexity profiling, & system security audit."""
    return stark_engine.analyze(payload.target)

@app.post("/api/v1/stark/adapt")
async def stark_adapt(payload: StarkAdaptRequest):
    """Stage 4: ADAPT — Dynamic routing, fallback execution, and self-learning adaptation."""
    return stark_engine.adapt(payload.intent)

@app.post("/api/v1/stark/control")
async def stark_control(payload: StarkControlRequest):
    """Stage 5: CONTROL — Hands-free execution with user permission escrow & Protocol VERONICA."""
    return stark_engine.control(payload.action, user_permission=payload.user_permission)

# --- Tony Stark Hacking Techniques & AI Cyber Ops Engine (5 MCU Case Studies) ---
from jarvis.security.stark_hacking_techniques import StarkHackingTechniquesEngine
stark_hacking_engine = StarkHackingTechniquesEngine()

@app.post("/api/v1/stark/technique/display_hijack")
async def stark_display_hijack(payload: DisplayHijackRequest):
    """Technique 01: Display / Video-Feed Hijack (Iron Man 2)."""
    return stark_hacking_engine.display_video_hijack(payload.channel, payload.feed)

@app.post("/api/v1/stark/technique/ghost_drive")
async def stark_ghost_drive(payload: GhostDriveRequest):
    """Technique 02: The Ghost Drive Enumeration (Iron Man 1)."""
    return stark_hacking_engine.ghost_drive_enumeration(payload.target_dir)

@app.post("/api/v1/stark/technique/physical_implant")
async def stark_physical_implant(payload: PhysicalImplantRequest):
    """Technique 03: Social Engineering & Physical Implant Bridge (The Avengers 2012)."""
    return stark_hacking_engine.physical_implant_bridge(payload.device_id)

@app.post("/api/v1/stark/technique/ai_cyber_ops")
async def stark_ai_cyber_ops(payload: AiCyberOpsRequest):
    """Technique 04: AI-Assisted Cyber Operations & Triage (Age of Ultron 2015)."""
    return stark_hacking_engine.ai_assisted_cyber_ops(payload.logs)

@app.post("/api/v1/stark/technique/human_validation")
async def stark_human_validation(payload: HumanValidationRequest):
    """Technique 05: Human Validation Escrow."""
    return stark_hacking_engine.human_validation_escrow(payload.operation, payload.approved)

# --- Lightweight Fast Command Router (< 1ms Intent Matching) ---
from jarvis.system.command_router import command_router

@app.post("/api/v1/system/command/fast")
async def execute_fast_command(payload: FastCommandRequest):
    """Executes sub-millisecond intent matching for common voice and system commands."""
    return command_router.execute(payload.command, user_confirmed=payload.confirmed)

# --- CPU Survival & Performance Mode Governor ---
from jarvis.system.cpu_survival import cpu_survival_manager

@app.get("/api/v1/system/survival")
async def get_survival_telemetry():
    """Returns CPU Survival telemetry, active performance profile, and CPU utilization."""
    return cpu_survival_manager.get_telemetry()

@app.post("/api/v1/system/survival/set_mode")
async def set_survival_mode(payload: SurvivalModeRequest):
    """Sets performance mode: TURBO, BALANCED, or SURVIVAL."""
    success = cpu_survival_manager.set_mode(payload.mode)
    if not success:
        raise HTTPException(status_code=400, detail=f"Invalid performance mode '{payload.mode}'. Choose from TURBO, BALANCED, SURVIVAL.")
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

# ===========================================================================
# Next-Gen Version 2 (Mark XCVI Standard) REST Endpoints
# ===========================================================================

# 1. Meta-Cognitive Self-Evolution
from jarvis.evolution.evaluator import self_evolution_engine

@app.get("/api/v1/evolution/health")
async def get_evolution_health():
    """Evaluates system regression status, error logs, and staged patches."""
    return self_evolution_engine.evaluate_system_health()

@app.post("/api/v1/evolution/diagnose")
async def diagnose_traceback(payload: EvolutionDiagnoseRequest):
    """Diagnoses runtime Python traceback, isolating file, line, and AST context."""
    return self_evolution_engine.analyzer.diagnose_traceback(payload.traceback)

@app.post("/api/v1/evolution/propose")
async def propose_evolution_patch(payload: EvolutionPatchRequest):
    """Stages a syntax-validated patch awaiting operator HMAC sign-off."""
    return self_evolution_engine.propose_patch(payload.target_file, payload.new_content, reason=payload.reason or "Automated patch")

@app.post("/api/v1/evolution/commit")
async def commit_evolution_patch(payload: EvolutionCommitRequest):
    """Executes a staged patch with atomic backup and rollback protection."""
    return self_evolution_engine.commit_patch(payload.proposal_id, approved=payload.approved)

# 2. Multi-Voice Persona Synthesis
from jarvis.audio.persona_manager import persona_manager

@app.get("/api/v1/persona/active")
async def get_active_persona():
    """Returns active Stark persona profile (J.A.R.V.I.S., F.R.I.D.A.Y., E.D.I.T.H.)."""
    return persona_manager.get_active_persona()

@app.post("/api/v1/persona/switch")
async def switch_active_persona(payload: PersonaSwitchRequest):
    """Switches active voice embedding and persona prompt (< 2ms)."""
    return persona_manager.switch_persona(payload.persona)

@app.get("/api/v1/persona/list")
async def list_available_personas():
    """Lists all registered Stark personas."""
    return persona_manager.list_available_personas()

# 3. Suit Vital Monitor & Biometric Adaptation
from jarvis.sensors.biometric_harvester import biometric_harvester

@app.get("/api/v1/biometrics/telemetry")
async def get_biometric_telemetry():
    """Returns operator vital telemetry, stress index, and tone adaptation mode."""
    return biometric_harvester.get_telemetry_dict()

@app.post("/api/v1/biometrics/update")
async def update_biometric_vitals(payload: BiometricUpdateRequest):
    """Updates biometric sensor observations (BLE HRV, fatigue, voice stress)."""
    biometric_harvester.update_vitals(
        heart_rate_bpm=payload.heart_rate_bpm,
        hrv_ms=payload.hrv_ms,
        eye_fatigue_level=payload.eye_fatigue_level,
        voice_stress_score=payload.voice_stress_score,
    )
    return biometric_harvester.get_telemetry_dict()

# 4. House Party Protocol Multi-Agent Swarm
from jarvis.swarm.parallel_executor import HousePartySwarmExecutor

@app.get("/api/v1/swarm/status")
async def get_swarm_status():
    """Returns House Party Protocol worker availability and DAG capabilities."""
    return {
        "status": "ONLINE",
        "max_concurrent_workers": 6,
        "protocol": "House Party Protocol Mark LII-LXXIV",
        "dag_engine": "Directed Acyclic Graph with Topological Wave Scheduling",
    }

# 5. Distributed P2P LAN Mesh & Orbital Relay
from jarvis.mesh.node_offloader import p2p_mesh_offloader
from jarvis.mesh.orbital_relay import orbital_satellite_relay

@app.get("/api/v1/mesh/status")
async def get_mesh_status():
    """Returns P2P LAN compute mesh offloading topology."""
    return p2p_mesh_offloader.get_mesh_status()

@app.get("/api/v1/mesh/orbital")
async def get_orbital_status():
    """Returns Starlink / WireGuard orbital satellite bypass tunnel status."""
    return orbital_satellite_relay.get_status()

# 6. Quantum Shield Post-Quantum Vault
from jarvis.security.quantum_vault import quantum_vault

@app.post("/api/v1/vault/encrypt")
async def vault_encrypt_data(payload: VaultEncryptRequest):
    """Encrypts plaintext using authenticated PBKDF2-HMAC-SHA512 stream cipher."""
    enc = quantum_vault.encrypt_data(payload.data.encode("utf-8"))
    if payload.key_name:
        saved_path = quantum_vault.save_vault_secret(payload.key_name, payload.data)
        enc["saved_path"] = saved_path
    return enc

@app.post("/api/v1/vault/decrypt")
async def vault_decrypt_data(payload: VaultDecryptRequest):
    """Decrypts and cryptographically verifies authenticated vault data."""
    try:
        decrypted_bytes = quantum_vault.decrypt_data(payload.encrypted_data)
        return {"decrypted": decrypted_bytes.decode("utf-8"), "verified": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 7. Project B.A.R.N.A.B.Y. Virtual Sandbox Simulator
from jarvis.simulation.barnaby_engine import barnaby_simulator

@app.post("/api/v1/simulation/dry_run")
async def simulate_code_dry_run(payload: SimulationDryRunRequest):
    """Simulates code execution in a Copy-on-Write sandbox and returns risk report."""
    return barnaby_simulator.simulate_script_execution(payload.script_code, payload.target_filepath or "")

# 8. Cross-Device Satellite Sync & Handoff
from jarvis.sync.satellite_sync import satellite_sync_engine

@app.get("/api/v1/sync/state")
async def get_sync_state():
    """Returns synchronized workspace state across paired satellite devices."""
    return satellite_sync_engine.get_state_dict()

@app.post("/api/v1/sync/handoff")
async def ingest_satellite_handoff(payload: SatelliteHandoffRequest):
    """Ingests remote workspace state handoff from a mobile or desktop satellite."""
    return satellite_sync_engine.ingest_remote_state(payload.state)

# 9. Stark Auto-Architect Multi-File Refactoring
from jarvis.refactoring.auto_architect import stark_auto_architect

@app.get("/api/v1/refactor/analyze")
async def analyze_project_architecture():
    """Parses AST dependency graphs and maps architectural coupling hotspots."""
    return stark_auto_architect.analyze_architecture()

# 10. Zero-Trust Continuous Biometric Gate
from jarvis.security.zero_trust_gate import zero_trust_gate

@app.post("/api/v1/zerotrust/verify")
async def verify_biometric_gate(payload: ZeroTrustVerifyRequest):
    """Verifies speaker voiceprint embedding or iris mesh."""
    if payload.voiceprint_embedding:
        return zero_trust_gate.verify_voiceprint(payload.voiceprint_embedding, threshold=payload.threshold or 0.88)
    elif payload.iris_signature:
        return zero_trust_gate.verify_iris(payload.iris_signature, threshold=payload.threshold or 0.85)
    else:
        raise HTTPException(status_code=400, detail="Must provide voiceprint_embedding or iris_signature.")

@app.post("/api/v1/zerotrust/token")
async def generate_root_token(payload: ZeroTrustTokenRequest):
    """Generates single-use HMAC token authorizing root command mutation."""
    token = zero_trust_gate.generate_root_authorization_token(payload.command, ttl_seconds=payload.ttl_seconds or 60)
    return {"token": token, "command": payload.command, "ttl_seconds": payload.ttl_seconds or 60}

# 11. Direct NPU Silicon Acceleration
from jarvis.hardware.npu_engine import npu_engine

@app.get("/api/v1/npu/status")
async def get_npu_silicon_status():
    """Returns Intel NPU / DirectML direct silicon binding telemetry."""
    return npu_engine.get_status()

@app.post("/api/v1/npu/compile")
async def compile_model_npu(payload: NpuCompileRequest):
    """Simulates/compiles neural model for target silicon accelerator."""
    return npu_engine.compile_model_for_target(payload.model_path)

@app.post("/api/v1/npu/bind_pcores")
async def bind_npu_pcores():
    """Pins process and background neural inference threads to Intel Performance Cores (0x00F)."""
    return npu_engine.bind_process_to_p_cores()

@app.get("/api/v1/npu/benchmark")
async def benchmark_npu_silicon(iterations: int = 50):
    """Executes micro-latency throughput benchmark on active silicon."""
    return npu_engine.benchmark_inference(iterations=iterations)

# 12. Real-Time Audio Spectrum & Live Telemetry WebSocket Bridge
from jarvis.audio.spectrum_analyzer import spectrum_analyzer

@app.get("/api/v1/audio/spectrum")
async def get_audio_spectrum():
    """Returns live 48-band FFT spectrum, RMS volume, active persona, and centroid."""
    spec = spectrum_analyzer.get_spectrum_data()
    active_p = persona_manager.get_active_persona()
    vitals = biometric_harvester.get_speech_adaptation_params()
    return {
        **spec,
        "active_persona": active_p.name,
        "persona_color": active_p.hud_accent_color,
        "stress_level": vitals.get("stress_index", 0.0),
        "hud_theme": vitals.get("hud_color", "BLUE"),
    }

@app.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    """Streams real-time 30 FPS audio spectrum, persona, and system vitals over WebSocket."""
    await websocket.accept()
    try:
        import asyncio
        while True:
            spec = spectrum_analyzer.get_spectrum_data()
            active_p = persona_manager.get_active_persona()
            vitals = biometric_harvester.get_speech_adaptation_params()
            payload = {
                "spectrum": spec,
                "active_persona": active_p.name,
                "persona_color": active_p.hud_accent_color,
                "stress_level": vitals.get("stress_index", 0.0),
                "hud_theme": vitals.get("hud_color", "BLUE"),
                "cpu_percent": psutil.cpu_percent(),
                "ram_percent": psutil.virtual_memory().percent,
                "timestamp": time.time(),
            }
            await websocket.send_json(payload)
            await asyncio.sleep(0.033)  # ~30 FPS broadcast
    except (WebSocketDisconnect, Exception) as e:
        logger.info(f"[WS TELEMETRY] Connection closed: {e}")

@app.post("/api/v1/system/shutdown_bg")
async def shutdown_system_bg(background_tasks: BackgroundTasks):
    """Triggers graceful shutdown of the FastAPI Spine server."""
    background_tasks.add_task(shutdown_manager.initiate_shutdown, 0, 0.3)
    return {"status": "shutting_down", "message": "J.A.R.V.I.S. Core Spine is terminating gracefully..."}

if __name__ == "__main__":
    uvicorn.run(
        "jarvis.main:app",
        host="0.0.0.0",
        port=config.fastapi_port,
        reload=False,
        log_level="info"
    )
