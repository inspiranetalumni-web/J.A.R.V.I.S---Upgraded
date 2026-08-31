# Agent: Proactive Observer Agent v2.0
### *"The best time to fix a problem is before it becomes one."*

**Runtime:** E-Core Thread 6 (affinity mask 0xFF0) | **Poll Cycle:** 5 seconds  
**Monitors:** WMI thermal zones, GPU metrics, RSS memory, log tail scanner  
**Auto-Actions:** Thermal → model unload (auto); Memory OOM → service restart (auto)

---

## 1. Observer State Machine

```
MONITORING (nominal)
  ↓ anomaly threshold exceeded
DIAGNOSING (< 500ms analysis)
  ↓ auto-fix confidence ≥ 0.8 AND action is read-safe
HEALING (auto, no HITL)
  ↓ auto-fix confidence < 0.8 OR mutating action
NOTIFYING (HUD modal + TTS)
  ↓ user decides
    [Y] → HEALING
    [N] → MONITORING (anomaly logged, operator dismissed)
    [Timeout 60s] → MONITORING (auto-dismiss, anomaly logged)
```

---

## 2. Real Thermal Event — Step-By-Step Timeline

```
2026-08-27 22:47:00 — Observer Cycle #24,264:
  WMI reading: cpu_temp_c=71.3°C (below 72°C WARNING)
  RAM: 12.1 GB / 14.5 GB — nominal
  GPU util: 67% — moondream vision task active
  Status: ALL_NOMINAL

2026-08-27 22:47:35 — Observer Cycle #24,271:
  WMI reading: cpu_temp_c=74.8°C (≥ 72°C → WARNING threshold)
  RAM: 12.3 GB / 14.5 GB
  GPU util: 72%
  → DIAGNOSING: classify_anomaly() → "THERMAL_WARNING"
  → Fix catalog: unload models (confidence 0.95, auto_safe=True)
  → Executing AUTO-FIX: POST http://127.0.0.1:8765/brain/unload
  → TTS: "Sir, thermal warning detected. I'm unloading moondream."
  → Time to auto-action: 2.3 seconds from threshold detection

2026-08-27 22:47:40 — Fix confirmed:
  WMI reading: cpu_temp_c=74.8°C (still elevated but stable)
  GPU util: 5% (moondream evicted from VRAM)
  RAM: 9.8 GB (2.5 GB freed by model eviction)

2026-08-27 22:48:00 — Temperature normalizing:
  cpu_temp_c=69.2°C → trending down
  Status: RECOVERING

Maximum temperature recorded: 74.8°C (stayed 5.2°C below CRITICAL 80°C threshold)
```

---

## 3. Proactive Advisory Examples

```python
# Beyond reactive fault detection — proactive insights:

PROACTIVE_ADVISORIES = [
    {
        "condition": "RAM > 12.0 GB AND model loaded for > 30 minutes without query",
        "advice": "Sir, the model has been idle for 31 minutes. Shall I unload it to free 2.1 GB?",
        "auto_action": None,  # Advisory only
        "hud_color": "BLUE"
    },
    {
        "condition": "benchmark_delta > 15% from 7-day moving average",
        "advice": "Sir, today's TTS latency (294ms) is 18% higher than the 7-day average (249ms). Investigation recommended.",
        "auto_action": None,
        "hud_color": "AMBER"
    },
    {
        "condition": "ChromaDB size > 500 entries AND last consolidation > 7 days",
        "advice": "Memory store has 512 facts and hasn't been consolidated in 9 days. Run consolidation?",
        "auto_action": "schedule_consolidation_tonight",
        "hud_color": "BLUE"
    },
    {
        "condition": "NVMe temperature > 60°C AND active write task running",
        "advice": "NVMe is at 62°C during write task. Normal, but pausing large file operations is advisable.",
        "auto_action": None,
        "hud_color": "AMBER"
    }
]
```

---

## 4. Endpoints

```
POST   /observer/start      → Boot observer daemon on E-Core thread
POST   /observer/stop       → Graceful shutdown (completes current cycle)
GET    /observer/status     → {
                               "monitoring": true,
                               "cycle_count": 24271,
                               "cpu_temp_c": 69.2,
                               "ram_used_gb": 9.8,
                               "gpu_util_pct": 5,
                               "active_anomalies": [],
                               "last_auto_action": "brain_unload @ 22:47:40",
                               "last_cycle_ms": 231.4
                             }
```
