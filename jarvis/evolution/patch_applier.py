"""
jarvis/evolution/patch_applier.py — Atomic Patch Applier with Crash-Safe Rollback Shield
Applies verified patches with syntax validation, .bak snapshots, and rollback guards.
"""

import os
import shutil
import difflib
import time
import py_compile
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from jarvis.config import config


class PatchApplier:
    """
    Atomic patch application with crash-safe rollback protection.
    """
    def __init__(self, backup_dir: Optional[Path] = None):
        self.backup_dir = backup_dir or config.backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def generate_diff(self, original_text: str, modified_text: str, filename: str = "module.py") -> str:
        """Generates unified diff between original and proposed code."""
        orig_lines = original_text.splitlines(keepends=True)
        mod_lines = modified_text.splitlines(keepends=True)
        diff = difflib.unified_diff(orig_lines, mod_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}")
        return "".join(diff)

    def validate_python_syntax(self, code_text: str) -> tuple[bool, str]:
        """Checks if code compiles cleanly without SyntaxError."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as tmp:
            tmp_path = tmp.name
            tmp.write(code_text)

        try:
            py_compile.compile(tmp_path, doraise=True)
            return True, "Syntax OK"
        except py_compile.PyCompileError as e:
            return False, str(e)
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    def apply_patch_safely(
        self,
        target_file: str | Path,
        new_content: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Atomically applies patch to target file with backup snapshot and rollback guarantee.
        """
        path = Path(target_file)
        if not path.is_absolute():
            path = config.root_dir / target_file

        if not path.exists():
            return {
                "success": False,
                "error": f"Target file does not exist: {path}",
                "backup_path": None,
                "diff": "",
            }

        original_content = path.read_text(encoding="utf-8")
        diff_str = self.generate_diff(original_content, new_content, filename=path.name)

        # Step 1: Syntax check
        is_valid, syntax_msg = self.validate_python_syntax(new_content)
        if not is_valid:
            return {
                "success": False,
                "error": f"Syntax validation failed: {syntax_msg}",
                "backup_path": None,
                "diff": diff_str,
            }

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "diff": diff_str,
                "message": "Dry-run validation successful. Code compiles cleanly.",
                "backup_path": None,
            }

        # Step 2: Create atomic backup
        timestamp = int(time.time())
        backup_filename = f"{path.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_filename
        shutil.copy2(path, backup_path)

        # Step 3: Write new content atomically via temporary file
        temp_dest = path.with_suffix(f".tmp_{timestamp}")
        try:
            temp_dest.write_text(new_content, encoding="utf-8")
            os.replace(temp_dest, path)
            return {
                "success": True,
                "diff": diff_str,
                "backup_path": str(backup_path),
                "target_file": str(path),
                "message": f"Patch applied cleanly. Backup created at {backup_path}",
            }
        except Exception as e:
            # Clean up temp and restore if needed
            if temp_dest.exists():
                try:
                    os.remove(temp_dest)
                except Exception:
                    pass
            self.rollback(backup_path, path)
            return {
                "success": False,
                "error": f"File write error: {e}. Rolled back to original.",
                "backup_path": str(backup_path),
                "diff": diff_str,
            }

    def rollback(self, backup_path: str | Path, target_file: str | Path) -> bool:
        """Restores file from backup snapshot."""
        try:
            b_path = Path(backup_path)
            t_path = Path(target_file)
            if not t_path.is_absolute():
                t_path = config.root_dir / target_file

            if b_path.exists():
                shutil.copy2(b_path, t_path)
                return True
            return False
        except Exception:
            return False


# Global helper function for direct calling
_default_patcher = PatchApplier()

def apply_patch_safely(target_file: str | Path, new_content: str, dry_run: bool = False) -> Dict[str, Any]:
    return _default_patcher.apply_patch_safely(target_file, new_content, dry_run=dry_run)
