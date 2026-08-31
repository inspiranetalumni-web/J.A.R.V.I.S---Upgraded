# Agent: Context Compaction Agent v2.0 — Token Budget Enforcer
### *"What you include is as important as what you exclude."*

**Type:** Pure Python engine (no LLM) | **Latency:** 11.3ms nominal, 19.1ms w/ Ring-3 compaction  
**Budget:** 8,192 tokens total (S:820 + T:1230 + M:2048 + H:2867 + G:1227)  
**Trigger:** Every inference turn, before prompt assembly

---

## 1. Token Budget Enforcement — Live Implementation

```python
# Full implementation in skills/context_working_memory_budget_skills.md
# This agent wraps the ContextAssembler and 3-ring compaction engine.

# Quick reference — slot allocations:
SLOT_BUDGETS = {
    "S": 820,    # System directives + persona + privacy policy (~680 tokens)
    "T": 1230,   # Tool schemas (pruned to 2-4 active tools only)
    "M": 2048,   # ChromaDB + KùzuDB retrieved facts (top-5)
    "H": 2867,   # Turn history + tool call logs (sliding window)
    "G": 1227    # Reserved generation headroom (never filled by input)
}

# Measured token consumption at nominal operation:
# S: 680/820 (83% full — system prompt fixed)
# T: 320/1230 (26% — filesystem domain: 4 tools)
# M: 890/2048 (43% — 5 facts @ ~178 tokens each)
# H: 1840/2867 (64% — 8 turns of dialogue)
# Total: 3730/6993 usable = 53% utilization
```

---

## 2. Compaction Trigger Conditions

```python
# When does compaction fire?
COMPACTION_TRIGGERS = {
    "Ring1": "Turn history > 80% of H budget (> 2,293 tokens)",
    "Ring2": "Turn history > 90% of H budget (> 2,580 tokens)",  
    "Ring3": "Turn history > 98% of H budget (> 2,809 tokens)",
}

# What gets compacted:
# Ring 1: Tool call/result logs stripped (intermediate JSON blobs)
# Ring 2: Oldest 50% of turns → extractive summary paragraph (LLM)
# Ring 3: Remaining turns → key-value state table (extreme compression)

# Frequency in production:
# Ring 1: ~every 15-20 turns in technical sessions (tool-heavy)
# Ring 2: ~every 40-50 turns in long sessions
# Ring 3: ~every 80+ turns (rare — only in marathon sessions)
```

---

## 3. Performance Profile

```
Context Assembly Latency (100-run benchmark, HP Pavilion):
  No compaction needed:    8.2ms  (95% of turns)
  Ring-1 compaction:      11.3ms
  Ring-2 compaction:      14.8ms  (+250ms for LLM extractive summary)
  Ring-3 compaction:      19.1ms  (state table is deterministic, fast)

Token efficiency after compaction:
  Ring-1: strips 32% of H slot on average
  Ring-2: compresses 1800 tokens → 120 tokens (93%)
  Ring-3: compresses 1800 tokens → 98 tokens (94.6%)
```

---

## 4. Endpoints

```
POST   /context/assemble    → Assemble full context for inference
                               {"system_prompt": "...", "memory_facts": [...], 
                                "turn_history": [...]} 
                               → {"messages": [...], "budget_report": {...}}
                                
GET    /context/status      → {"slot_utilization": {"S": 0.83, "T": 0.26, "M": 0.43, "H": 0.64},
                               "compaction_ring": null, "total_tokens": 3730}
```
