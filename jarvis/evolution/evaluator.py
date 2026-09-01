"""
jarvis/evolution/evaluator.py — Autonomous Self-Evaluation & Evolution Orchestrator
Coordinates diagnostic scans, regression assessments, and user-permissioned patch cycles.
"""

import time
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvis.config import config
from .ast_analyzer import ASTTracebackAnalyzer
from .regression_detector import RegressionDetector, BenchmarkMetric
from .patch_applier import PatchApplier

logger = logging.getLogger("jarvis.evolution")


class SelfEvolutionEvaluator:
    """
    Master self-evolution engine providing telemetry evaluation,
    automated root-cause isolation, and permission-gated patching.
    """
    def __init__(self):
        self.analyzer = ASTTracebackAnalyzer(config.root_dir)
        self.regression_detector = RegressionDetector(config.log_dir / "benchmark_history.json")
        self.patch_applier = PatchApplier(config.backup_dir)
        self.pending_evolutions: List[Dict[str, Any]] = []

    def scan_recent_logs_for_errors(self, max_lines: int = 200) -> List[Dict[str, Any]]:
        """Scans the latest system log file for unhandled exceptions."""
        log_file = config.log_dir / "jarvis.log"
        if not log_file.exists():
            return []

        try:
            lines = log_file.read_text(encoding="utf-8").splitlines()[-max_lines:]
            log_text = "\n".join(lines)

            # Look for Traceback blocks
            if "Traceback (most recent call last):" in log_text:
                blocks = log_text.split("Traceback (most recent call last):")
                findings = []
                for block in blocks[1:]:
                    tb = "Traceback (most recent call last):" + block
                    diag = self.analyzer.diagnose_traceback(tb)
                    if diag.get("diagnosed"):
                        findings.append(diag)
                return findings
        except Exception as e:
            logger.error(f"[EVOLUTION] Log scanning error: {e}")
        return []

    def evaluate_system_health(self) -> Dict[str, Any]:
        """Runs overall health evaluation across regressions and error logs."""
        regression_report = self.regression_detector.get_full_health_report()
        recent_errors = self.scan_recent_logs_for_errors()

        status = "NOMINAL"
        if regression_report.get("status") == "REGRESSION_DETECTED" or len(recent_errors) > 0:
            status = "ATTENTION_REQUIRED"

        return {
            "system_status": status,
            "regression_report": regression_report,
            "recent_error_count": len(recent_errors),
            "recent_errors": recent_errors,
            "pending_evolutions_count": len(self.pending_evolutions),
            "timestamp": time.time(),
        }

    def propose_patch(
        self,
        target_file: str,
        new_content: str,
        reason: str = "Automated bugfix"
    ) -> Dict[str, Any]:
        """Generates and stages a validated patch awaiting operator authorization."""
        dry_run_res = self.patch_applier.apply_patch_safely(target_file, new_content, dry_run=True)
        if not dry_run_res.get("success"):
            return {
                "staged": False,
                "error": dry_run_res.get("error", "Dry-run validation failed"),
                "diff": dry_run_res.get("diff", ""),
            }

        proposal = {
            "id": f"evo_{int(time.time())}_{len(self.pending_evolutions)+1}",
            "target_file": target_file,
            "new_content": new_content,
            "diff": dry_run_res.get("diff", ""),
            "reason": reason,
            "created_at": time.time(),
            "status": "AWAITING_USER_APPROVAL",
        }
        self.pending_evolutions.append(proposal)

        return {
            "staged": True,
            "proposal_id": proposal["id"],
            "target_file": target_file,
            "diff": proposal["diff"],
            "status": proposal["status"],
            "message": "Patch validated and staged. Awaiting user HMAC approval.",
        }

    def commit_patch(self, proposal_id: str, approved: bool = False) -> Dict[str, Any]:
        """Applies a staged patch once approved by the operator."""
        if not approved:
            return {
                "success": False,
                "error": "Explicit user approval (approved: True) required for patch execution.",
            }

        target_proposal = None
        for prop in self.pending_evolutions:
            if prop["id"] == proposal_id:
                target_proposal = prop
                break

        if not target_proposal:
            return {"success": False, "error": f"Proposal ID {proposal_id} not found."}

        res = self.patch_applier.apply_patch_safely(
            target_proposal["target_file"],
            target_proposal["new_content"],
            dry_run=False
        )

        if res.get("success"):
            target_proposal["status"] = "COMMITTED"
            target_proposal["backup_path"] = res.get("backup_path")
            return {
                "success": True,
                "proposal_id": proposal_id,
                "target_file": target_proposal["target_file"],
                "backup_path": res.get("backup_path"),
                "message": "Evolution committed successfully.",
            }
        else:
            target_proposal["status"] = "FAILED"
            return {
                "success": False,
                "proposal_id": proposal_id,
                "error": res.get("error"),
            }


# Singleton instance
self_evolution_engine = SelfEvolutionEvaluator()
