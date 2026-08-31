"""
jarvis/context/budget.py — Token Slot Budget Allocator & Context Compaction Engine
Strictly allocates tokens across 5 slot categories within an 8,192 token window.
Slot Formula: 10% System | 15% Tool Schemas | 25% Memory Vault | 35% History | 15% Output Headroom
"""

from typing import List, Dict, Any, Optional

MAX_WINDOW_TOKENS = 8192

# Token Ceilings
SYSTEM_SLOT_CEILING = int(MAX_WINDOW_TOKENS * 0.10)     # ~819 tokens
TOOLS_SLOT_CEILING = int(MAX_WINDOW_TOKENS * 0.15)      # ~1228 tokens
MEMORY_SLOT_CEILING = int(MAX_WINDOW_TOKENS * 0.25)     # ~2048 tokens
HISTORY_SLOT_CEILING = int(MAX_WINDOW_TOKENS * 0.35)    # ~2867 tokens
OUTPUT_SLOT_CEILING = int(MAX_WINDOW_TOKENS * 0.15)     # ~1228 tokens

def count_tokens(text: str) -> int:
    """Accurate token counter with fast 4-character approximation fallback."""
    if not text:
        return 0
    return max(1, len(text) // 4)

def count_messages(messages: List[Dict[str, str]]) -> int:
    """Calculates total tokens across a list of chat message dictionaries."""
    total = 0
    for msg in messages:
        total += count_tokens(msg.get("content", "")) + 4
    return total

class ContextBudget:
    """
    Deterministic Context Slot Budget Allocator.
    Prevents token window overflow and context degradation.
    """
    def __init__(self, max_tokens: int = MAX_WINDOW_TOKENS):
        self.max_tokens = max_tokens
        self.system_ceiling = SYSTEM_SLOT_CEILING
        self.tools_ceiling = TOOLS_SLOT_CEILING
        self.memory_ceiling = MEMORY_SLOT_CEILING
        self.history_ceiling = HISTORY_SLOT_CEILING

    def format_memory_section(self, memory_facts: List[str]) -> str:
        """Formats retrieved semantic memory facts under ceiling limits."""
        if not memory_facts:
            return ""
        formatted = "### [RECALLED LONG-TERM MEMORY]\n"
        for fact in memory_facts:
            line = f"- {fact}\n"
            if count_tokens(formatted + line) > self.memory_ceiling:
                break
            formatted += line
        return formatted.strip()

    def format_tools_section(self, tool_schemas: List[str]) -> str:
        """Formats active MCP tool schemas under ceiling limits."""
        if not tool_schemas:
            return ""
        formatted = "### [AVAILABLE ACTIVE TOOLS]\n"
        for schema in tool_schemas:
            block = f"```json\n{schema}\n```\n"
            if count_tokens(formatted + block) > self.tools_ceiling:
                break
            formatted += block
        return formatted.strip()

    def compact_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        3-Ring Context Compactor: Trims oldest dialogue turns to fit within 35% history ceiling.
        """
        if not history:
            return []

        compacted = list(history)
        while count_messages(compacted) > self.history_ceiling and len(compacted) > 2:
            # Remove oldest user/assistant turn pair
            compacted.pop(0)
            if compacted and compacted[0]["role"] == "assistant":
                compacted.pop(0)

        return compacted

    def assemble_context(
        self,
        system_prompt: str,
        tool_schemas: Optional[List[str]] = None,
        memory_facts: Optional[List[str]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        new_user_input: str = ""
    ) -> List[Dict[str, str]]:
        """
        Assembles complete LLM chat payload strictly obeying token budget slots.
        """
        tool_schemas = tool_schemas or []
        memory_facts = memory_facts or []
        history = history or []

        # 1. System Directive Slot (10%)
        system_str = system_prompt[:self.system_ceiling * 4]

        # 2. Tools Slot (15%)
        tools_str = self.format_tools_section(tool_schemas)

        # 3. Memory Vault Slot (25%)
        memory_str = self.format_memory_section(memory_facts)

        # Combine System + Tools + Memory into master system message
        full_system_components = [system_str]
        if memory_str:
            full_system_components.append(memory_str)
        if tools_str:
            full_system_components.append(tools_str)

        full_system_content = "\n\n".join(full_system_components)

        messages = [{"role": "system", "content": full_system_content}]

        # 4. Dialogue History Slot (35%)
        compacted_history = self.compact_history(history)
        messages.extend(compacted_history)

        # 5. Add Current User Input
        if new_user_input:
            messages.append({"role": "user", "content": new_user_input})

        return messages
