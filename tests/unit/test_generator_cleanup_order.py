import unittest

import numpy as np

from converter.generator import PPTGenerator
from converter.ir import ImageIR, TextIR


class _Context:
    def __init__(self):
        self.coords = {
            "img_h": 100,
            "json_h": 100,
            "img_w": 100,
            "json_w": 100,
            "scale_x": 1.0,
            "scale_y": 1.0,
        }
        self.original_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.cleanup_calls = []

    def add_element_bbox_for_cleanup(self, bbox, margin_px=0):
        self.cleanup_calls.append((bbox, margin_px))


class TestGeneratorCleanupOrder(unittest.TestCase):
    def test_cleanup_order_is_text_then_image(self):
        generator = PPTGenerator("out.pptx")
        context = _Context()
        context.original_image.fill(255)

        text_elem = TextIR(
            type="text",
            bbox=[10, 10, 20, 20],
            text="a",
            source="mineru",
            order=[10, 10],
            style={"bold": False, "font_size": None, "align": "left"},
            lines=None,
        )

        image_elem = ImageIR(
            type="image",
            bbox=[0, 0, 40, 40],
            source="mineru",
            order=[0, 0],
            style={"bold": False, "font_size": None, "align": "left"},
            crop_pixels=np.zeros((40, 40, 3), dtype=np.uint8),
        )

        cleaned_images = generator._cleanup_text_and_images(context, [text_elem], [image_elem])
        self.assertEqual(len(cleaned_images), 1)

        # text -> background cleanup should happen first
        self.assertEqual(len(context.cleanup_calls), 1)
        self.assertEqual(context.cleanup_calls[0][0], text_elem.bbox)
        self.assertGreater(context.cleanup_calls[0][1], 0)

        # text -> image cleanup should produce a new image IR instance
        self.assertIsNot(cleaned_images[0], image_elem)
        self.assertEqual(cleaned_images[0].bbox, image_elem.bbox)


if __name__ == "__main__":
    unittest.main()
