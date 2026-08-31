# Agent: Workflow Generator Agent v2.0 — n8n JSON Synthesis Engine
### *"Describe what you want. The system builds the machine to do it."*

**Model:** `qwen2.5-coder:1.5b` | **Output:** Valid n8n workflow JSON → optional REST deploy  
**Latency:** Generation: 34ms TTFT + ~1.5s full JSON | Deploy: ~200ms POST  
**Trigger:** Voice: "automate this", "create a workflow", "schedule X every Y"

---

## 1. n8n Node Type Quick Reference

```json
{
  "trigger_nodes": [
    "n8n-nodes-base.webhook",          // HTTP trigger from external systems
    "n8n-nodes-base.scheduleTrigger",  // Time-based (cron) trigger
    "n8n-nodes-base.manualTrigger",    // One-time manual execution
    "n8n-nodes-base.localFileTrigger"  // File system change trigger
  ],
  "action_nodes": [
    "n8n-nodes-base.httpRequest",      // HTTP GET/POST to any API
    "n8n-nodes-base.code",             // JavaScript/Python execution
    "n8n-nodes-base.writeBinaryFile",  // Write file to disk
    "n8n-nodes-base.readBinaryFile",   // Read file from disk
    "n8n-nodes-base.sqlite",           // Query/insert into SQLite
    "n8n-nodes-base.if",               // Conditional branching
    "n8n-nodes-base.wait",             // Delay/sleep
    "n8n-nodes-base.set"               // Transform/map data
  ],
  "output_nodes": [
    "n8n-nodes-base.respondToWebhook", // Send HTTP response
    "n8n-nodes-base.emailSend"         // Send email (local SMTP)
  ]
}
```

---

## 2. Example: Voice → Generated n8n JSON

```
Voice: "Create a workflow that backs up my SQLite database every night at midnight"

Generated Plan:
  1. scheduleTrigger: cron "0 0 * * *" (midnight)
  2. code: read path from env, generate timestamp filename
  3. readBinaryFile: read E:\J.A.R.V.I.S\data\jarvis.db
  4. writeBinaryFile: write to E:\J.A.R.V.I.S\data\backups\jarvis_YYYY-MM-DD.db
  5. httpRequest: POST http://127.0.0.1:8765/audio/say
              body: {"text": "Nightly backup complete."}
```

```json
{
  "name": "Nightly SQLite Backup",
  "nodes": [
    {
      "id": "node-trigger",
      "name": "Midnight Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [250, 300],
      "parameters": {
        "rule": {"interval": [{"field": "cronExpression", "expression": "0 0 * * *"}]}
      }
    },
    {
      "id": "node-gen-name",
      "name": "Generate Filename",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 300],
      "parameters": {
        "jsCode": "const d = new Date(); const ts = d.toISOString().slice(0,10);\nreturn {backup_path: `E:\\\\J.A.R.V.I.S\\\\data\\\\backups\\\\jarvis_${ts}.db`};"
      }
    },
    {
      "id": "node-read",
      "name": "Read Database",
      "type": "n8n-nodes-base.readBinaryFile",
      "typeVersion": 1,
      "position": [650, 300],
      "parameters": {"filePath": "E:\\J.A.R.V.I.S\\data\\jarvis.db"}
    },
    {
      "id": "node-write",
      "name": "Write Backup",
      "type": "n8n-nodes-base.writeBinaryFile",
      "typeVersion": 1,
      "position": [850, 300],
      "parameters": {"filePath": "={{ $json.backup_path }}"}
    },
    {
      "id": "node-notify",
      "name": "Notify J.A.R.V.I.S.",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1050, 300],
      "parameters": {
        "method": "POST",
        "url": "http://127.0.0.1:8765/audio/say",
        "contentType": "json",
        "body": "{\"text\": \"Nightly SQLite backup complete, Sir.\"}"
      }
    }
  ],
  "connections": {
    "Midnight Trigger":  {"main": [[{"node": "Generate Filename", "type": "main", "index": 0}]]},
    "Generate Filename": {"main": [[{"node": "Read Database",     "type": "main", "index": 0}]]},
    "Read Database":     {"main": [[{"node": "Write Backup",      "type": "main", "index": 0}]]},
    "Write Backup":      {"main": [[{"node": "Notify J.A.R.V.I.S.", "type": "main", "index": 0}]]}
  },
  "active": false,
  "settings": {"executionOrder": "v1"}
}
```

---

## 3. Deployment & Activation

```powershell
# Deploy generated workflow to n8n:
$workflow = Get-Content "n8n/generated/Nightly_SQLite_Backup_a1b2c3d4.json" | ConvertFrom-Json
$response = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:5678/api/v1/workflows" `
  -Headers @{"X-N8N-API-KEY" = $env:N8N_API_KEY; "Content-Type" = "application/json"} `
  -Body ($workflow | ConvertTo-Json -Depth 20)

$workflowId = $response.id
Write-Host "Deployed workflow ID: $workflowId"

# Activate the workflow:
Invoke-RestMethod -Method PATCH `
  -Uri "http://127.0.0.1:5678/api/v1/workflows/$workflowId" `
  -Headers @{"X-N8N-API-KEY" = $env:N8N_API_KEY; "Content-Type" = "application/json"} `
  -Body '{"active": true}'

Write-Host "Workflow $workflowId activated - will run nightly at midnight"
```
