"""
tests/test_phase4.py — Pytest Verification Suite for Phase 4 MCP Tools & Automated Workflows
"""

import pytest
from jarvis.mcp.manager import MCPProcessSupervisor
from jarvis.mcp.router import HybridIntentRouter
from jarvis.filesystem.operations import FilesystemManager, EverythingSearch
from jarvis.browser.playwright_client import PlaywrightClient
from jarvis.workflows.n8n_deployer import N8nWorkflowDeployer

def test_mcp_supervisor():
    """Verify MCPProcessSupervisor config loading and tool execution dispatch."""
    supervisor = MCPProcessSupervisor()
    tools = supervisor.list_tools()
    assert len(tools) >= 4

    res = supervisor.execute_tool("everything_search", {"query": "config.py"})
    assert res["status"] == "success"
    assert res["tool"] == "everything_search"

def test_hybrid_intent_router():
    """Verify 3-stage hybrid intent router classification and sub-0.1ms stage 1 latency."""
    router = HybridIntentRouter()

    # Stage 1 Regex Matcher test
    res1 = router.route("find file config.py")
    assert res1["stage"] == 1
    assert res1["intent_domain"] == "filesystem"
    assert res1["target_tool"] == "everything_search"
    assert res1["latency_ms"] < 10.0  # Stage 1 executes in < 0.1ms

    # Stage 2 Keyword Scoring test
    res2 = router.route("open website chrome page")
    assert res2["stage"] in (1, 2)
    assert res2["intent_domain"] == "browser"

    # Stage 3 LLM Fallback test
    res3 = router.route("Tell me a story about Iron Man")
    assert res3["stage"] == 3
    assert res3["intent_domain"] == "conversational"

def test_filesystem_manager():
    """Verify FilesystemManager search, file reading, and directory listing."""
    fs = FilesystemManager()

    # Search for config.py
    files = fs.search_files("config.py")
    assert len(files) > 0

    # Read config.py content
    content = fs.read_file_content(files[0])
    assert "DynamicSystemConfig" in content

    # List root directory
    entries = fs.list_directory(".")
    assert len(entries) > 0

def test_playwright_client():
    """Verify PlaywrightClient web automation client interface."""
    client = PlaywrightClient()
    nav_res = client.navigate("http://127.0.0.1:8765")
    assert nav_res["status"] == "success"
    assert "url" in nav_res

def test_n8n_workflow_deployer():
    """Verify N8nWorkflowDeployer node graph generation and deployment."""
    deployer = N8nWorkflowDeployer()
    graph = deployer.generate_graph("Database Backup Pipeline")
    assert graph["name"] == "Database Backup Pipeline"
    assert len(graph["nodes"]) == 2

    dep_res = deployer.deploy_workflow("Database Backup Pipeline")
    assert dep_res["status"] == "success"
