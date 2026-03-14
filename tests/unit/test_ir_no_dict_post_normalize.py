import unittest

from converter.ir import ImageIR, TextIR, normalize_element_ir, validate_ir_elements


class TestIRNoDictPostNormalize(unittest.TestCase):
    def test_normalize_returns_typed_ir(self):
        text = normalize_element_ir({"type": "text", "bbox": [0, 0, 10, 10], "text": "x", "source": "mineru"})
        image = normalize_element_ir({"type": "image", "bbox": [0, 0, 10, 10], "source": "mineru"})

        self.assertIsInstance(text, TextIR)
        self.assertIsInstance(image, ImageIR)

    def test_validate_ir_elements_returns_typed_elements(self):
        elements = validate_ir_elements(
            [
                {"type": "text", "bbox": [0, 0, 10, 10], "text": "a", "source": "mineru"},
                {"type": "image", "bbox": [0, 0, 10, 10], "source": "mineru"},
            ]
        )

        self.assertTrue(all(isinstance(elem, (TextIR, ImageIR)) for elem in elements))


if __name__ == "__main__":
    unittest.main()
