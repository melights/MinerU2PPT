# Task Blueprint: OCR variant-specific default tuning

**Input Source:** Conversation request (2026-03-15) — “lite 的默认参数更严格，区分两种默认参数”
**Plan Type:** Feature

## Required Task Chain

`I100 -> Q200 -> T300 -> E400 -> D500 -> C900`

## Tasks

### I100
- **Subject:** Implement variant-specific OCR defaults + unit tests
- **Description:**
  - PRD Section Refs: [Conversation 2026-03-15 §1]
  - Runtime Task ActiveForm: Implementing variant-specific OCR defaults
  - Add per-variant default mappings in `converter/ocr_merge.py` for DB thresholds and font-distance threshold.
  - Ensure defaults are applied based on resolved model variant (server vs lite) only when user parameters are `None`.
  - Pass effective DB params into PaddleOCR constructor attempts without mutating user-provided overrides.
  - Apply effective font-distance threshold for OCR bbox refinement per resolved variant.
  - Update `main.py` defaults to allow engine-side defaults (set CLI defaults to `None`).
  - Update `gui.py` to avoid hard-coding DB params and allow font-distance threshold to default per variant (empty/None).
  - Add/adjust unit test to assert lite/server default params are selected when not overridden.
- **Blocked By:** []
- **Acceptance:**
  - Variant defaults are applied per resolved model variant when user values are not provided.
  - Explicit CLI/GUI overrides still take precedence.
  - Unit tests for default selection pass.

### Q200
- **Subject:** Run syntax/static checks
- **Description:**
  - PRD Section Refs: [Conversation 2026-03-15 §1]
  - Runtime Task ActiveForm: Running syntax/static checks
  - Run Python syntax/static checks if configured; otherwise mark N/A with reason.
- **Blocked By:** [I100]
- **Acceptance:**
  - Checks pass or N/A is explicitly documented.

### T300
- **Subject:** Run integration tests
- **Description:**
  - PRD Section Refs: [Conversation 2026-03-15 §1]
  - Runtime Task ActiveForm: Running integration tests
  - Run integration coverage for CLI defaults and generator forwarding (e.g., `tests/integration/test_cli_ocr_option.py`, `tests/integration/test_generator_ocr_merge.py`).
- **Blocked By:** [Q200]
- **Acceptance:**
  - Integration tests pass for updated default behavior.

### E400
- **Subject:** Run e2e/smoke tests
- **Description:**
  - PRD Section Refs: [Conversation 2026-03-15 §1]
  - Runtime Task ActiveForm: Validating e2e/smoke coverage
  - Mark N/A if no e2e/smoke suite exists for this project.
- **Blocked By:** [T300]
- **Acceptance:**
  - E2E/smoke is N/A with justification or passes if run.

### D500
- **Subject:** Update documentation
- **Description:**
  - PRD Section Refs: [Conversation 2026-03-15 §1]
  - Runtime Task ActiveForm: Updating documentation
  - Update README/GUI help text only if default behavior is documented (otherwise mark N/A).
- **Blocked By:** [E400]
- **Acceptance:**
  - Docs updated if needed, or N/A recorded.

### C900
- **Subject:** Commit validated changes
- **Description:**
  - PRD Section Refs: [Conversation 2026-03-15 §1]
  - Runtime Task ActiveForm: Committing validated changes
  - Commit only if explicitly requested by the user.
- **Blocked By:** [D500]
- **Acceptance:**
  - Commit created only when requested and includes intended files.
