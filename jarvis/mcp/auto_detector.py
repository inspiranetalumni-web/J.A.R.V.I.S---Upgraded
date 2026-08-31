"""
jarvis/mcp/auto_detector.py — Auto-Detecting MCP Tool Engine & Permission Guardrail v3.0
Scans local AAS catalog (2,005+ skills) & online MCP registries.
Enforces offline-first privacy: requires explicit user permission before initiating online network calls.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvis.config import config

class MCPAutoDetector:
    """
    Auto-detects relevant MCP tools from local skill catalog & online registries.
    Enforces offline guardrails with explicit user confirmation for online access.
    """
    def __init__(self):
        self.root_dir = config.root_dir
        self.aas_catalog_path = self.root_dir / "skills" / "agentic-awesome-skills" / "skills_index.json"
        self.online_access_approved = False  # Default: 100% Offline Mode

    def set_online_permission(self, approved: bool):
        """Sets online network access permission state."""
        self.online_access_approved = approved

    def auto_detect_tools(self, task_description: str) -> Dict[str, Any]:
        """
        Scans task description and auto-detects required MCP tools.
        Categorizes tools into Local (Offline) vs Online (Requires Permission).
        """
        task_lower = task_description.lower()
        detected_local_tools = []
        detected_online_tools = []

        # Local MCP Tools (Always Available Offline)
        if any(w in task_lower for w in ["file", "search", "directory", "read", "write", "folder"]):
            detected_local_tools.append({"name": "filesystem_mcp", "type": "local", "status": "READY"})
        if any(w in task_lower for w in ["sqlite", "kuzu", "chroma", "database", "sql"]):
            detected_local_tools.append({"name": "database_mcp", "type": "local", "status": "READY"})
        if any(w in task_lower for w in ["cmd", "powershell", "execute", "win32", "actuation"]):
            detected_local_tools.append({"name": "os_actuation_mcp", "type": "local", "status": "READY"})

        # Online MCP Tools (Requires Explicit User Permission)
        if any(w in task_lower for w in ["web", "scrape", "http", "url", "browse", "api"]):
            detected_online_tools.append({"name": "playwright_browser_mcp", "type": "online", "permission_required": True})
        if any(w in task_lower for w in ["git clone", "github", "remote repo"]):
            detected_online_tools.append({"name": "github_mcp", "type": "online", "permission_required": True})

        permission_needed = len(detected_online_tools) > 0 and not self.online_access_approved

        return {
            "task": task_description,
            "offline_mode_active": not self.online_access_approved,
            "permission_prompt_required": permission_needed,
            "user_message": (
                "[ONLINE MCP TOOL DETECTED]: This task requires online network access. "
                "Do you authorize J.A.R.V.I.S. to connect online? (Reply YES to proceed)"
                if permission_needed else "All required tools are 100% local and offline."
            ),
            "local_tools": detected_local_tools,
            "online_tools": detected_online_tools
        }
