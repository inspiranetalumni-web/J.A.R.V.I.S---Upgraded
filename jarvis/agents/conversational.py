"""
jarvis/agents/conversational.py — J.A.R.V.I.S. Main Conversational Persona Agent
Orchestrates Tony Stark's J.A.R.V.I.S. persona, memory recall, context budgeting, and LLM inference.
"""

from typing import List, Dict, Any, Optional
from jarvis.llm.engine import OllamaEngine
from jarvis.context.budget import ContextBudget
from jarvis.memory.semantic import SemanticMemoryVault

JARVIS_SYSTEM_PERSONA = (
    "You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), Tony Stark's sovereign AI assistant. "
    "Address the operator as 'Sir'. Keep responses concise, witty, highly intelligent, and polite. "
    "Prioritize direct action and precision over verbose commentary."
)

class ConversationalAgent:
    """
    Primary J.A.R.V.I.S. Conversational Persona Agent.
    """
    def __init__(self):
        self.engine = OllamaEngine()
        self.budget = ContextBudget()
        self.memory = SemanticMemoryVault()

        self.persona_prompt = JARVIS_SYSTEM_PERSONA
        self.history: List[Dict[str, str]] = []
        self.active_tool_schemas: List[str] = []

    def process_message(self, user_input: str) -> str:
        """
        Main multi-turn message processor:
        1. Recalls relevant long-term memory facts matching user input.
        2. Assembles context obeying 10/15/25/35/15 token slot ceilings.
        3. Generates response via Ollama LLM.
        4. Updates dialogue history and persists key facts to memory vault.
        """
        if not user_input or not user_input.strip():
            return "At your service, Sir."

        shutdown_terms = ["shutdown", "power down", "turn off jarvis", "stop jarvis", "jarvis shutdown"]
        if any(term in user_input.lower() for term in shutdown_terms):
            import os, time, threading
            def _do_shutdown():
                time.sleep(1.0)
                os._exit(0)
            threading.Thread(target=_do_shutdown, daemon=True).start()
            return "Shutting down core systems, sir. Goodnight."

        # 1. Recall Semantic Memories
        memory_facts = self.memory.recall_relevant(user_input, top_k=5)

        # 2. Assemble Token-Budgeted Context
        messages = self.budget.assemble_context(
            system_prompt=self.persona_prompt,
            tool_schemas=self.active_tool_schemas,
            memory_facts=memory_facts,
            history=self.history,
            new_user_input=user_input
        )

        # 3. Perform LLM Inference
        response_text = self.engine.chat(messages=messages, temperature=0.7)

        # 4. Update Conversation History
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response_text})

        # 5. Persist Turn into Memory Vault
        self.memory.store_text(f"User: {user_input} | J.A.R.V.I.S.: {response_text}")

        return response_text

    def clear_history(self) -> None:
        """Clears current active conversation turn history."""
        self.history.clear()
