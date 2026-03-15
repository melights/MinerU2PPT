# Backend Task Patterns (Node.js, Minimal)

> Use task-only format. Do not add standalone requirement/phase narrative sections.

## Required Task Chain

`I100 -> Q200 -> T300 -> E400 -> D500 -> C900`

## Task Format (Mandatory)

Each task must contain only these fields:
- Subject
- Description
- Blocked By
- Acceptance

Description must include:
- `PRD Section Refs: [PRD §x.y, ...]`
- Executable notes for this task

---

## Task Specifications

### I100
- Subject: Implement feature + unit tests
- Description:
  - PRD Section Refs: [PRD §2.1, §4.2]
  - Implement scoped code changes
  - Include/adjust unit tests for changed logic
- Blocked By: []
- Acceptance:
  - Scoped implementation is complete
  - Unit tests for changed logic pass

### Q200
- Subject: Run syntax/static checks
- Description:
  - PRD Section Refs: [PRD §6.1]
  - Run lint and type/syntax checks for changed modules
- Blocked By: [I100]
- Acceptance:
  - Lint and type/syntax checks pass

### T300
- Subject: Run integration tests
- Description:
  - PRD Section Refs: [PRD §6.2]
  - Validate cross-module behavior for changed flow
  - Cover success and error paths
- Blocked By: [Q200]
- Acceptance:
  - Integration scenarios pass for scoped flow

### E400
- Subject: Run e2e/smoke tests
- Description:
  - PRD Section Refs: [PRD §6.3]
  - Validate end-to-end user/system flow
  - If not required, mark explicit N/A with reason
- Blocked By: [T300]
- Acceptance:
  - E2E/smoke passes, or N/A is justified

### D500
- Subject: Update documentation
- Description:
  - PRD Section Refs: [PRD §7.1]
  - Update impacted docs (API/architecture/ops as needed)
- Blocked By: [E400]
- Acceptance:
  - Docs match implemented behavior and test scope

### C900
- Subject: Commit validated changes
- Description:
  - PRD Section Refs: [PRD §8.1]
  - Commit only after upstream tasks are complete
- Blocked By: [D500]
- Acceptance:
  - I100/Q200/T300/E400/D500 are complete
  - Commit contains intended files only

---

## Refactor/Migration Extra Tasks (only when needed)

### M600
- Subject: Cutover to single active path
- Description:
  - PRD Section Refs: [PRD §5.1]
  - Ensure scoped flows use only new path
- Blocked By: [E400]
- Acceptance: New path is the only active implementation in scope

### M700
- Subject: Retire legacy implementation
- Description:
  - PRD Section Refs: [PRD §5.2]
  - Remove/retire legacy modules and routes
- Blocked By: [M600]
- Acceptance: Legacy implementation is removed or hard-retired

### M800
- Subject: Prove no residual legacy references
- Description:
  - PRD Section Refs: [PRD §5.3]
  - Verify no remaining callers/imports/references
- Blocked By: [M700]
- Acceptance: Residual checks show zero legacy references

For refactor/migration, set commit `Blocked By` to include `M800`.