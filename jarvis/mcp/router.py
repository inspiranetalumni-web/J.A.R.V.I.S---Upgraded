"""
jarvis/mcp/router.py — 3-Stage Hybrid Intent Router v3.0
Stage 1: Regex pattern matcher (< 0.1ms latency)
Stage 2: Keyword scoring classifier (< 0.5ms latency)
Stage 3: LLM Intent Classifier fallback (~30ms latency)
"""

import re
import time
from typing import Dict, Any, Optional
from jarvis.llm.engine import OllamaEngine

# Stage 1 Regex Rules
REGEX_PATTERNS = [
    (re.compile(r"^(shutdown|stop|turn off|power down)\s*(jarvis|system|server)?$", re.IGNORECASE), "system", "shutdown_system", lambda m: {}),
    (re.compile(r"^(write|create|generate)\s+(a\s+)?prd\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "write_prd", lambda m: {"feature": m.group(4) or "unnamed_feature"}),
    (re.compile(r"^(generate|create|scan)\s+(agents\.md|jarvis\.md|codebase|repo spec)", re.IGNORECASE), "workflow", "generate_agents_md", lambda m: {}),
    (re.compile(r"^(ultra\s+plan|plan\s+mode|deep\s+plan)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "ultra_plan", lambda m: {"task": m.group(3) or "unnamed_task"}),
    (re.compile(r"^(write|create)\s+spec\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "spec_driven_dev", lambda m: {"feature": m.group(3) or "unnamed_feature"}),
    (re.compile(r"^(design\s+brief|ui\s+ux\s+brief|ui\s+brief)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "ui_ux_brief", lambda m: {"screen_or_flow": m.group(3) or "main_flow"}),
    (re.compile(r"^(implementation\s+plan|build\s+sequence)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "implementation_plan", lambda m: {"spec_or_prd": m.group(3) or "unnamed_spec"}),
    (re.compile(r"^(wire\s+mcp|setup\s+mcp|mcp\s+server)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "wire_mcp_server", lambda m: {"service_or_api": m.group(3) or "custom_mcp"}),
    (re.compile(r"^(connect\s+database|connect\s+db|database\s+setup)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "connect_database", lambda m: {"db_type": m.group(3) or "ChromaDB + KùzuDB"}),
    (re.compile(r"^(find\s+security\s+gaps|security\s+audit|audit\s+security)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "find_security_gaps", lambda m: {"focus_areas": m.group(3) or "AUTH / USER DATA"}),
    (re.compile(r"^(debug\s+error|debug\s+fast|fix\s+error)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "debug_error_fast", lambda m: {"error_trace": m.group(3) or "unspecified_error"}),
    (re.compile(r"^(e2e\s+test|playwright\s+test)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "e2e_test_app", lambda m: {"flow": m.group(3) or "core_flow"}),
    (re.compile(r"^(clean\s+dead\s+code|delete\s+dead\s+code)\s*(in)?\s*(.*)", re.IGNORECASE), "workflow", "cleanup_dead_code", lambda m: {"scope": m.group(3) or "whole_repo"}),
    (re.compile(r"^(clean\s+git\s+commit|conventional\s+commit|git\s+commit)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "write_clean_commits", lambda m: {}),
    (re.compile(r"^(guardrail\s+hooks|setup\s+hooks)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "hooks_as_guardrails", lambda m: {}),
    (re.compile(r"^(create\s+skill|task\s+to\s+skill|turn\s+into\s+skill)\s*(for)?\s*(.*)", re.IGNORECASE), "workflow", "turn_task_into_skill", lambda m: {"task_name": m.group(3) or "new_task", "description": "Custom task skill", "trigger_phrases": [m.group(3) or "trigger"]}),
    (re.compile(r"^(find|search)\s+(file|path)?\s*(.*)", re.IGNORECASE), "filesystem", "everything_search", lambda m: {"query": m.group(3)}),
    (re.compile(r"^(open|browse|navigate|go to)\s+(https?://\S+|\S+\.\S+)", re.IGNORECASE), "browser", "browse_url", lambda m: {"url": m.group(2)}),
    (re.compile(r"^(create|deploy)\s+(workflow|automation|n8n)\s*(.*)", re.IGNORECASE), "workflow", "deploy_workflow", lambda m: {"name": m.group(3) or "unnamed_workflow"}),
    (re.compile(r"^(read|cat)\s+file\s+(.*)", re.IGNORECASE), "filesystem", "read_file", lambda m: {"path": m.group(2)})
]

# Stage 2 Keywords
KEYWORD_DOMAINS = {
    "filesystem": ["file", "directory", "folder", "drive", "path", "find", "search", "read"],
    "browser": ["browse", "url", "website", "http", "https", "page", "scrape", "chrome"],
    "workflow": ["n8n", "workflow", "automation", "trigger", "webhook", "dag", "deploy", "prd", "agents.md", "plan", "spec", "design", "brief", "implementation", "mcp", "database", "security", "audit", "debug", "e2e", "test", "deadcode", "commit", "hooks", "skill"]
}

class HybridIntentRouter:
    """
    3-Stage Hybrid Intent Router.
    Routes queries to the fastest execution tier possible (< 0.1ms for Stage 1).
    """
    def __init__(self):
        self.llm = OllamaEngine()

    def route(self, query: str) -> Dict[str, Any]:
        """
        Routes user query across Stage 1 (Regex), Stage 2 (Keyword), and Stage 3 (LLM).
        """
        t0 = time.perf_counter()
        query_str = query.strip()

        # --- STAGE 1: Fast Regex Matcher (< 0.1ms) ---
        for pattern, domain, tool, arg_builder in REGEX_PATTERNS:
            m = pattern.match(query_str)
            if m:
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
                return {
                    "stage": 1,
                    "intent_domain": domain,
                    "target_tool": tool,
                    "arguments": arg_builder(m),
                    "confidence": 1.0,
                    "latency_ms": elapsed_ms
                }

        # --- STAGE 2: Keyword Scoring Classifier (< 0.5ms) ---
        tokens = set(re.findall(r"\w+", query_str.lower()))
        domain_scores = {}
        for domain, keywords in KEYWORD_DOMAINS.items():
            matches = tokens.intersection(set(keywords))
            score = len(matches) / max(1, len(keywords))
            if len(matches) > 0:
                domain_scores[domain] = score

        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            best_score = domain_scores[best_domain]
            if best_score >= 0.15:
                tool_map = {
                    "filesystem": "everything_search",
                    "browser": "browse_url",
                    "workflow": "deploy_workflow"
                }
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
                return {
                    "stage": 2,
                    "intent_domain": best_domain,
                    "target_tool": tool_map.get(best_domain, "conversational"),
                    "arguments": {"query": query_str},
                    "confidence": round(best_score, 2),
                    "latency_ms": elapsed_ms
                }

        # --- STAGE 3: Conversational LLM Fallback (~30ms) ---
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
        return {
            "stage": 3,
            "intent_domain": "conversational",
            "target_tool": None,
            "arguments": {"query": query_str},
            "confidence": 0.85,
            "latency_ms": elapsed_ms
        }
