# ⚙️ J.A.R.V.I.S. Dynamic Task Workflows Master Standard (Modes 01 - 15)

This skill establishes the complete 15-part dynamic development workflow suite for J.A.R.V.I.S. to dynamically switch execution modes based on incoming task prompts.

---

## Mode 01: PRD Generator (`docs/prd-[feature].md`)
- **Trigger Words:** `write prd`, `prd for feature`, `create prd`, `generate prd`
- **Output:** Saves lean <2-page document to `docs/prd-[feature].md` with problem statement, user stories, acceptance criteria, scope, data model, and edge cases.

## Mode 02: Codebase Architecture Map (`AGENTS.md` / `JARVIS.md`)
- **Trigger Words:** `generate agents.md`, `scan codebase`, `repo spec`, `create jarvis.md`
- **Output:** Saves repo architecture specification to root `AGENTS.md` / `JARVIS.md` with project summary, stack versions, build commands, architecture tree, hard rules, and gotchas.

## Mode 03: Ultra Plan Mode (7-Step Strict Planning Protocol)
- **Trigger Words:** `ultra plan`, `plan mode`, `deep plan`
- **Output:** Halts code modifications and generates a 7-step pre-execution plan: Touched Files Audit, Behavior Mapping, 2-3 Approaches with Tradeoffs, Chosen Approach Justification, Incremental Verifiable Steps, Risks & Rollback, Sensitive Area Flags.

## Mode 04: Spec-Driven Development Engine
- **Trigger Words:** `write spec`, `spec driven`, `create spec`
- **Output:** Generates Given-When-Then specification, API contract schema, database migrations, UI states, and line-by-line acceptance checklists.

## Mode 05: Full UI & UX Design Brief Engine
- **Trigger Words:** `design brief`, `ui ux brief`, `ui brief`
- **Output:** Generates user journeys, screen layout hierarchies, component inventories (hover/empty/error/loading), typography & color tokens, motion parameters, and WCAG 2.1 AA accessibility guidelines.

## Mode 06: Sequential Implementation Plan
- **Trigger Words:** `implementation plan`, `build sequence`, `execution steps`
- **Output:** Generates an incremental build sequence where the app compiles and runs after EVERY single step. Sized `[S / M / L]`, riskiest unknowns first, file touch audits, and step-by-step verification checks.

## Mode 07: Wire Up an MCP Server
- **Trigger Words:** `wire mcp`, `setup mcp`, `mcp server`
- **Output:** Checks for official server registry, scaffolds custom MCP SDK tools, wires secrets through environment variables, generates `mcp_config.json`, and verifies end-to-end tool call execution.

## Mode 08: Connect Your Database
- **Trigger Words:** `connect database`, `connect db`, `database setup`
- **Output:** Selects client for stack, configures env vars in `.env.example`, defines entity schemas with indexes, generates migrations & rollback scripts, writes typed query helpers, and verifies seeding & read-back.

## Mode 09: Find Security Gaps (Red-Team Audit)
- **Trigger Words:** `find security gaps`, `security audit`, `audit security`
- **Output:** Conducts red-team security assessment focusing on AUTH, PAYMENTS, USER DATA. Audits secret leaks, injection (SQL/XSS/Command), IDOR, input validation, CVEs, rate limiting, and log leaks. Ranks severity with file:line references.

## Mode 10: Debug an Error Fast (No-Vibes Debugging)
- **Trigger Words:** `debug error`, `debug fast`, `fix error`
- **Output:** Reads stack trace, opens exact files, states expected vs actual behavior, ranks 3 hypotheses by likelihood, proves/kills each with empirical evidence, fixes root cause (not symptom), adds regression test, and delivers 2-line post-mortem.

## Mode 11: E2E Test Your Application (Playwright)
- **Trigger Words:** `e2e test`, `playwright test`
- **Output:** Configures Playwright E2E test suite. Tests core user flows first, uses role & label selectors (never brittle CSS), includes unhappy path isolation, enforces independent test state, configures headless CI & headed local debugging, and captures failure screenshots & traces.

## Mode 12: Clean Up Dead Code
- **Trigger Words:** `clean dead code`, `delete dead code`
- **Output:** Audits and purges unused exports, unreachable conditional branches, commented-out blocks, stale package dependencies, stuck feature flags, duplicate logic, and dead CSS/assets. Enforces ripgrep search before EVERY deletion.

## Mode 13: Write Clean Conventional Git Commits
- **Trigger Words:** `clean git commit`, `conventional commit`, `git commit`
- **Output:** Stages atomic commits split by concern. Formats `type(scope): subject` (<50 chars, imperative mood), body explaining WHY wrapped at 72 chars, ticket references, refactor separation, and zero secret/env commits.

## Mode 14: Hooks as Guardrails
- **Trigger Words:** `guardrail hooks`, `setup hooks`
- **Output:** Configures automated development guardrails: `PostToolUse` lint & typecheck, `PreToolUse` protected path blocking (`data/vault/`, `security/guardrails.py`), `Stop` session pytest verification, and `Notification` audio/HUD alerts.

## Mode 15: Turn a Task Into a Skill
- **Trigger Words:** `create skill`, `task to skill`, `turn into skill`
- **Output:** Converts repetitive developer workflows into reusable J.A.R.V.I.S. Skill modules. Automatically creates `skills/[name]/SKILL.md` with YAML frontmatter, trigger phrases, numbered workflow, asking vs inferring boundaries, and definition of done.
