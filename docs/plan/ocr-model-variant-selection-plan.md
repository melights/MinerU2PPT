# Task Plan: OCR Model Variant Selection

## I100
**Subject:** Implement OCR model variant selection

**Description:**
PRD Section Refs: [PRD §1.1, PRD §2.1, PRD §3.1, PRD FR-001, PRD FR-002, PRD FR-005]
Runtime Task ActiveForm: Implementing OCR model variant selection
- Add model-variant selection (auto/lite/server) in PaddleOCREngine initialization flow.
- Default auto chooses server when GPU is available, lite when GPU is unavailable.
- Map lite to PP-OCRv5_lite_det/rec and server to PP-OCRv5_server_det/rec.
- Ensure model-root handling resolves the correct subdirectory based on variant.
- Add logging that includes chosen variant and whether it was auto-resolved.
- Add/adjust unit tests for variant selection and model-root resolution.

**Blocked By:** None

**Acceptance:**
- Variant selection is enforced in initialization and logged clearly.
- Unit tests cover auto/lite/server selection and missing model error behavior.

## Q200
**Subject:** Update CLI and GUI options for OCR model variant

**Description:**
PRD Section Refs: [PRD FR-003, PRD FR-004]
Runtime Task ActiveForm: Updating CLI and GUI options for OCR model variant
- Add CLI flag `--ocr-model-variant` with choices auto/lite/server.
- Add GUI control to select OCR model variant in single and batch modes.
- Ensure CLI/GUI pass the variant into convert_mineru_to_ppt and PaddleOCREngine.

**Blocked By:** I100

**Acceptance:**
- CLI accepts the new flag and passes it through to OCR initialization.
- GUI exposes variant selection and it takes effect for both single and batch conversions.

## T300
**Subject:** Add integration coverage for OCR model variant

**Description:**
PRD Section Refs: [PRD §5, PRD §6]
Runtime Task ActiveForm: Adding integration coverage for OCR model variant
- Extend integration tests to assert CLI argument propagation for ocr-model-variant.
- Add test coverage for auto variant when GPU unavailable (mocked) selecting lite.

**Blocked By:** Q200

**Acceptance:**
- Integration tests verify CLI propagation and auto-selection behavior.

## E400
**Subject:** Run functional smoke checks for GUI variant selection

**Description:**
PRD Section Refs: [PRD §6]
Runtime Task ActiveForm: Running functional smoke checks for GUI variant selection
- Run a manual/automated GUI smoke path to validate variant selection toggles (single and batch).
- Capture evidence via log output that chosen variant is used.

**Blocked By:** T300

**Acceptance:**
- Evidence shows GUI variant selection toggles affect OCR model choice.

## D500
**Subject:** Update documentation for OCR model variant

**Description:**
PRD Section Refs: [PRD §2.1, PRD FR-003]
Runtime Task ActiveForm: Updating documentation for OCR model variant
- Update README/README_zh with new CLI option and behavior.
- Document model-root layout expectations for lite/server variants.

**Blocked By:** E400

**Acceptance:**
- Docs reflect the new CLI flag and default behavior.

## C900
**Subject:** Final verification and sign-off

**Description:**
PRD Section Refs: [PRD §5, PRD §6]
Runtime Task ActiveForm: Finalizing verification and sign-off
- Ensure unit/integration tests pass or document any required skips.
- Confirm logs show model variant selection in CPU-only path.

**Blocked By:** D500

**Acceptance:**
- Verification notes confirm acceptance criteria coverage and passing tests.
