---
name: coding-workflow-guide
description: A user-invocable guide that displays the standard operating procedure for software development in this project.
---
# Coding Workflow Guide (PRD-First, Task-Driven)

This document defines the standard workflow for development tasks in this project.

## Core Philosophy

- **PRD defines detail** (requirements, constraints, acceptance logic).
- **Task plan defines execution flow** (what to do, in what order, with what gates).
- **Human review is the final quality gate** before commit.

Default flow avoids over-design during planning and emphasizes executable tasks.

## Standard Workflow

### 1) `/code-interview` (optional when requirements are already clear)
- **Goal:** Convert ideas into a structured PRD.
- **Output:** `docs/interview/spec-<feature>.md`
- **Requirement:** PRD should use standard section numbering (e.g., `2.1`, `4.2`) for downstream referencing.

### 2) `/code-plan` (required for non-trivial work)
- **Goal:** Convert PRD into a task-only execution plan.
- **Output:** `docs/plan/<feature>-plan.md`
- **Plan style:** Minimal task schema only:
  - `Subject`
  - `Description` (must include `PRD Section Refs`)
  - `Blocked By`
  - `Acceptance`
- **Default chain:** `I100 -> Q200 -> T300 -> E400 -> D500 -> C900`
- **Planning mode constraint:** task decomposition only (no architecture redesign by default).
- **Validation:** run independent plan coverage review.
- **Auto-transition:** after plan is finalized, `/code-plan` invokes `/coding --plan <plan-path>`.

### 3) `/coding`
- **Goal:** Execute the latest task blueprint from `/code-plan`.
- **Behavior:** follow task dependencies and acceptance gates.
- **Execution scope:** implement code + required tests/checks + docs updates from tasks.

### 4) Human Review (manual gate)
- **Goal:** Final human verification of correctness, scope, and maintainability.
- **Why:** automated refactor review is not a required stage in this workflow.

### 5) `/code-commit`
- **Goal:** Commit after manual review and task acceptance are complete.
- **Gate expectation:** required checks/tests pass and intended files only.

### 6) `/code-docs` (optional, conditional)
Use only when long-term project memory/rules need updates (not for every change).

---

## Optional Stage: `/code-review-refactor`

Not a default step.
Use only for high-risk cases, such as:
- cross-layer or wide refactors,
- security-sensitive changes,
- unstable regressions needing additional automated refactor pass.

---

## Handoff Format

```markdown
## HANDOFF: /code-plan -> /coding

### Context
- Plan generated from: `docs/interview/spec-<feature>.md`
- Plan file: `docs/plan/<feature>-plan.md`

### Task Chain
- I100 -> Q200 -> T300 -> E400 -> D500 -> C900

### Notes
- PRD controls requirement detail via `PRD Section Refs`.
- Execute tasks in `Blocked By` order.
```

```markdown
## HANDOFF: /coding -> Human Review

### Context
- Executed plan: `docs/plan/<feature>-plan.md`

### Files Modified
- <file list>

### Validation Evidence
- Unit: <result>
- Syntax/Static: <result>
- Integration: <result>
- E2E/Smoke: <result or N/A rationale>

### Review Focus
- Scope adherence to PRD refs
- Risky code paths and edge behavior
```

---

## Final Report Format

```markdown
ORCHESTRATION REPORT
====================
Workflow: <feature name>
Steps Executed: /code-interview (optional) -> /code-plan -> /coding -> Human Review -> /code-commit

SUMMARY
-------
PRD-first task plan was generated and executed. Human review completed before commit.

KEY OUTPUTS
-----------
- PRD: `docs/interview/spec-<feature>.md` (if used)
- Plan: `docs/plan/<feature>-plan.md`
- Commit: `<commit message>` (SHA: <sha>)

FINAL STATUS
------------
RECOMMENDATION: SHIP | HOLD
```
