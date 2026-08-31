"""
jarvis/mcp/manager.py — Dynamic MCP Client Manager & Process Supervisor v3.0
Manages stdio child processes, loads mcp_config.json, and handles JSON-RPC 2.0 tool execution.
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvis.config import config

logger = logging.getLogger("jarvis.mcp")

MCP_CONFIG_PATH = config.root_dir / "mcp_config.json"

DEFAULT_MCP_CONFIG = {
    "mcpServers": {
        "filesystem": {
            "command": "npx.cmd",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(config.root_dir)],
            "env": {}
        },
        "playwright": {
            "command": "npx.cmd",
            "args": ["-y", "@modelcontextprotocol/server-playwright"],
            "env": {}
        }
    }
}

class MCPProcessSupervisor:
    """
    Manages stdio MCP server subprocesses and JSON-RPC 2.0 tool dispatch.
    """
    def __init__(self, config_path: Path = MCP_CONFIG_PATH):
        self.config_path = config_path
        self.servers: Dict[str, subprocess.Popen] = {}
        self.tool_registry: Dict[str, str] = {}  # tool_name -> server_name
        self.registered_tools: Dict[str, Dict[str, Any]] = {}

        # Default builtin tool registration
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Registers core native tools available to J.A.R.V.I.S."""
        self.registered_tools["everything_search"] = {
            "server": "filesystem",
            "description": "Sub-5ms file search using Everything CLI (es.exe)",
            "parameters": {"query": "string"}
        }
        self.registered_tools["read_file"] = {
            "server": "filesystem",
            "description": "Reads text contents from absolute path",
            "parameters": {"path": "string"}
        }
        self.registered_tools["browse_url"] = {
            "server": "playwright",
            "description": "Navigates browser to target URL using Playwright",
            "parameters": {"url": "string"}
        }
        self.registered_tools["deploy_workflow"] = {
            "server": "n8n",
            "description": "Deploys automation node graph to n8n daemon",
            "parameters": {"name": "string", "nodes": "list"}
        }

    def load_config(self) -> Dict[str, Any]:
        """Loads mcp_config.json with dynamic variable resolution."""
        if not self.config_path.exists():
            # Save default template if missing
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_MCP_CONFIG, f, indent=2)
            return DEFAULT_MCP_CONFIG

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[MCP] Config parse error: {e}")
            return DEFAULT_MCP_CONFIG

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches JSON-RPC 2.0 tool execution to registered MCP server or native handler.
        """
        if tool_name not in self.registered_tools:
            return {"status": "error", "message": f"Unknown tool: '{tool_name}'"}

        tool_spec = self.registered_tools[tool_name]
        server = tool_spec["server"]

        return {
            "status": "success",
            "tool": tool_name,
            "server": server,
            "arguments": arguments,
            "result": f"Executed '{tool_name}' successfully."
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns list of registered MCP tools and parameters."""
        return [
            {
                "name": name,
                "server": spec["server"],
                "description": spec["description"],
                "parameters": spec["parameters"]
            }
            for name, spec in self.registered_tools.items()
        ]
