# Skill: Real-World Flaws, Edge Cases & Future Failure Modes v3.0 (Stark Audit)
### *"Engineering transparency: Analyzing where v3.0 will encounter real-world friction and how to survive it."*

**Audit Scope:** Real-world hardware stress, optical ambiguity, network jitter, concurrency collisions, and memory drift in J.A.R.V.I.S. v3.0  
**Host Target:** Intel Core i7-1255U (16 GB Shared DDR4) + Iris Xe Graphics + Windows 11  
**Principle:** Identify every single physical failure mode before it happens in production.

---

## 1. Master v3.0 Real-World Flaws & Failures Matrix

| # | Subsystem | Documented Spec | Real-World Physical Reality & Flaw | Root Cause | Engineered Mitigation |
| :- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Shared Memory Contention** | 16 GB DDR4 shared RAM ceiling | Iris Xe GPU borrows from system RAM. Running LLM + MediaPipe 3D + DXGI + PySide6 overlay simultaneously can trigger **Windows DWM frame stutter** or VRAM allocation delay. | Zero dedicated VRAM; GPU & CPU contend for same 3200MHz DDR4 memory bus. | Force `OLLAMA_MAX_LOADED_MODELS=1` + drop optical gesture loop to 30 FPS under heavy LLM load. |
| **2** | **Optical Gesture False Triggers** | 60 FPS 3D MediaPipe tracking | Adjusting glasses, drinking coffee, or waving at someone triggers **accidental clicks or unexpected audio mutes**. | 3D hand tracking cannot distinguish deliberate control gestures from ambient human movements. | Require a 0.3s gesture dwell time + visual confirmation ring on HUD before triggering actions. |
| **3** | **Wi-Fi 6 LAN Mesh Jitter** | < 8ms LAN RPC offload latency | Microwave interference, Wi-Fi channel congestion, or packet drops cause **50ms-300ms latency spikes or stream disconnects**. | Wireless LAN packet loss & TCP retransmission stalls. | Enforce 3.0s RPC timeout; if connection degrades, auto-failover immediately back to local host. |
| **4** | **BLE Sensor Sleep & Freeze** | Real-time vital stress index | Smartwatches enter low-power sleep modes, causing **frozen stress readings** (e.g., stuck in RED Tactical mode). | BLE connection timeout / power-saving GATT disconnect. | 15s heartbeat timeout: if BLE fails to update, gracefully reset stress index to `NOMINAL (0.0)`. |
| **5** | **Sarcasm Misinterpretation** | Operator feedback harvester | Sarcastic operator remarks (e.g., *"Oh sure, delete all my files"*) could be **mislearned as a permanent preference rule**. | SLMs struggle with acoustic sarcasm and pragmatic irony. | Require rule frequency $\ge 3$ occurrences + explicit HUD confirmation before rule promotion. |
| **6** | **SQLite DB Lock Contention** | House Party Parallel Swarm | 4 sub-agents writing to ChromaDB / SQLite simultaneously trigger **`database is locked` operational errors**. | SQLite single-writer lock restriction (`SQLITE_BUSY`). | Single-writer queue actor (`asyncio.Queue`) for all database writes across swarm workers. |
| **7** | **WASAPI Audio Underruns** | < 300ms clause TTS delivery | CPU spikes to 95%+ cause **robotic voice crackling / stuttering** during heavy background pytest runs. | Audio buffer underrun when P-Core thread scheduler starves soundcard buffer. | Pin Kokoro TTS thread priority to `REALTIME_PRIORITY_CLASS` + increase WASAPI buffer size to 64ms. |
| **8** | **UIAutomation Handle Staleness** | 9ms UIA element click | React / Electron apps rewrite DOM dynamically, causing **`COMError: Element not available`** when clicking. | UIAutomation COM handle invalidated between find and click. | Catch `COMError` and retry with fresh element lookup or fall back to moondream vision grounding. |

---

## 2. Technical Deep-Dive into the Top 4 Failure Modes

### 2.1 Shared DDR4 Memory Bus Bottleneck (Iris Xe VRAM Allocation)

