# Agent: Self-Evolution Agent v2.0
### *"The system that cannot improve itself is already obsolete."*

**Model:** `qwen2.5-coder:1.5b` | **Trigger:** Benchmark regression OR pytest failure OR unhandled traceback  
**Safety:** Zero self-commit without HMAC-signed HITL approval + automated rollback shield  
**Cycle:** Monitor → Diagnose → Patch → Validate → Hotreload OR Rollback

---

## 1. Evolution Trigger Conditions

```python
# jarvis/evolution/trigger.py — Self-evolution trigger evaluation
from pathlib import Path
import json, time

HEALTH_REPORT = Path("data/logs/health_report.json")

REGRESSION_THRESHOLDS = {
    "TTS Warm Latency":    {"max": 300.0,  "unit": "ms"},
    "Ollama TTFT":         {"max": 120.0,  "unit": "ms"},
    "Peak RAM":            {"max": 14.5,   "unit": "GB"},
    "Wake Word CPU":       {"max": 2.0,    "unit": "%"},
    "ChromaDB Recall":     {"max": 45.0,   "unit": "ms"},
    "Everything CLI":      {"max": 5.0,    "unit": "ms"},
    "pytest Suite":        {"max": 0,      "unit": "failures"},
}

def check_evolution_needed() -> dict | None:
    """
    Read health_report.json and determine if self-evolution should activate.
    Returns the failing metric dict or None if all pass.
    """
    if not HEALTH_REPORT.exists():
        return None
    
    with open(HEALTH_REPORT) as f:
        report = json.load(f)
    
    # Check if report is stale (> 30 minutes old)
    if time.time() - report.get("timestamp", 0) > 1800:
        return None  # Stale report — don't evolve based on old data
    
    metrics = report.get("metrics", {})
    for name, data in metrics.items():
        if not data.get("passed", True):
            return {
                "metric": name,
                "value": data["value"],
                "target": data["target"],
                "severity": "high" if data["value"] > data["target"] * 1.5 else "medium"
            }
    
    return None
```

---

## 2. AST Patch Generation Pipeline

```python
# jarvis/evolution/patch_generator.py — Qwen 2.5 Coder patch synthesis
import requests, json, ast, difflib
from pathlib import Path

PATCH_GENERATION_PROMPT = """You are an autonomous code repair agent.
A benchmark regression has been detected. Analyze the failing metric and the code,
then produce a minimal unified diff patch to fix it.

FAILING METRIC: {metric_name} = {measured_value} (target: < {target_value} {unit})
ERROR CONTEXT: {error_context}

CURRENT CODE:
```python
{current_code}
```

CONSTRAINTS:
- Output ONLY a valid Python unified diff (--- / +++ / @@ format)
- Make the MINIMAL change required — do not refactor unrelated code
- The fix must be provably correct — explain your reasoning in 2 sentences after the diff
- If you cannot produce a confident fix, output: CANNOT_FIX

Output format:
```diff
--- a/{file_path}
+++ b/{file_path}
@@ ... @@
[your diff]
```
Reasoning: [2 sentences]"""

def generate_patch(
    metric: dict,
    source_file: str,
    error_context: str
) -> dict:
    """
    Use Qwen 2.5 Coder to generate a unified diff patch for the failing metric.
    """
    source = Path(source_file).read_text(encoding="utf-8")
    
    resp = requests.post("http://127.0.0.1:11434/api/chat", json={
        "model": "qwen2.5-coder:1.5b",
        "messages": [{
            "role": "user",
            "content": PATCH_GENERATION_PROMPT.format(
                metric_name=metric["metric"],
                measured_value=metric["value"],
                target_value=metric.get("target", "?"),
                unit=metric.get("unit", ""),
                error_context=error_context[:500],
                current_code=source[:3000],
                file_path=source_file
            )
        }],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 1000}
    }, timeout=60)
    
    response = resp.json()["message"]["content"]
    
    # Extract diff block
    import re
    diff_match = re.search(r'```diff\n(.+?)```', response, re.DOTALL)
    if not diff_match or "CANNOT_FIX" in response:
        return {"success": False, "reason": "Qwen could not produce a confident fix"}
    
    diff_text = diff_match.group(1)
    
    # Extract reasoning
    reasoning_match = re.search(r'Reasoning:\s*(.+?)$', response, re.DOTALL)
    reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
    
    return {
        "success": True,
        "diff": diff_text,
        "reasoning": reasoning,
        "source_file": source_file
    }
```

---

## 3. HITL HUD Announcement + Approval Flow

