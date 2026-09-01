"""
jarvis/evolution/__init__.py — J.A.R.V.I.S. Meta-Cognitive Self-Evolution Package
"""

from .ast_analyzer import parse_traceback_to_location, extract_function_source, ASTTracebackAnalyzer
from .regression_detector import RegressionDetector, BenchmarkMetric
from .patch_applier import apply_patch_safely, PatchApplier
from .evaluator import SelfEvolutionEvaluator

__all__ = [
    "parse_traceback_to_location",
    "extract_function_source",
    "ASTTracebackAnalyzer",
    "RegressionDetector",
    "BenchmarkMetric",
    "apply_patch_safely",
    "PatchApplier",
    "SelfEvolutionEvaluator",
]
