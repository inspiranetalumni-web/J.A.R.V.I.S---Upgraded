"""
tests/test_phase3.py — Pytest Verification Suite for Phase 3 Cognitive Core & Tiered Memory Vault
"""

import pytest
from jarvis.llm.engine import OllamaEngine
from jarvis.context.budget import ContextBudget, count_tokens, count_messages
from jarvis.memory.semantic import SemanticMemoryVault
from jarvis.agents.conversational import ConversationalAgent

def test_ollama_engine():
    """Verify OllamaEngine chat interface and fallback response generator."""
    engine = OllamaEngine()
    messages = [{"role": "user", "content": "Who are you?"}]
    response = engine.chat(messages)

    assert isinstance(response, str)
    assert len(response) > 0

def test_context_budget():
    """Verify ContextBudget slot allocation and history compaction math."""
    budget = ContextBudget()

    system_prompt = "You are J.A.R.V.I.S."
    tools = ['{"name": "everything_search", "params": {"query": "string"}}']
    memories = ["User prefers FastAPI."]
    history = [
        {"role": "user", "content": f"Message {i}"} if i % 2 == 0 else {"role": "assistant", "content": f"Reply {i}"}
        for i in range(20)
    ]

    messages = budget.assemble_context(
        system_prompt=system_prompt,
        tool_schemas=tools,
        memory_facts=memories,
        history=history,
        new_user_input="Run system audit"
    )

    assert len(messages) > 2
    assert messages[0]["role"] == "system"
    assert "J.A.R.V.I.S." in messages[0]["content"]
    assert "FastAPI" in messages[0]["content"]
    assert messages[-1]["content"] == "Run system audit"

def test_semantic_memory_vault():
    """Verify SemanticMemoryVault triple storage and recall."""
    vault = SemanticMemoryVault()
    vault.clear()

    vault.store_fact("Dhamodran", "prefers", "FastAPI web framework")
    vault.store_text("The primary hardware host is HP Pavilion with Intel i7-1255U.")

    facts = vault.recall_relevant("FastAPI")
    assert len(facts) > 0
    assert any("FastAPI" in f for f in facts)

def test_conversational_agent():
    """Verify ConversationalAgent full pipeline message processing."""
    agent = ConversationalAgent()
    agent.clear_history()

    reply1 = agent.process_message("Hello J.A.R.V.I.S.")
    assert isinstance(reply1, str)
    assert len(reply1) > 0

    reply2 = agent.process_message("What is your primary directive?")
    assert isinstance(reply2, str)

    assert len(agent.history) == 4  # 2 user turns + 2 assistant responses
