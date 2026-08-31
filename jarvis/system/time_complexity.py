"""
jarvis/system/time_complexity.py — 10 Must-Know Time Complexity Patterns Profiler & Optimizer
Analyzes algorithms, code snippets, and execution steps to determine Big-O time complexity and optimize performance.
"""

from typing import Dict, Any, List

COMPLEXITY_PATTERNS: Dict[str, Dict[str, Any]] = {
    "O(1)": {
        "pattern": "1. Hash Lookup",
        "code_example": "value = map.get(key)",
        "visualization": "one jump, any n",
        "latency_impact": "sub-0.1ms (Instant)",
        "recommendation": "Optimal. Preferred pattern for dictionary and cache lookups."
    },
    "O(log n)": {
        "pattern": "2. Halving Loop",
        "code_example": "while (n > 1) n = n / 2",
        "visualization": "halves every step",
        "latency_impact": "< 0.5ms (Logarithmic)",
        "recommendation": "Highly efficient for sorted vector search and binary indexing."
    },
    "O(n)": {
        "pattern": "3. Single Loop",
        "code_example": "for (i=0; i<n; i++) sum += a[i]",
        "visualization": "touch each element once",
        "latency_impact": "~1-5ms (Linear)",
        "recommendation": "Good for single-pass stream processing and array scans."
    },
    "O(n + m)": {
        "pattern": "4. Sequential Loops",
        "code_example": "for(i=0..n) {}; for(j=0..m) {}",
        "visualization": "one pass over each collection",
        "latency_impact": "~2-10ms (Linear Multi-Pass)",
        "recommendation": "Acceptable for separate sequential processing steps."
    },
    "O(n log n)": {
        "pattern": "5. Loop + Binary Search / Divide & Conquer",
        "code_example": "for(i=0..n) binarySearch(a, x)",
        "visualization": "n x log n work across levels",
        "latency_impact": "~10-30ms (Quasilinear)",
        "recommendation": "Standard for sorting algorithms (MergeSort, Timsort) and vector retrieval."
    },
    "O(n^2)": {
        "pattern": "7. Nested Loop / Triangular Loop",
        "code_example": "for(i=0..n) for(j=0..n) {}",
        "visualization": "all n x n pairs grid",
        "latency_impact": "~100-500ms (Quadratic)",
        "recommendation": "[WARNING]: Avoid for large datasets. Refactor using Hash Maps O(1) or Binary Search O(log n)."
    },
    "O(2^n)": {
        "pattern": "9. Branching Recursion",
        "code_example": "T(n) = T(n-1) + T(n-2)",
        "visualization": "doubles per tree level",
        "latency_impact": "> 5,000ms (Exponential)",
        "recommendation": "[CRITICAL WARNING]: Refactor immediately with Dynamic Programming / Memoization O(n)."
    },
    "O(n!)": {
        "pattern": "10. Permutations",
        "code_example": "for (c : choices) permute(rest)",
        "visualization": "n x (n-1) x ... x 1 paths",
        "latency_impact": "> 60,000ms (Factorial Explosion)",
        "recommendation": "[CRITICAL WARNING]: Unbounded search space. Apply Pruning or Heuristic Search."
    }
}

class TimeComplexityProfiler:
    """
    Profiles code snippets and task operations against the 10 Time Complexity Patterns.
    """
    def profile_code(self, code_snippet: str) -> Dict[str, Any]:
        """Analyzes code structure to estimate Big-O complexity."""
        snippet_lower = code_snippet.lower()

        if "permute" in snippet_lower or "combinations" in snippet_lower:
            big_o = "O(n!)"
        elif snippet_lower.count("for ") >= 2 or snippet_lower.count("while ") >= 2:
            if "for" in snippet_lower and ("binarysearch" in snippet_lower or "log" in snippet_lower):
                big_o = "O(n log n)"
            else:
                big_o = "O(n^2)"
        elif "sort(" in snippet_lower or "sorted(" in snippet_lower:
            big_o = "O(n log n)"
        elif "for " in snippet_lower or "while " in snippet_lower:
            if "/ 2" in snippet_lower or ">>= 1" in snippet_lower:
                big_o = "O(log n)"
            else:
                big_o = "O(n)"
        elif ".get(" in snippet_lower or "[" in snippet_lower:
            big_o = "O(1)"
        else:
            big_o = "O(1)"

        pattern_info = COMPLEXITY_PATTERNS.get(big_o, COMPLEXITY_PATTERNS["O(1)"])
        return {
            "big_o": big_o,
            "pattern_name": pattern_info["pattern"],
            "visualization": pattern_info["visualization"],
            "latency_impact": pattern_info["latency_impact"],
            "recommendation": pattern_info["recommendation"]
        }
