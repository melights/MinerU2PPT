import unittest
from unittest import mock

import main


class TestCliOCROption(unittest.TestCase):
    def test_cli_forwards_core_flags_and_default_ocr_options(self):
        argv = [
            "main.py",
            "--json",
            "a.json",
            "--input",
            "a.pdf",
            "--output",
            "a.pptx",
            "--debug-images",
            "--no-watermark",
        ]

        with mock.patch("sys.argv", argv), mock.patch("main.convert_mineru_to_ppt") as mocked_convert:
            main.main()

        self.assertEqual(mocked_convert.call_count, 1)
        kwargs = mocked_convert.call_args.kwargs
        self.assertTrue(kwargs["debug_images"])
        self.assertTrue(kwargs["remove_watermark"])
        self.assertEqual(kwargs["ocr_device_policy"], "auto")
        self.assertIsNone(kwargs["ocr_model_root"])
        self.assertTrue(kwargs["ocr_offline_only"])
        self.assertEqual(kwargs["ocr_det_db_thresh"], 0.35)
        self.assertEqual(kwargs["ocr_det_db_box_thresh"], 0.8)
        self.assertEqual(kwargs["ocr_det_db_unclip_ratio"], 1.0)
        self.assertIsNone(kwargs["page_range"])

    def test_cli_forwards_explicit_ocr_options(self):
        argv = [
            "main.py",
            "--json",
            "a.json",
            "--input",
            "a.pdf",
            "--output",
            "a.pptx",
            "--ocr-device",
            "gpu",
            "--ocr-model-root",
            "models/paddleocr",
        ]

        with mock.patch("sys.argv", argv), mock.patch("main.convert_mineru_to_ppt") as mocked_convert:
            main.main()

        kwargs = mocked_convert.call_args.kwargs
        self.assertEqual(kwargs["ocr_device_policy"], "gpu")
        self.assertEqual(kwargs["ocr_model_root"], "models/paddleocr")
        self.assertTrue(kwargs["ocr_offline_only"])
        self.assertEqual(kwargs["ocr_det_db_thresh"], 0.35)
        self.assertEqual(kwargs["ocr_det_db_box_thresh"], 0.8)
        self.assertEqual(kwargs["ocr_det_db_unclip_ratio"], 1.0)
        self.assertIsNone(kwargs["page_range"])

    def test_cli_forwards_tuned_ocr_detection_options(self):
        argv = [
            "main.py",
            "--json",
            "a.json",
            "--input",
            "a.pdf",
            "--output",
            "a.pptx",
            "--ocr-det-db-thresh",
            "0.35",
            "--ocr-det-db-box-thresh",
            "0.8",
            "--ocr-det-db-unclip-ratio",
            "1.1",
        ]

        with mock.patch("sys.argv", argv), mock.patch("main.convert_mineru_to_ppt") as mocked_convert:
            main.main()

        kwargs = mocked_convert.call_args.kwargs
        self.assertEqual(kwargs["ocr_det_db_thresh"], 0.35)
        self.assertEqual(kwargs["ocr_det_db_box_thresh"], 0.8)
        self.assertEqual(kwargs["ocr_det_db_unclip_ratio"], 1.1)

    def test_cli_forwards_page_range(self):
        argv = [
            "main.py",
            "--json",
            "a.json",
            "--input",
            "a.pdf",
            "--output",
            "a.pptx",
            "--page-range",
            "1,3,5-8",
        ]

        with mock.patch("sys.argv", argv), mock.patch("main.convert_mineru_to_ppt") as mocked_convert:
            main.main()

        kwargs = mocked_convert.call_args.kwargs
        self.assertEqual(kwargs["page_range"], "1,3,5-8")

    def test_cli_rejects_removed_ocr_flag(self):
        argv = [
            "main.py",
            "--json",
            "a.json",
            "--input",
            "a.pdf",
            "--output",
            "a.pptx",
            "--ocr-merge",
        ]

        with mock.patch("sys.argv", argv), self.assertRaises(SystemExit):
            main.main()


if __name__ == "__main__":
    unittest.main()
