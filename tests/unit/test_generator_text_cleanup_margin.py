import unittest

import numpy as np

from converter.generator import PPTGenerator
from converter.ir import TextIR


class TestGeneratorTextCleanupMargin(unittest.TestCase):
    def test_cleanup_margin_uses_single_line_height_when_lines_present(self):
        generator = PPTGenerator("out.pptx")
        context = type("Ctx", (), {})()
        context.coords = {"img_h": 2000, "json_h": 1000}

        elem = TextIR(
            type="text",
            bbox=[0, 0, 100, 200],
            text="a\nb",
            source="mineru",
            order=[0, 0],
            style={"bold": False, "font_size": None, "align": "left"},
            lines=[
                {"bbox": [0, 0, 100, 20], "spans": [{"content": "a", "bbox": [0, 0, 100, 20], "type": "text"}]},
                {"bbox": [0, 30, 100, 50], "spans": [{"content": "b", "bbox": [0, 30, 100, 50], "type": "text"}]},
            ],
        )

        margin_px = generator._compute_text_cleanup_margin_px(context, elem)
        # single line json height=20, scale=2 => 40px, 5% => 2px
        self.assertEqual(margin_px, 2)

    def test_cleanup_margin_falls_back_to_element_bbox_height(self):
        generator = PPTGenerator("out.pptx")
        context = type("Ctx", (), {})()
        context.coords = {"img_h": 1000, "json_h": 1000}

        elem = TextIR(
            type="text",
            bbox=[0, 0, 100, 40],
            text="a",
            source="mineru",
            order=[0, 0],
            style={"bold": False, "font_size": None, "align": "left"},
            lines=None,
        )

        margin_px = generator._compute_text_cleanup_margin_px(context, elem)
        # 40 * 5% = 2
        self.assertEqual(margin_px, 2)

    def test_cleanup_stage_registers_margin_px_not_ratio(self):
        generator = PPTGenerator("out.pptx")

        calls = []

        class _Context:
            def __init__(self):
                self.coords = {"img_h": 1000, "json_h": 1000, "scale_y": 1.0, "img_w": 1000, "json_w": 1000}
                self.original_image = np.zeros((100, 100, 3), dtype=np.uint8)

            def add_element_bbox_for_cleanup(self, bbox, margin_px=0):
                calls.append({
                    "bbox": bbox,
                    "margin_px": margin_px,
                })

        text_elem = TextIR(
            type="text",
            bbox=[0, 0, 100, 40],
            text="a",
            source="mineru",
            order=[0, 0],
            style={"bold": False, "font_size": None, "align": "left"},
            lines=[
                {"bbox": [0, 0, 100, 20], "spans": [{"content": "a", "bbox": [0, 0, 100, 20], "type": "text"}]}
            ],
        )

        cleaned_images = generator._cleanup_text_and_images(_Context(), [text_elem], [])

        self.assertEqual(cleaned_images, [])
        self.assertEqual(len(calls), 1)
        self.assertGreater(calls[0]["margin_px"], 0)


if __name__ == "__main__":
    unittest.main()
