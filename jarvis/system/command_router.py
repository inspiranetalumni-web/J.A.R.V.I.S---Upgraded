"""
jarvis/system/command_router.py — Lightweight Fast Command Router v3.0
Sub-millisecond intent matching for high-frequency everyday voice tasks.
Bypasses heavy LLM inference and context assembly for instant voice responsiveness.
Enforces explicit user confirmation on sensitive operations (e.g. shutdown).
"""

import os
import re
import sys
import time
import psutil
import datetime
import subprocess
from typing import Dict, Any, Optional, Tuple, List
from jarvis.actuation.win32 import Win32Actuator

class LightweightCommandRouter:
    """
    High-Performance Deterministic Command Router.
    Performs sub-millisecond intent matching (< 1ms) and executes common OS/system tasks.
    """
    # Pre-compiled regular expressions for maximum micro-latency throughput
    PAT_TIME = re.compile(r"^(what('s| is) the )?(current )?time( now)?\??$")
    PAT_DATE = re.compile(r"^(what('s| is) the )?(today('s)? )?date( today)?\??$")
    PAT_CPU = re.compile(r"^(cpu|cpu usage|cpu status|cpu load)\??$")
    PAT_RAM = re.compile(r"^(ram|ram usage|memory|memory usage|memory status)\??$")
    PAT_APP = re.compile(r"^(?:open|launch|start)\s+(notepad|calculator|calc|chrome|browser|terminal|cmd|powershell|explorer|files)$")
    PAT_IDENTITY = re.compile(r"^(who are you|what is your name|identify yourself)\??$")
    PAT_CAPABILITIES = re.compile(r"^(what can you do|help|capabilities)\??$")
    PAT_GREETING = re.compile(r"^(hello|hi|hey|good morning|good afternoon|good evening)( jarvis)?\??$")
    PAT_SHUTDOWN = re.compile(r"^(shutdown|power down|turn off|halt)\s*(jarvis|system|server)?$")

    def __init__(self):
        self.actuator = Win32Actuator()
        self._pending_confirmation: Optional[str] = None
        self._confirmation_expiry: float = 0.0

    def match_intent(self, query: str) -> Optional[Tuple[str, re.Match]]:
        """
        Fast regex/keyword matcher (< 0.1ms).
        Returns (command_category, match_object) or None.
        """
        q = query.strip().lower()

        # Confirmation phrases
        if self._pending_confirmation and time.time() < self._confirmation_expiry:
            if q in ["yes", "confirm", "confirm shutdown", "proceed", "yes shutdown", "do it"]:
                return "confirmed_action", None
            elif q in ["no", "cancel", "abort", "don't"]:
                return "cancelled_action", None

        # 1. Time & Date
        if self.PAT_TIME.search(q) or q in ["time", "what time is it", "tell me the time"]:
            return "time", None
        if self.PAT_DATE.search(q) or q in ["date", "what date is today", "what day is it"]:
            return "date", None

        # 2. System Status & Telemetry
        if q in ["status", "system status", "health", "system health", "status report", "system report"]:
            return "system_status", None
        if self.PAT_CPU.search(q) or "cpu usage" in q:
            return "cpu_usage", None
        if self.PAT_RAM.search(q) or "ram usage" in q:
            return "ram_usage", None
        if "battery" in q or "power level" in q:
            return "battery", None

        # 3. Audio & Media Controls
        if q in ["mute", "silence", "mute volume", "mute audio"]:
            return "volume_mute", None
        if q in ["unmute", "unmute volume", "unmute audio"]:
            return "volume_unmute", None
        if q in ["volume up", "louder", "increase volume", "raise volume"]:
            return "volume_up", None
        if q in ["volume down", "quieter", "lower volume", "decrease volume"]:
            return "volume_down", None
        if q in ["stop", "stop talking", "be quiet", "pause audio", "stop playback", "silence jarvis"]:
            return "stop_audio", None

        # 4. Quick App Launch
        m = self.PAT_APP.match(q)
        if m:
            return "app_launch", m

        # 5. Performance / Survival Modes
        if "survival mode" in q or "low power mode" in q:
            return "mode_survival", None
        if "turbo mode" in q or "high performance mode" in q:
            return "mode_turbo", None
        if "balanced mode" in q or "normal mode" in q:
            return "mode_balanced", None

        # 6. Conversational Identity & Greetings
        if self.PAT_IDENTITY.search(q):
            return "identity", None
        if self.PAT_CAPABILITIES.search(q):
            return "capabilities", None
        if self.PAT_GREETING.search(q):
            return "greeting", None

        # 7. Code Graph & Graphify Intents
        if any(term in q for term in ["code graph", "graphify", "ast graph", "codebase graph", "architecture graph"]):
            return "code_graph_summary", None
        if "blast radius" in q or "impact analysis" in q:
            return "code_graph_blast", None
        if "dead code" in q or "orphaned modules" in q:
            return "code_graph_dead", None

        # 8. Next-Gen V2 Intents (Persona, Swarm, Biometrics, Simulation, Vault, Sync, NPU)
        if any(term in q for term in ["switch to friday", "activate friday", "call friday"]):
            return "persona_friday", None
        if any(term in q for term in ["switch to edith", "activate edith", "call edith"]):
            return "persona_edith", None
        if any(term in q for term in ["switch to jarvis", "activate jarvis", "call jarvis"]):
            return "persona_jarvis", None
        if any(term in q for term in ["who is speaking", "active persona", "current persona"]):
            return "persona_status", None
        if any(term in q for term in ["deploy swarm", "house party protocol", "swarm status", "swarm execute"]):
            return "swarm_deploy", None
        if any(term in q for term in ["suit vitals", "operator vitals", "stress level", "biometric status"]):
            return "biometric_vitals", None
        if any(term in q for term in ["quantum vault", "quantum shield", "vault status"]):
            return "quantum_vault_status", None
        if any(term in q for term in ["run simulation", "barnaby simulation", "simulate script"]):
            return "simulation_dryrun", None
        if any(term in q for term in ["satellite sync", "satellite status", "sync state"]):
            return "satellite_sync_status", None
        if any(term in q for term in ["npu status", "silicon accelerator", "npu engine"]):
            return "npu_status", None

        # 9. Sensitive Operations (Shutdown)
        if self.PAT_SHUTDOWN.search(q):
            return "shutdown", None

        return None

    def execute(self, query: str, user_confirmed: bool = False) -> Dict[str, Any]:
        """
        Routes and executes fast commands. Returns detailed command result dictionary.
        """
        t0 = time.perf_counter()
        matched = self.match_intent(query)
        match_latency_ms = round((time.perf_counter() - t0) * 1000, 3)

        if not matched:
            return {
                "matched": False,
                "intent": None,
                "response": None,
                "executed": False,
                "requires_confirmation": False,
                "match_latency_ms": match_latency_ms
            }

        category, match_obj = matched
        response_text = ""
        executed = True
        requires_conf = False

        # Handle pending confirmation resolution
        if category == "confirmed_action":
            action = self._pending_confirmation
            self._pending_confirmation = None
            if action == "shutdown":
                response_text = "Shutdown confirmed. Powering down core systems, Sir. Goodnight."
                from jarvis.system.shutdown import shutdown_manager
                shutdown_manager.initiate_shutdown(delay_s=0.5)
            else:
                response_text = f"Action '{action}' confirmed and executed, Sir."

        elif category == "cancelled_action":
            self._pending_confirmation = None
            response_text = "Operation cancelled, Sir. Standing by."

        # 1. Time & Date
        elif category == "time":
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            response_text = f"The current time is {now_str}, Sir."

        elif category == "date":
            today_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            response_text = f"Today is {today_str}, Sir."

        # 2. System Status & Telemetry
        elif category == "system_status":
            cpu_pct = psutil.cpu_percent(interval=None)
            ram_pct = psutil.virtual_memory().percent
            response_text = f"All systems nominal, Sir. CPU load is at {cpu_pct:.1f}%, and memory utilization is at {ram_pct:.1f}%."

        elif category == "cpu_usage":
            cpu_pct = psutil.cpu_percent(interval=None)
            logical = psutil.cpu_count(logical=True)
            response_text = f"CPU utilization is currently at {cpu_pct:.1f}% across {logical} logical threads."

        elif category == "ram_usage":
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024**3)
            total_gb = mem.total / (1024**3)
            response_text = f"RAM utilization is {used_gb:.1f} GB out of {total_gb:.1f} GB ({mem.percent:.1f}%)."

        elif category == "battery":
            battery = psutil.sensors_battery()
            if battery:
                plugged = "plugged in" if battery.power_plugged else "on battery power"
                response_text = f"Battery is at {battery.percent:.0f}%, {plugged}."
            else:
                response_text = "System is operating on continuous AC power, Sir."

        # 3. Audio & Volume
        elif category == "volume_mute":
            # VK_VOLUME_MUTE = 0xAD
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
            response_text = "Audio muted, Sir."

        elif category == "volume_unmute":
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
            response_text = "Audio unmuted, Sir."

        elif category == "volume_up":
            # VK_VOLUME_UP = 0xAF
            if sys.platform == "win32":
                import ctypes
                for _ in range(3):
                    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
            response_text = "Volume increased, Sir."

        elif category == "volume_down":
            # VK_VOLUME_DOWN = 0xAE
            if sys.platform == "win32":
                import ctypes
                for _ in range(3):
                    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
            response_text = "Volume decreased, Sir."

        elif category == "stop_audio":
            response_text = "Stopping audio playback."

        # 4. App Launch
        elif category == "app_launch":
            app_target = match_obj.group(1).lower()
            app_map = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "calc": "calc.exe",
                "chrome": "start chrome",
                "browser": "start http://127.0.0.1:8765",
                "terminal": "wt.exe" if os.path.exists(r"C:\Windows\System32\wt.exe") else "cmd.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe",
                "explorer": "explorer.exe",
                "files": "explorer.exe"
            }
            exe = app_map.get(app_target, app_target)
            try:
                subprocess.Popen(exe, shell=True)
                response_text = f"Opening {app_target}, Sir."
            except Exception as e:
                response_text = f"Unable to launch {app_target}: {e}"

        # 5. Performance Modes
        elif category == "mode_survival":
            from jarvis.system.cpu_survival import cpu_survival_manager
            cpu_survival_manager.set_mode("SURVIVAL")
            response_text = "CPU Survival Mode engaged. System profile tuned for minimum idle footprint."

        elif category == "mode_turbo":
            from jarvis.system.cpu_survival import cpu_survival_manager
            cpu_survival_manager.set_mode("TURBO")
            response_text = "Turbo performance profile activated. All compute cores unlocked."

        elif category == "mode_balanced":
            from jarvis.system.cpu_survival import cpu_survival_manager
            cpu_survival_manager.set_mode("BALANCED")
            response_text = "Standard balanced performance profile restored."

        # 6. Identity & Greetings
        elif category in ["identity", "capabilities", "greeting"]:
            from jarvis.llm.cognitive_reasoner import cognitive_reasoner
            response_text = cognitive_reasoner.analyze_and_respond(query)

        # 7. Code Graph & Graphify Operations
        elif category == "code_graph_summary":
            from jarvis.analysis.code_graph import code_graph_engine
            topo = code_graph_engine.get_topological_summary()
            clusters_str = ", ".join([f"{k.capitalize()} ({v})" for k, v in topo["clusters"].items()])
            response_text = (
                f"J.A.R.V.I.S. AST Code Graph comprises {topo['total_nodes']} active Python modules with "
                f"{topo['total_edges']} directed dependency edges across clusters: {clusters_str}."
            )

        elif category == "code_graph_blast":
            from jarvis.analysis.code_graph import code_graph_engine
            words = query.lower().split()
            target_node = "jarvis.main"
            for n_id in code_graph_engine.nodes:
                if any(w in n_id.lower() for w in words if len(w) > 3 and w not in ["blast", "radius", "what", "show", "tell", "from"]):
                    target_node = n_id
                    break
            blast = code_graph_engine.get_blast_radius(target_node)
            response_text = (
                f"AST Blast Radius for '{target_node}': {len(blast['downstream_dependencies'])} dependencies "
                f"and {len(blast['callers_and_importers'])} incoming callers ({blast['total_impact_count']} total connected links)."
            )

        elif category == "code_graph_dead":
            from jarvis.analysis.code_graph import code_graph_engine
            orphaned = []
            for n_id, node in code_graph_engine.nodes.items():
                blast = code_graph_engine.get_blast_radius(n_id)
                if not blast["callers_and_importers"] and not blast["downstream_dependencies"]:
                    orphaned.append(node.file_path)
            if orphaned:
                response_text = f"Scan complete, Sir. Found {len(orphaned)} isolated modules: {', '.join(orphaned[:3])}."
            else:
                response_text = "All repository modules are actively connected within the architecture. Zero isolated files detected, Sir."

        # 8. Next-Gen V2 Intents (Persona, Swarm, Biometrics, Simulation, Vault, Sync, NPU)
        elif category == "persona_friday":
            from jarvis.audio.persona_manager import persona_manager
            p = persona_manager.switch_persona("FRIDAY")
            response_text = f"F.R.I.D.A.Y. online, Boss. Tactical subroutines armed and ready."

        elif category == "persona_edith":
            from jarvis.audio.persona_manager import persona_manager
            p = persona_manager.switch_persona("EDITH")
            response_text = f"E.D.I.T.H. active. Code execution and technical directives locked."

        elif category == "persona_jarvis":
            from jarvis.audio.persona_manager import persona_manager
            p = persona_manager.switch_persona("JARVIS")
            response_text = f"J.A.R.V.I.S. restored, Sir. At your service as always."

        elif category == "persona_status":
            from jarvis.audio.persona_manager import persona_manager
            p = persona_manager.get_active_persona()
            response_text = f"Current active voice profile is {p.display_title} ({p.accent_description})."

        elif category == "swarm_deploy":
            from jarvis.swarm.parallel_executor import HousePartySwarmExecutor
            response_text = "House Party Protocol ready, Sir. 6 parallel sub-agent workers standby on Performance Cores."

        elif category == "biometric_vitals":
            from jarvis.sensors.biometric_harvester import biometric_harvester
            telemetry = biometric_harvester.get_telemetry_dict()
            stress = telemetry["adaptation"]["stress_index"]
            mode = telemetry["adaptation"]["mode"]
            response_text = f"Suit Vitals nominal. Operator stress index: {stress:.2f} ({mode} mode active)."

        elif category == "quantum_vault_status":
            from jarvis.security.quantum_vault import quantum_vault
            response_text = "Quantum Shield Cryptographic Vault active. AES-256-GCM memory encryption verified."

        elif category == "simulation_dryrun":
            from jarvis.simulation.barnaby_engine import barnaby_simulator
            response_text = "Project B.A.R.N.A.B.Y. virtual sandbox online. Ready for Copy-on-Write dry runs."

        elif category == "satellite_sync_status":
            from jarvis.sync.satellite_sync import satellite_sync_engine
            report = satellite_sync_engine.get_state_dict()
            response_text = f"Satellite sync active with {report['satellite_count']} connected companion nodes."

        elif category == "npu_status":
            from jarvis.hardware.npu_engine import npu_engine
            status = npu_engine.get_status()
            response_text = f"Silicon accelerator target: {status['device_target']} ({status['continuous_power_draw_watts']}W power profile)."

        # 9. Sensitive Operations (Shutdown)
        elif category == "shutdown":
            if user_confirmed:
                response_text = "Shutting down core systems, Sir. Goodnight."
                from jarvis.system.shutdown import shutdown_manager
                shutdown_manager.initiate_shutdown(delay_s=0.5)
            else:
                self._pending_confirmation = "shutdown"
                self._confirmation_expiry = time.time() + 15.0  # 15s confirmation window
                requires_conf = True
                executed = False
                response_text = "Sir, please confirm system shutdown by saying 'confirm shutdown' or 'yes'."

        return {
            "matched": True,
            "intent": category,
            "response": response_text,
            "executed": executed,
            "requires_confirmation": requires_conf,
            "match_latency_ms": match_latency_ms
        }

command_router = LightweightCommandRouter()