```
Physical Reality on HP Pavilion 14-dv2xxx:
- Intel Iris Xe Graphics has ZERO dedicated VRAM. It shares 16 GB DDR4-3200 RAM with the CPU.
- Shared bandwidth = ~51.2 GB/s maximum.

When running simultaneously:
1. Llama 3.2 3B LLM Inference:   ~2.1 GB RAM @ 38 tok/s   (uses ~28 GB/s memory bandwidth)
2. MediaPipe 3D Hand Tracking:   ~350 MB RAM @ 60 FPS     (uses ~8 GB/s bandwidth)
3. DXGI Desktop Capture (1080p): ~120 MB RAM @ 30 FPS     (uses ~4 GB/s bandwidth)
4. Kokoro TTS ONNX Synthesis:    ~180 MB RAM               (uses ~3 GB/s bandwidth)

Total memory bandwidth demand: ~43 GB/s (84% of total theoretical memory bus capacity!)

Failure Mode: When background processes (Windows Defender, Chrome) spike memory requests, 
              total bus demand exceeds 51.2 GB/s, causing desktop DWM stutter and audio popping.

Engineered Fix:
- Dynamically scale gesture camera capture from 60 FPS down to 30 FPS when LLM is actively streaming.
- Unload vision models (`moondream`) immediately after use (`keep_alive=0`).
```

---

### 2.2 Sarcasm & Implicit Preference Mislearning

```python
# Failure Scenario:
# User (frustrated): "Oh brilliant, why don't you just delete all python files next time?!"
# Naive Harvester extracts: "OPERATOR PREFERENCE: Delete all python files"
# Result: DANGEROUS RULE PROMOTED TO MEMORY.

# Production Mitigation Code (jarvis/learning/guard.py):
import re

DANGEROUS_VERBS = ["delete", "remove", "format", "clear", "wipe", "destroy", "shutdown"]

def validate_learned_rule_safety(rule_text: str) -> bool:
    """
    Blocks learning of rules containing destructive action verbs or sarcasm indicators.
    """
    rule_lower = rule_text.lower()
    
    # 1. Block destructive action verbs
    for verb in DANGEROUS_VERBS:
        if verb in rule_lower:
            print(f"[LEARNING GUARD] Blocked dangerous rule candidate: {rule_text}")
            return False
            
    # 2. Detect common sarcasm markers
    sarcasm_markers = ["oh sure", "oh brilliant", "why don't you just", "great job", "awesome choice"]
    if any(marker in rule_lower for marker in sarcasm_markers):
        print(f"[LEARNING GUARD] Sarcasm marker detected. Rule discarded: {rule_text}")
        return False

    return True
```

---

### 2.3 SQLite Lock Contention in Swarm Execution

```python
# Failure Scenario in House Party Protocol Swarm:
# Sub-Agent 1 (Security) writes audit event to database.db
# Sub-Agent 3 (Test Runner) writes test result to database.db at exact same millisecond
# Result: sqlite3.OperationalError: database is locked

# Production Mitigation: Single-Writer Actor Queue (jarvis/db/writer.py)
import asyncio, sqlite3

class AsyncDatabaseWriter:
    """
    Serializes all database writes across swarm workers through a single asyncio queue.
    Prevents SQLite lock contention completely.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.write_queue = asyncio.Queue()
        self._is_running = True

    async def start_writer_loop(self):
        conn = sqlite3.connect(self.db_path)
        while self._is_running:
            sql, params, future = await self.write_queue.get()
            try:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                conn.commit()
                if not future.done():
                    future.set_result(cursor.lastrowid)
            except Exception as e:
                if not future.done():
                    future.set_exception(e)
            finally:
                self.write_queue.task_done()

    async def execute_write(self, sql: str, params: tuple = ()) -> int:
        future = asyncio.get_running_loop().create_future()
        await self.write_queue.put((sql, params, future))
        return await future
```

---

## 3. Resilience & Failure Recovery Table

```
System Failure Recovery Latencies:
┌──────────────────────────────────────────────┬────────────────────────┐
│ Failure Scenario                             │ Recovery Mechanism     │
├──────────────────────────────────────────────┼────────────────────────┤
│ Gesture False Trigger (Accidental Click)     │ 0.3s Dwell Time Filter │
│ LAN Wi-Fi Mesh Disconnect / Timeout          │ 3.0s Fallback to Host  │
│ BLE Vital Sensor Disconnect                  │ 15s Reset to Nominal   │
│ SQLite Lock Collision                        │ Single-Writer Queue    │
│ WASAPI Audio Underrun / Crackle              │ REALTIME_PRIORITY Pin  │
│ UIA Handle Staleness (DOM Change)            │ COMError Retry + Vision│
└──────────────────────────────────────────────┴────────────────────────┘
```
