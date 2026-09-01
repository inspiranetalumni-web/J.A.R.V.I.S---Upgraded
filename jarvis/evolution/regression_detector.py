"""
jarvis/evolution/regression_detector.py — Statistical Performance & Regression Detector
Analyzes system telemetry and acceptance benchmark trends to flag anomalies.
"""

import json
import math
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from jarvis.config import config


@dataclass
class BenchmarkMetric:
    name: str
    value: float
    unit: str
    target: float
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class RegressionDetector:
    """
    Statistical regression analysis engine for TTFT, TTS latency, and memory footprints.
    """
    def __init__(self, history_file: Optional[Path] = None):
        self.history_file = history_file or (config.log_dir / "benchmark_history.json")
        self._history: Dict[str, List[Dict[str, Any]]] = self._load_history()

    def _load_history(self) -> Dict[str, List[Dict[str, Any]]]:
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_history(self):
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.write_text(json.dumps(self._history, indent=2), encoding="utf-8")
        except Exception:
            pass

    def record_metric(self, metric: BenchmarkMetric) -> Dict[str, Any]:
        """Record a benchmark sample and evaluate for regression against baseline."""
        name = metric.name
        if name not in self._history:
            self._history[name] = []

        entry = asdict(metric)
        self._history[name].append(entry)
        # Keep last 50 samples per metric
        if len(self._history[name]) > 50:
            self._history[name] = self._history[name][-50:]

        self._save_history()
        return self.analyze_metric(name)

    def analyze_metric(self, name: str, threshold_pct: float = 25.0) -> Dict[str, Any]:
        """
        Calculates baseline mean and evaluates whether the latest observation
        exceeds normal operating thresholds by `threshold_pct`.
        """
        history = self._history.get(name, [])
        if not history:
            return {"metric": name, "has_regression": False, "samples": 0, "reason": "No data"}

        values = [h["value"] for h in history]
        latest = values[-1]
        target = history[-1].get("target", 0.0)
        unit = history[-1].get("unit", "")

        if len(values) < 3:
            # Not enough samples for statistical mean, compare directly against target
            exceeds_target = (latest > target) if target > 0 else False
            return {
                "metric": name,
                "latest": latest,
                "target": target,
                "unit": unit,
                "has_regression": exceeds_target,
                "delta_pct": round(((latest - target) / target * 100) if target > 0 else 0.0, 2),
                "samples": len(values),
                "reason": "Direct target comparison (insufficient samples)",
            }

        # Calculate baseline from earlier samples (excluding latest)
        baseline_samples = values[:-1]
        mean_val = sum(baseline_samples) / len(baseline_samples)
        variance = sum((x - mean_val) ** 2 for x in baseline_samples) / len(baseline_samples)
        std_dev = math.sqrt(variance) if variance > 0 else 0.001

        delta_pct = ((latest - mean_val) / mean_val) * 100 if mean_val > 0 else 0.0
        z_score = (latest - mean_val) / std_dev if std_dev > 0 else 0.0

        is_regression = (delta_pct > threshold_pct) or (latest > target and target > 0)

        return {
            "metric": name,
            "latest": round(latest, 3),
            "baseline_mean": round(mean_val, 3),
            "std_dev": round(std_dev, 3),
            "z_score": round(z_score, 2),
            "delta_pct": round(delta_pct, 2),
            "target": target,
            "unit": unit,
            "has_regression": is_regression,
            "samples": len(values),
            "reason": f"{delta_pct:+.1f}% shift from baseline" if is_regression else "Nominal",
        }

    def get_full_health_report(self) -> Dict[str, Any]:
        """Evaluates all tracked metrics and returns overall system regression status."""
        report = {}
        total_regressions = 0

        for metric_name in self._history:
            analysis = self.analyze_metric(metric_name)
            report[metric_name] = analysis
            if analysis.get("has_regression"):
                total_regressions += 1

        return {
            "status": "HEALTHY" if total_regressions == 0 else "REGRESSION_DETECTED",
            "total_metrics": len(self._history),
            "regressed_metrics_count": total_regressions,
            "metrics": report,
            "timestamp": time.time(),
        }
