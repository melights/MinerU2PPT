# Testing Guide: OCR BBox Refinement (XY in Unified Flow)

## Scope
- Feature/workflow under test: OCR text bbox refinement where X refinement is added inside existing Y refinement flow.
- Test layers covered: unit / integration / e2e-smoke

## Shared Testing Rules
- Mandatory coverage expectations:
  - Y-direction refinement behavior remains valid (non-regression).
  - X-direction refinement is covered for both trim and extend behavior.
  - `line.bbox` and `span.bbox` are synchronized in both X and Y.
  - Debug fields (`ocr_bbox_original`, `ocr_bbox_pad`, `ocr_bbox_refined`) remain present.
- Test data/fixtures conventions:
  - Use deterministic synthetic images with clear text-like foreground/background contrast.
  - Include over-wide/over-tall and too-small bbox scenarios.
- Mock/adapter expectations:
  - Unit tests should target refine logic directly without requiring OCR model initialization.

## How to Run
- Unit:
  - `python -m pytest "tests/unit/test_ocr_bbox_refine.py"`
- Integration:
  - `python -m pytest "tests/integration/test_generator_ocr_merge.py"`
- E2E/Smoke:
  - `python main.py --json "demo/case1/MinerU_PixPin_2026-03-05_21-52-43__20260305135318.json" --input "demo/case1/PixPin_2026-03-05_21-52-43.png" --output "demo/case1/ocr-xy-refine-smoke-output.pptx"`

## Workflow Validation Requirements
- When workflow changes, required test updates:
  - Any change to row/column hit thresholds or trim/extend rules must update/refit unit assertions.
  - Any change to bbox writeback logic must assert element/line/span synchronization.
- Required evidence for sign-off:
  - Unit and integration test pass output.
  - Smoke output artifact generated successfully.

## Failure Handling
- Common failure patterns:
  - Synthetic fixture mismatch causes color extraction to invert expectations.
  - Too-tight bbox with no hit pixels leads to no refinement (expected in some cases).
  - Over-aggressive thresholds can over-expand/over-trim boundaries.
- Debug/triage checklist:
  1. Inspect `ocr_bbox_original`, `ocr_bbox_pad`, `ocr_bbox_refined`.
  2. Verify row/column hit signal presence for fixture ROI.
  3. Confirm fallback path triggers only on invalid refined bbox.

## References
- PRD/Plan refs:
  - `docs/interview/spec-ocr-bbox-xy-refine.md`
  - `docs/plan/ocr-bbox-xy-refine-plan.md`
- Related test files:
  - `tests/unit/test_ocr_bbox_refine.py`
  - `tests/integration/test_generator_ocr_merge.py`
