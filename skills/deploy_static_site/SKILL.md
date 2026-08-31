---
name: deploy_static_site
description: Deploys static site to local web root
triggers: ['deploy site']
---

# Deploy Static Site Skill

## Overview
Deploys static site to local web root

## Workflow & Execution Steps
1. Parse operator input matching trigger phrases: 'deploy site'.
2. Initialize environment requirements and verify zero hardcoded path violations.
3. Execute core task logic with error isolation.
4. Verify execution success and present clean natural language output to operator.

## What J.A.R.V.I.S. Asks vs Infers
* **Asks:** Explicit target scope or ambiguous parameter overrides.
* **Infers:** System paths, hardware thread affinity, logging configurations.

## Definition of Done
- Task executes cleanly without raising unhandled exceptions.
- Output verified against expected schema contract.
