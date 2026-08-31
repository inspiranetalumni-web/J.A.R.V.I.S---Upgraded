"""
jarvis/filesystem/operations.py — High-Speed Filesystem & Everything Search v3.0
Integrates Everything CLI (es.exe < 5ms search) with fallback Python glob directory scanner.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from jarvis.config import config

class EverythingSearch:
    """
    Sub-5ms Windows file indexer using voidtools Everything CLI (es.exe).
    Falls back to recursive python directory search if es.exe is not installed.
    """
    def __init__(self, root_dir: Path = config.root_dir):
        self.root_dir = root_dir
        self.es_path = shutil.which("es.exe") or shutil.which("es")

    def search(self, query: str, max_results: int = 10) -> List[str]:
        """Performs high-speed file search across host filesystem."""
        query_str = query.strip()
        if not query_str:
            return []

        # 1. Try es.exe CLI fast path (< 5ms)
        if self.es_path:
            try:
                cmd = [self.es_path, "-n", str(max_results), query_str]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                if res.returncode == 0:
                    lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
                    if lines:
                        return lines[:max_results]
            except Exception:
                pass

        # 2. Python recursive search fallback
        results = []
        try:
            for path in self.root_dir.rglob(f"*{query_str}*"):
                if path.is_file() and ".git" not in path.parts and ".venv" not in path.parts:
                    results.append(str(path))
                    if len(results) >= max_results:
                        break
        except Exception:
            pass

        return results

class FilesystemManager:
    """
    Real-world filesystem manager for J.A.R.V.I.S.
    """
    def __init__(self):
        self.everything = EverythingSearch()

    def search_files(self, query: str, max_results: int = 10) -> List[str]:
        """Searches files using Everything CLI or python scanner."""
        return self.everything.search(query, max_results=max_results)

    def read_file_content(self, file_path: str, max_bytes: int = 8192) -> str:
        """Reads file text contents safely."""
        p = Path(file_path)
        if not p.exists() or not p.is_file():
            return f"Error: File not found at path '{file_path}'"
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(max_bytes)
                return content
        except Exception as e:
            return f"Error reading file '{file_path}': {e}"

    def list_directory(self, dir_path: str) -> List[Dict[str, Any]]:
        """Lists directory entries with file size and type details."""
        p = Path(dir_path)
        if not p.exists() or not p.is_dir():
            return []
        items = []
        try:
            for child in p.iterdir():
                items.append({
                    "name": child.name,
                    "path": str(child),
                    "is_dir": child.is_dir(),
                    "size_bytes": child.stat().st_size if child.is_file() else 0
                })
        except Exception:
            pass
        return items
