---
name: code-interview
description: Iteratively clarifies fragmented ideas into requirements through multi-round discussion; after explicit user OK, generates a decision-first concise execution-ready PRD (without redundant traceability matrix by default), then auto-invokes code-plan.
argument-hint: [optional topic or one-line idea]
user-invocable: true
---

# Iterative Requirement Interview (Decision-First, Concise PRD Mode)

## Objective
Use an iterative conversation to clarify requirements.

Do not enter structured PRD mode before the user explicitly says "OK" (or equivalent).
After user OK, generate a decision-first concise PRD; once PRD is approved and saved, immediately invoke `code-plan` without asking again.

## Workflow

### 1) Treat initial input as fragments by default
- Accept incomplete notes and rough thoughts.
- Do not require full requirements upfront.
- First restate current understanding in clear language.

### 2) Iterative clarification loop (core)
Before user explicitly says OK, keep running this loop:

1. Restate current understanding concisely:
   - goal/problem
   - expected process flow
   - key capabilities
   - current boundaries
   - unresolved points
2. Provide 2–4 options for ambiguous decisions with trade-offs.
3. Add evidence when needed:
   - search codebase (`Glob`/`Grep`/`Read`) for constraints and reusable capabilities;
   - use web search for external facts.
4. Rewrite latest discussion into clearer requirement wording.
5. Maintain a running decision ledger in conversation:
   - confirmed decisions
   - open questions
6. Invite correction.

## Important constraints (clarification phase)
- Do not demand "complete requirements" early.
- Do not force a fixed number of questions.
- Do not output structured PRD during clarification.
- Only transition on explicit user OK.

### 3) Transition signal
Move forward only when user clearly indicates:
- "OK", "good to formalize", "requirements are clear enough", or equivalent.

### 4) Generate PRD draft (decision-first, concise) and request confirmation
After OK, generate a **concise execution-ready PRD draft** from confirmed context.

Mandatory drafting rules:
- Put **Decision Summary** at the beginning of the PRD body.
- Keep only implementation-driving content; remove repetitive narrative.
- Do not duplicate the same decision across multiple sections.
- Requirements and acceptance criteria must be testable.
- Keep unresolved items explicit in `Open Questions`.
- Use stable section numbering so downstream `code-plan` can reference sections.
- **Do not include `Discussion-to-PRD Traceability Matrix` by default.**
- Include traceability matrix only when the user explicitly asks for it.

Process rules:
- Present PRD draft first.
- Explicitly request user confirmation.
- If user asks for changes, revise and re-present until explicitly approved.

### 5) Save only after PRD approval
Only after explicit PRD approval, save to:
- `docs/interview/spec-[feature-name].md`

Use kebab-case for `[feature-name]`.

### 6) Auto-transition to code-plan (mandatory)
Immediately after approved PRD is saved, invoke:
- `code-plan docs/interview/spec-[feature-name].md`

Do not ask user whether to generate code-plan.

## PRD Template (use only after explicit OK)

```markdown
# Product Requirements Document: [Feature Name]

## 0. Document Control
- Version: v0.x
- Status: Draft / Approved
- Source: requirements interview conversation
- Last Updated: YYYY-MM-DD

## 1. Decision Summary

### 1.1 Confirmed Decisions
- D1: ...
- D2: ...

### 1.2 Out of Scope / Non-Goals
- ...

## 2. Scope & Boundaries

### 2.1 In Scope
- ...

### 2.2 Constraints & Dependencies
- ...

## 3. Final-State Process Flow

### 3.1 End-to-End Happy Path
1. [Actor/System] ...
2. [Actor/System] ...

### 3.2 Key Exception Flows
- EX-1: trigger -> handling -> expected outcome
- EX-2: ...

## 4. Functional Requirements
Use stable IDs (`FR-001`, `FR-002`, ...). Keep each FR concise.

### FR-001 [Requirement title]
- Description:
- Trigger/Input:
- Processing rules:
- Output/Result:
- Error/Failure behavior:
- Priority: Must/Should/Could

## 5. Acceptance Criteria (Release Gate)
- AG-001: ... (maps to FR IDs)
- AG-002: ...

## 6. Verification Plan
- Unit tests required:
- Integration tests required:
- Functional/smoke tests required:
- Evidence needed for sign-off:

## 7. Open Questions
- Q1 ...
- Q2 ...

<!-- Optional appendix: add traceability matrix only if user explicitly requests it -->
```

## PRD Quality Checklist (must pass before final approval request)
- [ ] Decision summary appears first and is explicit.
- [ ] No section-level duplication of the same decisions.
- [ ] Final-state flow is explicit and actionable.
- [ ] FRs are testable and uniquely identified.
- [ ] Acceptance criteria are verifiable and map to FRs.
- [ ] Open questions are isolated and clearly marked.
- [ ] Content is concise but sufficient for direct `code-plan` execution.
- [ ] Traceability matrix is absent unless user explicitly requested it.