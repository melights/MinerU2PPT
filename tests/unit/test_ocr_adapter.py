import unittest

from converter.adapters.ocr_adapter import OCRAdapter
from converter.ir import TextIR


class _FakeEngine:
    def extract_text_elements(self, _page_image, _json_w, _json_h, return_stage_elements=False):
        elements = [
            {
                "type": "text",
                "bbox": [20, 30, 120, 60],
                "index": 3,
                "lines": [
                    {
                        "bbox": [20, 30, 120, 60],
                        "spans": [
                            {"bbox": [20, 30, 70, 60], "content": "Hello", "type": "text"},
                            {"bbox": [72, 30, 120, 60], "content": "World", "type": "text"},
                        ],
                    }
                ],
            }
        ]
        if return_stage_elements:
            return {
                "before_refined_elements": elements,
                "after_refined_elements": elements,
            }
        return elements


class TestOCRAdapter(unittest.TestCase):
    def test_maps_ocr_output_to_ir_text(self):
        adapter = OCRAdapter(_FakeEngine())
        elements = adapter.extract_page_elements(page_image=None, json_w=200, json_h=100)

        self.assertEqual(len(elements), 1)
        elem = elements[0]
        self.assertIsInstance(elem, TextIR)
        self.assertEqual(elem.type, "text")
        self.assertEqual(elem.source, "ocr")
        self.assertEqual(elem.text, "HelloWorld")
        self.assertGreater(elem.style["font_size"], 0)
        self.assertEqual(elem.style["align"], "left")
        self.assertIsInstance(elem.text_runs, list)
        self.assertEqual(len(elem.text_runs), 2)
        self.assertEqual(elem.text_runs[0].bbox, [20.0, 30.0, 70.0, 60.0])


if __name__ == "__main__":
    unittest.main()
