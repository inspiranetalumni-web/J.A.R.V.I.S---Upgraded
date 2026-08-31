# Agent: Cyclic Orchestration Agent v2.0 — Multi-Step Workflow Director
### *"Complex tasks are just simple steps chained with proper error handling."*

**Model:** `qwen2.5-coder:1.5b` | **Checkpoint:** Merkle-hashed JSON (tamper-detectable)  
**Max Retries:** 3 per step → HITL escalation | **Triggers:** Voice workflow | n8n dispatch | file watcher

---

## 1. Goal Decomposition — JSON Plan Format

```python
# jarvis/workflows/orchestration.py — Plan schema

EXAMPLE_PLAN = {
    "workflow_id": "deploy_n8n_workflow_verify",
    "goal": "Export n8n workflow to JSON, deploy to n8n, then test webhook endpoint",
    "steps": [
        {
            "step_id": "step_1_export",
            "description": "Read current workflow definition from n8n",
            "tool": "playwright_navigate",
            "args": {"url": "http://127.0.0.1:5678/workflow/WF-2847"},
            "expected_exit": "HTTP 200",
            "retry_limit": 3
        },
        {
            "step_id": "step_2_post_to_n8n",
            "description": "POST workflow JSON to n8n REST API",
            "tool": "run_powershell",
            "args": {"command": "curl -X POST http://127.0.0.1:5678/api/v1/workflows -H 'Content-Type: application/json' -d @data/workflows/backup.json"},
            "expected_exit": "returncode 0",
            "retry_limit": 3,
            "depends_on": ["step_1_export"]
        },
        {
            "step_id": "step_3_webhook_test",
            "description": "Test the deployed webhook endpoint responds 200",
            "tool": "run_powershell",
            "args": {"command": "curl -f http://127.0.0.1:5678/webhook/backup-trigger"},
            "expected_exit": "returncode 0",
            "retry_limit": 3,
            "depends_on": ["step_2_post_to_n8n"]
        }
    ]
}
```

---

## 2. Execution Loop — Core Orchestrator

```python
# jarvis/workflows/executor.py — Step execution with retry + reflection
from jarvis.workflows.checkpoint import CheckpointManager, WorkflowCheckpoint, CheckpointStep
from jarvis.workflows.reflection import reflect_on_failure
from jarvis.workflows.loop_guard import CircularReflectionGuard
import requests, time

class WorkflowExecutor:
    def __init__(self):
        self.checkpoint_mgr = CheckpointManager()
    
    async def execute_plan(self, plan: dict) -> dict:
        """Execute a multi-step workflow with checkpoint persistence."""
        session_id = f"session_{plan['workflow_id'][:8]}_{int(time.time())}"
        
        # Check for resumable checkpoint
        checkpoint = self.checkpoint_mgr.scan_for_incomplete()
        if checkpoint:
            print(f"[ORCHESTRATOR] Resuming checkpoint: {checkpoint.active_node}")
        else:
            checkpoint = WorkflowCheckpoint(
                session_id=session_id,
                workflow_id=plan["workflow_id"],
                created_at=time.time(),
                updated_at=time.time(),
                active_node=plan["steps"][0]["step_id"],
                pending_steps=[CheckpointStep(**{k: v for k, v in s.items() if k != "depends_on"}) 
                               for s in plan["steps"]]
            )
        
        results = []
        loop_guard = CircularReflectionGuard()
        
        for step_data in checkpoint.pending_steps[:]:
            step = CheckpointStep(**vars(step_data)) if hasattr(step_data, '__dict__') else step_data
            checkpoint.active_node = step.step_id
            
            print(f"[ORCHESTRATOR] → {step.step_id}: {step.tool}({step.arguments})")
            
            success = False
            for attempt in range(step.retry_limit or 3):
                # Execute step
                result = await self._execute_tool(step.tool, step.arguments)
                
                if result.get("success"):
                    step.status = "success"
                    step.completed_at = time.time()
                    checkpoint.completed_steps.append(step)
                    checkpoint.pending_steps.remove(step_data)
                    self.checkpoint_mgr.save(checkpoint)
                    loop_guard.reset()
                    results.append({"step": step.step_id, "status": "success"})
                    success = True
                    break
                
                # Failure — try reflection
                diagnosis = reflect_on_failure(
                    step.step_id, step.tool, step.arguments,
                    result.get("stderr", ""), plan["goal"], attempt + 1
                )
                
                if not diagnosis or loop_guard.check_and_record(diagnosis.get("corrected_arguments", {})):
                    # Escalate to HUD
                    await self._escalate_to_hud(step, result, diagnosis)
                    return {"status": "escalated", "step": step.step_id}
                
                step.arguments = diagnosis["corrected_arguments"]
                step.attempt_count = attempt + 1
            
            if not success:
                return {"status": "failed", "step": step.step_id, "completed": [r["step"] for r in results]}
        
        return {"status": "complete", "steps": results}
    
    async def _execute_tool(self, tool: str, args: dict) -> dict:
        """Dispatch tool call via FastAPI MCP proxy."""
        try:
            resp = requests.post("http://127.0.0.1:8765/mcp/call", json={
                "tool": tool, "params": args
            }, timeout=30)
            data = resp.json()
            return {"success": resp.status_code == 200, "result": data, "stderr": data.get("error", "")}
        except Exception as e:
            return {"success": False, "result": {}, "stderr": str(e)}
```

---

## 3. Checkpoint Recovery — Boot Scan

```python
# Called during jarvis_boot.ps1 → python -m jarvis.main startup:
def recover_incomplete_workflows():
    mgr = CheckpointManager()
    incomplete = mgr.scan_for_incomplete()
    if incomplete:
        print(f"[BOOT] Found {len(incomplete)} incomplete workflows")
        for cp in incomplete:
            print(f"  - {cp.workflow_id}: stopped at {cp.active_node}")
        # TTS announcement:
        requests.post("http://127.0.0.1:8765/audio/say", json={
            "text": f"Sir, I found {len(incomplete)} unfinished workflow{'s' if len(incomplete) > 1 else ''} from the previous session. Shall I resume them?"
        })
```
