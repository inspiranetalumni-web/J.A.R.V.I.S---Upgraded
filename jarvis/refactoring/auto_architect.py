"""
jarvis/refactoring/auto_architect.py — Stark Auto-Architect Multi-File Refactoring Engine
Parses repository-wide AST dependency graphs, identifies structural coupling, and refactors cleanly.
"""

import os
import ast
import shutil
import time
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from jarvis.config import config

logger = logging.getLogger("jarvis.refactoring")


class ASTDependencyGraph:
    """Parses Python source files to generate structural dependency maps."""
    def __init__(self, root_path: Optional[Path] = None):
        self.root = root_path or config.root_dir
        self.graph: Dict[str, List[str]] = {}

    def build_graph(self) -> Dict[str, List[str]]:
        """Scans all repository python files and maps their imported modules."""
        self.graph.clear()
        for py_file in self.root.rglob("*.py"):
            path_str = str(py_file)
            if ".venv" in path_str or "__pycache__" in path_str or ".pytest_cache" in path_str:
                continue

            try:
                rel_path = str(py_file.relative_to(self.root)).replace("\\", "/")
                imports = self._extract_imports(py_file)
                self.graph[rel_path] = imports
            except Exception:
                pass
        return self.graph

    def _extract_imports(self, file_path: Path) -> List[str]:
        imports = []
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:
            pass
        return sorted(list(set(imports)))


class StarkAutoArchitect:
    """
    Autonomous architectural refactoring engine.
    Deconstructs monolithic code into clean layered modules with AST validation.
    """
    def __init__(self, project_root: Optional[Path] = None):
        self.root = project_root or config.root_dir
        self.graph_builder = ASTDependencyGraph(self.root)

    def analyze_architecture(self) -> Dict[str, Any]:
        """Analyzes repository dependency structure and coupling."""
        graph = self.graph_builder.build_graph()
        total_files = len(graph)
        total_import_edges = sum(len(deps) for deps in graph.values())

        # Find most imported modules (hot spots)
        import_counts: Dict[str, int] = {}
        for deps in graph.values():
            for d in deps:
                import_counts[d] = import_counts.get(d, 0) + 1

        top_hotspots = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_modules_indexed": total_files,
            "total_import_edges": total_import_edges,
            "average_coupling_factor": round(total_import_edges / total_files, 2) if total_files > 0 else 0.0,
            "top_core_dependencies": top_hotspots,
        }

    def execute_architectural_refactor(
        self,
        target_files: List[str],
        refactor_plan: Dict[str, str],
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Executes multi-file refactoring with atomic snapshot backups.
        Args:
            target_files: List of relative file paths to refactor
            refactor_plan: Map of {file_path: new_code_string}
            dry_run: If True, only validates AST and returns plan
        """
        t0 = time.perf_counter()

        # Step 1: Validate all incoming codes via AST
        for rel_file, new_code in refactor_plan.items():
            try:
                ast.parse(new_code)
            except SyntaxError as e:
                return {
                    "success": False,
                    "error": f"AST Syntax error in proposed refactor for {rel_file}: {e}",
                    "failed_file": rel_file,
                }

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "files_validated": list(refactor_plan.keys()),
                "message": "All refactored files passed AST syntax validation cleanly.",
            }

        # Step 2: Atomic backups
        timestamp = int(time.time())
        bak_dir = config.backup_dir / f"refactor_{timestamp}"
        bak_dir.mkdir(parents=True, exist_ok=True)
        backups: Dict[str, str] = {}

        for rel_file in target_files:
            file_path = self.root / rel_file
            if file_path.exists():
                bak_path = bak_dir / file_path.name
                shutil.copy2(file_path, bak_path)
                backups[rel_file] = str(bak_path)

        # Step 3: Write files
        try:
            for rel_file, new_code in refactor_plan.items():
                dest_file = self.root / rel_file
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(new_code, encoding="utf-8")

            elapsed_ms = (time.perf_counter() - t0) * 1000
            return {
                "success": True,
                "dry_run": False,
                "files_updated": list(refactor_plan.keys()),
                "backup_dir": str(bak_dir),
                "elapsed_ms": round(elapsed_ms, 2),
            }
        except Exception as e:
            # Rollback
            for rel_file, bak_path in backups.items():
                dest_file = self.root / rel_file
                if Path(bak_path).exists():
                    shutil.copy2(bak_path, dest_file)
            return {"success": False, "error": f"Write failed: {e}. Rolled back to backups."}


# Singleton instance
stark_auto_architect = StarkAutoArchitect()
