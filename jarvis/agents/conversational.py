"""
jarvis/agents/conversational.py — J.A.R.V.I.S. Main Conversational Persona Agent
Orchestrates Tony Stark's J.A.R.V.I.S. persona, fast command routing, memory recall,
context budgeting, and real-time streaming LLM inference.
"""

import threading
from typing import List, Dict, Any, Optional, Iterator
from jarvis.llm.engine import OllamaEngine
from jarvis.context.budget import ContextBudget
from jarvis.memory.semantic import SemanticMemoryVault
from jarvis.system.command_router import command_router
from jarvis.system.cpu_survival import cpu_survival_manager

JARVIS_SYSTEM_PERSONA = (
    "You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), Tony Stark's sovereign AI assistant. "
    "Address the operator as 'Sir'. Keep responses concise, witty, highly intelligent, and polite. "
    "Prioritize direct action and precision over verbose commentary."
)

class ConversationalAgent:
    """
    Primary J.A.R.V.I.S. Conversational Persona Agent.
    Supports sub-millisecond command matching and streaming clause synthesis.
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
        1. Checks LightweightCommandRouter for sub-millisecond intent matching.
        2. Recalls relevant long-term memory facts matching user input.
        3. Assembles context obeying token budget ceilings.
        4. Generates response via Ollama LLM.
        5. Updates dialogue history and persists key facts to memory vault.
        """
        if not user_input or not user_input.strip():
            return "At your service, Sir."

        # 1. Fast Path: Lightweight Command Router (< 1ms match)
        cmd_result = command_router.execute(user_input)
        if cmd_result["matched"] and cmd_result["response"]:
            resp = cmd_result["response"]
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": resp})
            return resp

        # 2. Recall Semantic Memories
        memory_facts = self.memory.recall_relevant(user_input, top_k=5)

        # 3. Assemble Token-Budgeted Context
        messages = self.budget.assemble_context(
            system_prompt=self.persona_prompt,
            tool_schemas=self.active_tool_schemas,
            memory_facts=memory_facts,
            history=self.history,
            new_user_input=user_input
        )

        # 4. Perform LLM Inference
        max_tokens = cpu_survival_manager.get_llm_max_tokens()
        response_text = self.engine.chat(messages=messages, temperature=0.7, max_tokens=max_tokens)

        # 5. Update Conversation History
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response_text})

        # 6. Persist Turn into Memory Vault
        self.memory.store_text(f"User: {user_input} | J.A.R.V.I.S.: {response_text}")

        return response_text

    def stream_response(
        self,
        user_input: str,
        cancel_event: Optional[threading.Event] = None
    ) -> Iterator[str]:
        """
        Yields natural clause chunks for real-time speech synthesis:
        - Bypasses LLM immediately if matched by LightweightCommandRouter.
        - Streams clause-buffered LLM tokens otherwise.
        """
        if not user_input or not user_input.strip():
            yield "At your service, Sir."
            return

        # 1. Fast Path: Lightweight Command Router
        cmd_result = command_router.execute(user_input)
        if cmd_result["matched"] and cmd_result["response"]:
            resp = cmd_result["response"]
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": resp})
            yield resp
            return

        # 2. Recall Semantic Memories
        memory_facts = self.memory.recall_relevant(user_input, top_k=5)

        # 3. Assemble Token-Budgeted Context
        messages = self.budget.assemble_context(
            system_prompt=self.persona_prompt,
            tool_schemas=self.active_tool_schemas,
            memory_facts=memory_facts,
            history=self.history,
            new_user_input=user_input
        )

        # 4. Stream Natural Clause Chunks
        max_tokens = cpu_survival_manager.get_llm_max_tokens()
        accumulated_chunks = []

        for clause in self.engine.stream_clauses(
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
            cancel_event=cancel_event
        ):
            if cancel_event and cancel_event.is_set():
                break
            accumulated_chunks.append(clause)
            yield clause

        full_response = " ".join(accumulated_chunks).strip()
        if full_response:
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": full_response})
            self.memory.store_text(f"User: {user_input} | J.A.R.V.I.S.: {full_response}")

    def clear_history(self) -> None:
        """Clears current active conversation turn history."""
        self.history.clear()