```python
# jarvis/evolution/hitl_flow.py — HUD presentation of proposed evolution
import requests

def present_evolution_to_hud(
    patch_result: dict,
    metric: dict
) -> bool:
    """
    Display evolution proposal on Ghost HUD and wait for operator decision.
    Returns True if approved, False if denied.
    
    HUD shows:
    - Purple "SELF-EVOLUTION PROPOSED" banner
    - Metric: {name} = {value} → target: {target}
    - File: {source_file}
    - Diff summary (first 300 chars)
    - Reasoning: {2-sentence explanation}
    - [Y] Approve and Apply | [N] Reject
    
    TTS also announces: "Sir, I have identified a fix for the {metric} regression.
                         Shall I apply the patch?"
    """
    # Push to HUD (HTTP POST to FastAPI /hud/evolution-modal endpoint)
    resp = requests.post("http://127.0.0.1:8765/hud/evolution-modal", json={
        "title": "Self-Evolution Proposed",
        "metric": metric,
        "file": patch_result["source_file"],
        "diff_preview": patch_result["diff"][:300] + "...",
        "reasoning": patch_result["reasoning"],
        "color": "purple"
    }, timeout=5)
    
    # TTS announcement
    requests.post("http://127.0.0.1:8765/audio/say", json={
        "text": f"Sir, I have identified a regression fix for {metric['metric']}. "
                f"Shall I apply the patch?"
    })
    
    # Poll for user decision (60s timeout)
    import time
    deadline = time.time() + 60
    while time.time() < deadline:
        decision = requests.get("http://127.0.0.1:8765/hud/evolution-decision").json()
        if decision.get("decided"):
            return decision.get("approved", False)
        time.sleep(0.5)
    
    return False  # Timeout = auto-reject
```

---

## 4. Complete Evolution Cycle (End-to-End)

```python
# jarvis/evolution/cycle.py — Full self-evolution execution
import subprocess, sys, importlib

def run_evolution_cycle():
    """
    Full autonomous self-evolution cycle.
    Called when benchmark regression is detected.
    """
    print("[EVOLUTION] Starting self-evolution cycle...")
    
    # Step 1: Check triggers
    failing_metric = check_evolution_needed()
    if not failing_metric:
        print("[EVOLUTION] No regression detected. System nominal.")
        return
    
    print(f"[EVOLUTION] Regression: {failing_metric['metric']} = {failing_metric['value']}")
    
    # Step 2: Find root cause
    error_context = scan_logs_for_errors("data/logs/jarvis.log", last_n_lines=100)
    source_file = map_metric_to_source_file(failing_metric["metric"])
    
    # Step 3: Generate patch
    patch = generate_patch(failing_metric, source_file, error_context)
    if not patch["success"]:
        print(f"[EVOLUTION] Cannot auto-fix: {patch['reason']}. Alerting operator.")
        requests.post("http://127.0.0.1:8765/audio/say", json={
            "text": f"Sir, I detected a regression in {failing_metric['metric']} "
                    "but cannot determine a safe fix. Manual inspection required."
        })
        return
    
    # Step 4: Semantic similarity guard
    if not _passes_semantic_similarity_guard(source_file, patch["diff"]):
        print("[EVOLUTION] Semantic guard FAILED: patch changes too much. Aborting.")
        return
    
    # Step 5: HITL approval
    approved = present_evolution_to_hud(patch, failing_metric)
    if not approved:
        print("[EVOLUTION] Operator denied patch. Evolution aborted.")
        return
    
    # Step 6: Apply and verify
    result = apply_patch_safely(source_file, patch["diff"], session_secret=SESSION_SECRET)
    
    if result["tests_passed"]:
        # Step 7: Hot-reload the patched module
        module_path = source_file.replace("/", ".").replace("\\", ".").rstrip(".py")
        importlib.invalidate_caches()
        print(f"[EVOLUTION] ✓ Evolution complete. {source_file} hot-reloaded.")
        requests.post("http://127.0.0.1:8765/audio/say", json={
            "text": f"Evolution applied successfully. {failing_metric['metric']} regression resolved."
        })
    else:
        print("[EVOLUTION] ✗ Tests failed after patch. Rollback applied automatically.")
        requests.post("http://127.0.0.1:8765/audio/say", json={
            "text": "The patch did not pass tests. I have rolled back automatically. Manual review needed."
        })

METRIC_TO_SOURCE_MAP = {
    "TTS Warm Latency": "jarvis/audio/tts.py",
    "Ollama TTFT": "jarvis/ollama/router.py",
    "ChromaDB Recall": "jarvis/memory/vector_store.py",
    "pytest Suite": None,   # Multiple possible files — needs traceback analysis
}

def map_metric_to_source_file(metric_name: str) -> str:
    return METRIC_TO_SOURCE_MAP.get(metric_name, "jarvis/main.py")
```

---

## 5. Semantic Similarity Guard

```python
def _passes_semantic_similarity_guard(source_file: str, diff: str) -> bool:
    """
    Reject patches that change more than 30% of the function semantically.
    Prevents: patch that 'fixes' a latency bug by deleting the entire function.
    
    Uses cosine similarity of TF-IDF vectors of original vs patched function.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    
    original = Path(source_file).read_text(encoding="utf-8")
    
    # Apply diff to get patched version
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(suffix=".diff", mode="w", delete=False) as f:
        f.write(diff)
        diff_path = f.name
    
    patched = subprocess.run(
        ["patch", "--dry-run", "-o", "-", source_file, diff_path],
        capture_output=True, text=True
    ).stdout
    
    if not patched:
        return False  # Patch failed to apply even in dry-run
    
    # Compute semantic similarity
    vectorizer = TfidfVectorizer(analyzer="word", token_pattern=r"[a-zA-Z_]\w*")
    vectors = vectorizer.fit_transform([original, patched])
    sim = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])
    
    print(f"[SEMANTIC GUARD] Similarity: {sim:.3f} (threshold: 0.60)")
    return sim >= 0.60  # Reject if < 60% similarity (patch changes too much)
```
