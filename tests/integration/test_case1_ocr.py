import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from converter.generator import convert_mineru_to_ppt


class TestCase1OCR(unittest.TestCase):
    def test_case1_png_json_runs_with_forced_ocr(self):
        repo_root = Path(__file__).resolve().parents[2]
        input_png = repo_root / "demo" / "case1" / "PixPin_2026-03-05_21-52-43.png"
        input_json = repo_root / "demo" / "case1" / "MinerU_PixPin_2026-03-05_21-52-43__20260305135318.json"

        self.assertTrue(input_png.exists(), f"Missing demo image: {input_png}")
        self.assertTrue(input_json.exists(), f"Missing demo json: {input_json}")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_ppt = Path(temp_dir) / "case1-ocr.pptx"
            logs = io.StringIO()

            with redirect_stdout(logs), redirect_stderr(logs):
                convert_mineru_to_ppt(
                    str(input_json),
                    str(input_png),
                    str(output_ppt),
                    remove_watermark=True,
                    debug_images=False,
                )

            log_text = logs.getvalue()
            self.assertTrue(output_ppt.exists(), "Output PPT was not generated")
            self.assertIn("[OCR] Page 1:", log_text)
            self.assertNotIn("fallback to MinerU-only", log_text)
            self.assertIn("candidates=", log_text)
            self.assertTrue("groups=" in log_text or "group_replaced=" in log_text)
            self.assertIn("added=", log_text)
            self.assertTrue("mineru_removed=" in log_text or "overlap_replaced=" in log_text)

            from PIL import Image
            import numpy as np
            from converter.ocr_merge import PaddleOCREngine

            page_image = np.array(Image.open(input_png).convert("RGB"))
            ocr_engine = PaddleOCREngine()
            ocr_elements = ocr_engine.extract_text_elements(
                page_image,
                page_image.shape[1],
                page_image.shape[0],
            )
            ocr_texts = [
                span.get("content", "")
                for elem in ocr_elements
                for line in elem.get("lines", [])
                for span in line.get("spans", [])
            ]
            self.assertIn("基于AI的声明式数据开发新范式", ocr_texts)

    def test_all_demo_cases_generate_ppt_outputs_for_manual_review(self):
        repo_root = Path(__file__).resolve().parents[2]
        demo_root = repo_root / "demo"
        output_root = repo_root / "tmp" / "regression_ppt_outputs"
        output_root.mkdir(parents=True, exist_ok=True)

        case_dirs = sorted(path for path in demo_root.glob("case*") if path.is_dir())
        self.assertGreater(len(case_dirs), 0, f"No demo case directories found in: {demo_root}")

        for case_dir in case_dirs:
            json_candidates = sorted(case_dir.glob("MinerU*.json")) or sorted(case_dir.glob("*.json"))
            self.assertGreater(len(json_candidates), 0, f"Missing MinerU json file in: {case_dir}")
            input_candidates = sorted(case_dir.glob("*.pdf"))
            if not input_candidates:
                input_candidates = sorted(
                    path
                    for path in case_dir.iterdir()
                    if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg"}
                )
            self.assertGreater(len(input_candidates), 0, f"Missing input file in: {case_dir}")

            input_file = input_candidates[0]
            json_file = json_candidates[0]
            output_ppt = output_root / f"{case_dir.name}.pptx"

            logs = io.StringIO()
            with redirect_stdout(logs), redirect_stderr(logs):
                convert_mineru_to_ppt(
                    str(json_file),
                    str(input_file),
                    str(output_ppt),
                    remove_watermark=True,
                    debug_images=False,
                )

            self.assertTrue(
                output_ppt.exists(),
                f"Output PPT was not generated for {case_dir.name}: {output_ppt}",
            )
            self.assertGreater(output_ppt.stat().st_size, 0, f"Generated empty PPT for {case_dir.name}: {output_ppt}")


if __name__ == "__main__":
    unittest.main()
