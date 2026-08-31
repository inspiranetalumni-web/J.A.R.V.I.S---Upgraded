# 🧠 J.A.R.V.I.S. Cognitive Architecture & Self-Upgrade Standard

This skill establishes the 3-tier cognitive classification framework (LLM vs RAG vs AI Agent vs Hybrid) and the permission-gated self-upgrade protocol for J.A.R.V.I.S. v3.1.

---

## 1. The 3 Cognitive Tiers & Hybrid Mode

```
                   ┌───────────────────────────────────────────────┐
                   │    J.A.R.V.I.S. Cognitive Tier Classifier    │
                   └───────────────────────┬───────────────────────┘
                                           │
         ┌───────────────────┬─────────────┴─────────────┬───────────────────┐
         ▼                   ▼                           ▼                   ▼
    🧠 LLM MODE         🔍 RAG MODE                🤖 AI AGENT MODE     ⚡ HYBRID MODE
  • Text Generation   • Doc/Vault Retrieval      • Goal Planning     • LLM + RAG + Agent
  • Internal Knowledge• Reads + Thinks           • Tool Execution    • Reads, Thinks & Acts
  • Low Complexity    • Medium Complexity        • High Complexity   • Maximum Autonomy
```

### Tier Comparison Matrix

| Feature | LLM Mode | RAG Mode | AI Agent Mode | Hybrid Mode |
|---|---|---|---|---|
| **Primary Goal** | Generate text from learned knowledge | Retrieve external information before generating | Plan, decide, & perform tasks autonomously | Combine retrieval, reasoning, & tool actions |
| **Knowledge Source** | Model training data | Vector Store (ChromaDB) + Knowledge Graph (KùzuDB) | LLM + Memory + MCP Tools + OS Actuation | Full System Context |
| **Tool Calling** | ❌ No | 🟢 Document Retrieval Only | 🟢 Full (APIs, DBs, Apps, CLI) | 🟢 Complete Tool Suite |
| **Action Execution**| ❌ No | ❌ No | 🟢 Yes (Hands-Free OS Control) | 🟢 Yes |
| **Core Formula** | **LLM Thinks** | **RAG Reads + Thinks** | **AI Agent Thinks + Acts** | **Reads, Thinks & Acts** |

---

## 2. Self-Improvement & Self-Upgrade Protocol

J.A.R.V.I.S. includes a self-evolution engine that generates structured upgrade proposals for system enhancements.

### Security & User Permission Escrow
1. **Proposal Stage:** J.A.R.V.I.S. generates `v3.1.0` upgrade proposal outlining components changed, risks, and benefits.
2. **Permission Escrow:** System enters `AWAITING_USER_APPROVAL` state. No code modifications occur automatically.
3. **Authorization:** The operator must explicitly authorize the upgrade via API payload (`approved: True`) or voice command (`"Authorize J.A.R.V.I.S. upgrade"`).
4. **Execution & Rollback:** Upgrades are applied atomically with automatic rollback snapshots saved in `data/backups/`.
