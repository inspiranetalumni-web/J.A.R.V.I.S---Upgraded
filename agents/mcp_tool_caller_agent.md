# Agent: MCP Tool Caller Agent v2.0 — Pydantic JSON Function Calling
### *"A tool is only as good as its argument schema."*

**Model:** `llama3.2:3b` in tools mode (Ollama `/api/chat` with `tools` field)  
**Validation:** Pydantic v2 model validation → rejects malformed JSON before execution  
**Security:** All extracted arguments pass to Security Guardrail Agent before execution

---

## 1. Ollama Tools API — Full JSON Function Calling

```python
# jarvis/agents/tool_caller.py — Pydantic-validated Ollama tool calling
import requests, json
from pydantic import BaseModel, Field, validator
from typing import Any, Optional

# Example Pydantic schemas for tool argument validation
class RunPowerShellArgs(BaseModel):
    command: str = Field(..., min_length=1, max_length=2000, 
                        description="PowerShell command to execute")
    working_directory: Optional[str] = Field(
        default="E:\\J.A.R.V.I.S",
        description="Working directory for command execution"
    )
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    
    @validator("command")
    def no_forbidden_patterns(cls, v):
        forbidden = ["rm -rf", "format ", "reg delete", "shutdown /"]
        for pattern in forbidden:
            if pattern.lower() in v.lower():
                raise ValueError(f"Forbidden pattern in command: {pattern}")
        return v

class WriteFileArgs(BaseModel):
    path: str = Field(..., description="Absolute file path to write")
    content: str = Field(..., max_length=50000)
    encoding: str = Field(default="utf-8")
    
    @validator("path")
    def must_be_in_allowed_roots(cls, v):
        from pathlib import Path
        allowed = ["E:\\J.A.R.V.I.S", "C:\\Users\\dhamo\\Documents"]
        target = str(Path(v).resolve())
        if not any(target.startswith(r) for r in allowed):
            raise ValueError(f"Path {v} outside allowed roots")
        return v

TOOL_SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "run_powershell": RunPowerShellArgs,
    "write_file": WriteFileArgs,
    # ... all other tool schemas
}
```

---

## 2. Ollama Tool Calling Request (Native Tools API)

```python
def extract_tool_call(
    user_request: str,
    available_tools: list[dict],
    model: str = "llama3.2:3b"
) -> dict | None:
    """
    Use Ollama's native tools API to extract validated tool call from natural language.
    Returns {tool_name, arguments} or None if no tool call detected.
    """
    resp = requests.post("http://127.0.0.1:11434/api/chat", json={
        "model": model,
        "messages": [{"role": "user", "content": user_request}],
        "tools": available_tools,  # JSON schema list
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 500}
    }, timeout=20)
    
    message = resp.json().get("message", {})
    tool_calls = message.get("tool_calls", [])
    
    if not tool_calls:
        return None
    
    # Take first tool call (no parallel tool calling in v1)
    call = tool_calls[0]
    tool_name = call["function"]["name"]
    raw_args = call["function"]["arguments"]
    
    # Validate with Pydantic
    schema_class = TOOL_SCHEMA_REGISTRY.get(tool_name)
    if schema_class:
        try:
            validated = schema_class(**raw_args)
            return {"tool": tool_name, "arguments": validated.dict()}
        except Exception as e:
            return {"tool": tool_name, "arguments": raw_args, 
                    "validation_error": str(e)}
    
    return {"tool": tool_name, "arguments": raw_args}

# Example tool schema for Ollama:
EXAMPLE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_powershell",
        "description": "Execute a PowerShell command in a sandboxed ConstrainedLanguage session",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "PowerShell command"},
                "working_directory": {"type": "string", "default": "E:\\J.A.R.V.I.S"}
            },
            "required": ["command"]
        }
    }
}
```

---

## 3. Tool Call → Security → Execute → Result Flow

```
User: "Run the acceptance benchmark"

1. Tool Caller extracts: {tool: "run_powershell", args: {command: ".venv\\Scripts\\python scripts\\acceptance_benchmark.py"}}
2. Pydantic validation: RunPowerShellArgs(**args) → PASSES
3. Security Guardrail: classify_action("run_powershell") → "hitl_required"
4. HUD Modal: "Authorise: .venv\Scripts\python scripts\acceptance_benchmark.py ? [Y] [N]"
5. User presses [Y] → HMAC token consumed
6. Job Object created: 512MB cap
7. Command executes: subprocess.run([...], timeout=30)
8. stdout returned to Tool Caller
9. Tool Caller formats response: "Benchmark complete. All 7 metrics passed."
10. Conversational Agent delivers result via TTS

Total latency (excluding user decision time): ~3.1s
  (Extraction: 44ms + validation: 2ms + HITL token: 1ms + subprocess: ~2.8s)
```
