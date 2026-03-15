---
name: code-docs
description: Route durable project knowledge into docs/ (architecture, testing, core-flow, api), then update CLAUDE.md and README.md references.
argument-hint: "--mode incremental|full"
---

# Code Docs Skill (Docs-First Knowledge Routing)

## Purpose

Persist reusable project knowledge into `docs/`, not into a monolithic `CLAUDE.md` body.

Primary documentation domains:
- `docs/architecture/`
- `docs/testing/`
- `docs/core-flow/`
- `docs/api/`

`CLAUDE.md` acts as a high-signal index/entrypoint and must reference these folders.
`README.md` must also expose this docs structure for contributors.

## Execution Modes

- `--mode incremental` (default if omitted): analyze latest approved change set via git diff and update docs incrementally.
- `--mode full`: scan the full codebase and rebuild/refresh docs comprehensively.

## Workflow

1. **Input & Scope**
   - Run after code changes are approved.
   - Incremental mode: analyze git diff + relevant PRD/plan context.
   - Full mode: analyze full repository code + existing docs baseline.

2. **Classify changes into doc domains**
   - Architecture rules/constraints -> `docs/architecture/`
   - Shared testing rules + execution guidance -> `docs/testing/`
   - Runtime/business workflow changes -> `docs/core-flow/`
   - Public/internal API contract changes -> `docs/api/`

3. **Write/Update docs in docs/ using domain templates**
   - Prefer updating existing files.
   - Create new files only when a topic has no suitable home.
   - Keep content durable and reusable (avoid one-off fix notes).
   - Use the matching template from:
     - `references/architecture-template.md`
     - `references/testing-template.md`
     - `references/core-flow-template.md`
     - `references/api-template.md`

4. **Mandatory index updates**
   - Update `CLAUDE.md` with references to documentation folders/files.
   - Update `README.md` with docs navigation references.

5. **Decision Gate**
   - Present proposed doc deltas for user approval before finalizing.

## Testing Documentation Rule (Mandatory)

Testing docs are shared/common guidance, not fix-specific notes.

Must include in `docs/testing/`:
- reusable testing rules/conventions
- how to run tests (unit/integration/e2e)
- required validation expectations for workflow changes

Do not add ad-hoc “this one bug fix test note” memory entries.

## Output Format

Provide a concise docs change package:
- Mode used: `incremental` or `full`
- Source scope analyzed (diff range or full repo)
- Target files to update/create
- Domain type per file (`architecture`/`testing`/`core-flow`/`api`)
- Why each file is updated
- Key additions/edits per file
- CLAUDE.md index changes
- README.md navigation changes

## Guardrails

- Do not dump all knowledge into `CLAUDE.md`.
- Keep `CLAUDE.md` concise and index-oriented.
- Prefer stable, long-term conventions over temporary implementation details.
- Keep docs language operational and actionable.
- In `full` mode, do not erase valid existing docs blindly; reconcile and refresh with explicit rationale.
