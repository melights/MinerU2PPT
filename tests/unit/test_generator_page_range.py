import unittest

from converter.generator import _parse_pdf_page_range


class TestGeneratorPageRange(unittest.TestCase):
    def test_parse_single_page(self):
        self.assertEqual(_parse_pdf_page_range("1", 10), [0])

    def test_parse_mixed_expression(self):
        self.assertEqual(_parse_pdf_page_range("1,3,5-8", 10), [0, 2, 4, 5, 6, 7])

    def test_parse_deduplicates_and_sorts(self):
        self.assertEqual(_parse_pdf_page_range("3,1,2,2,1-2", 10), [0, 1, 2])

    def test_parse_accepts_spaces(self):
        self.assertEqual(_parse_pdf_page_range(" 1 , 3 , 5 - 6 ", 10), [0, 2, 4, 5])

    def test_parse_rejects_invalid_token(self):
        with self.assertRaises(ValueError):
            _parse_pdf_page_range("1--3", 10)

    def test_parse_rejects_reverse_range(self):
        with self.assertRaises(ValueError):
            _parse_pdf_page_range("8-5", 10)

    def test_parse_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            _parse_pdf_page_range("11", 10)

    def test_parse_rejects_empty_expression(self):
        with self.assertRaises(ValueError):
            _parse_pdf_page_range("", 10)


if __name__ == "__main__":
    unittest.main()
