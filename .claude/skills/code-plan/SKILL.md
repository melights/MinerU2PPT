---
name: code-plan
description: Generate and iteratively refine a PRD-first, task-only blueprint focused on execution task decomposition (not solution redesign). Write the plan file directly first, run task-completeness loops, require independent review, then auto-invoke coding with the saved plan.
argument-hint: [optional-spec-path-or-topic]
user-invocable: true
---

# Task Decomposition Planner (PRD-First + Minimal Fields)

Create a task-only execution blueprint from PRD. Focus on task decomposition and dependency ordering, not architecture redesign. After plan finalization, auto-invoke `coding --plan <saved-plan-path>`.

## Core Planning Policy (MANDATORY)

1. **Task-only output**
   - Do not write phase narrative or standalone requirement sections.

2. **PRD-first decomposition mode (default)**
   - Build tasks directly from PRD sections and IDs.
   - Do not re-design requirements already finalized in PRD.
   - Do not introduce new architecture proposals unless explicitly requested.

3. **Task controls workflow; PRD controls detail**
   - Tasks define execution order and acceptance gates.
   - PRD remains source of detailed business/functional requirements.

4. **Fixed default task chain**
   - `I100 -> Q200 -> T300 -> E400 -> D500 -> C900`
   - `E400` may be N/A only with explicit rationale.

5. **File-first generation**
   - Write initial file directly to `docs/plan/` without pre-confirmation.

6. **Task-completeness loop**
   - Keep patching until all required tasks/fields/rules are complete.

7. **Independent review gate**
   - Run `prd-plan-coverage-review-agent`; patch and re-review until PASS.

## Required Task Fields (MANDATORY)

Each task must include exactly these fields:
- Subject
- Description
- Blocked By
- Acceptance

## Description Content Rules (MANDATORY)

Every task `Description` must include:
- `PRD Section Refs: [PRD §x.y, ...]`
- `Runtime Task ActiveForm: <present-continuous phrase>`
- Concrete executable notes for that task

If there is no formal PRD file, use:
- `PRD Section Refs: [Conversation Baseline: <short-anchor>]`

## Runtime Task Mapping Rules (MANDATORY)

To support direct `TaskCreate(subject, description, activeForm)` mapping in `/coding`:
- `Subject` must be imperative and concise (e.g., "Run integration tests").
- `Runtime Task ActiveForm` must be present-continuous and execution-focused (e.g., "Running integration tests").
- `Description` must be directly reusable as runtime task description without rewording.
- Keep one execution intent per task; avoid multi-action overloaded tasks.

## Mapping Rules (MANDATORY)

- No standalone `requirement` task type/section.
- `I100` must include implementation scope and unit-test intent.
- `T300` (integration) and `E400` (e2e) must be separate tasks.
- `Blocked By` chain must be executable end-to-end.

## Refactor/Migration Add-on Rules (MANDATORY when applicable)

Must add:
- `M600` cutover to single active path
- `M700` legacy retirement/deletion
- `M800` no-residual-legacy proof

And `C900` must be blocked by `M800` (in addition to normal chain).

## Workflow

### 1) Resolve planning input
Priority:
1. Skill argument (path/topic)
2. Recent conversation context
3. One clarification question if ambiguous

### 2) Lightweight codebase sanity check (non-design)
Use minimal `Glob`/`Grep`/`Read` only to confirm:
- referenced modules/files exist,
- no obvious layering/import-boundary conflict for planned tasks,
- test entrypoints referenced by tasks are present.

Do not perform deep redesign or alternative architecture exploration in this step.

### 3) Write initial plan file directly
- Save under `docs/plan/`
- Filename must end with `-plan.md`

### 4) Task-completeness loop
Verify and patch until all are true:
- Required chain tasks exist (`I100/Q200/T300/E400/D500/C900`)
- Every task has `Subject/Description/Blocked By/Acceptance`
- Every task description includes valid PRD section refs
- Mapping rules are satisfied
- For refactor/migration: `M600/M700/M800` exist and `C900` is blocked by `M800`

### 5) Independent review gate
Use `Task` with subagent `prd-plan-coverage-review-agent`.
If BLOCK, patch and re-run until PASS.

### 6) Full file readback to user
Read and present full final plan file with concise closure/review summary.

### 7) Auto-transition to coding (mandatory)
Immediately invoke:
- `coding --plan <final-plan-path>`

Do not request an extra planning-to-coding approval step unless user explicitly asks to pause.

## Important Constraints

- Do not implement code changes directly inside this skill.
- Coding execution must occur via `coding --plan <final-plan-path>`.
- Do not stop while blocking gaps remain.
- Do not bypass independent review gate.
- Do not add extra design/architecture sections beyond PRD-backed task decomposition.
- Do not expand scope with speculative enhancements.