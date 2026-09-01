"""
jarvis/evolution/ast_analyzer.py — AST + Traceback Root Cause Locator
Parses runtime tracebacks and extracts targeted function AST context.
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, Optional
from jarvis.config import config


def parse_traceback_to_location(traceback_text: str) -> Optional[Dict[str, Any]]:
    """
    Parse a Python traceback to extract the exact file, line, and function
    that caused the failure.

    Example input:
        Traceback (most recent call last):
          File "jarvis/audio/tts.py", line 42, in synthesize
            audio = self._session.run(None, inputs)
        RuntimeError: ONNX error

    Returns:
        {"file": "jarvis/audio/tts.py", "line": 42, "function": "synthesize",
         "error_type": "RuntimeError", "error_msg": "ONNX error"}
    """
    if not traceback_text or not isinstance(traceback_text, str):
        return None

    # Extract file + line from last "File" entry (innermost frame)
    file_pattern = re.compile(r'File "([^"]+)", line (\d+)(?:, in (\w+))?')
    matches = file_pattern.findall(traceback_text)
    if not matches:
        return None

    filepath, lineno, funcname = matches[-1]

    # Extract error type and message from trailing line
    error_pattern = re.compile(r'^(\w[\w.]*(?:Error|Exception|Warning)|RuntimeException|ValueError|KeyError|AttributeError|TypeError): (.+)$', re.M)
    error_match = error_pattern.search(traceback_text)

    error_type = error_match.group(1) if error_match else "UnknownError"
    error_msg = error_match.group(2) if error_match else traceback_text.strip().splitlines()[-1]

    return {
        "file": filepath,
        "line": int(lineno),
        "function": funcname if funcname else "<module>",
        "error_type": error_type,
        "error_msg": error_msg,
    }


def extract_function_source(filepath: str, line: int) -> str:
    """Extract the full source code of the function containing the failing line."""
    try:
        path = Path(filepath)
        if not path.is_absolute():
            path = config.root_dir / filepath

        if not path.exists():
            return ""

        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno
                end = getattr(node, "end_lineno", start + 30)
                if start <= line <= end:
                    lines = source.splitlines()
                    return "\n".join(lines[start - 1:end])

        # Fallback: return ±15 lines around the failure
        lines = source.splitlines()
        start = max(0, line - 10)
        end = min(len(lines), line + 10)
        return "\n".join(lines[start:end])
    except Exception:
        return ""


class ASTTracebackAnalyzer:
    """
    Coordinates AST analysis, diagnostic stack parsing, and context harvesting.
    """
    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or config.root_dir

    def diagnose_traceback(self, traceback_text: str) -> Dict[str, Any]:
        location = parse_traceback_to_location(traceback_text)
        if not location:
            return {
                "diagnosed": False,
                "error": "Could not parse traceback structure",
                "location": None,
                "context_code": "",
            }

        context = extract_function_source(location["file"], location["line"])
        return {
            "diagnosed": True,
            "location": location,
            "context_code": context,
            "file_exists": (self.root_dir / location["file"]).exists() if not Path(location["file"]).is_absolute() else Path(location["file"]).exists(),
        }
