import os
import unittest

from booklet import Booklet
from page import PageFactory
from utils import build_book, read_page_specs
import page_text
import page_lines
import page_grid
import page_checklist
import page_weekly
import page_daily
import page_title
import page_tracker
import page_montrack
import page_dice
import page_month
import page_monthref
import page_image


class InputDefaultsTests(unittest.TestCase):
    def test_input_defaults_font_size_is_applied_to_the_book(self):
        repo_root = os.path.dirname(os.path.dirname(__file__))
        input_path = os.path.join(repo_root, "input.txt")

        specs = read_page_specs(input_path)
        book = Booklet()
        build_book(book, specs, PageFactory)

        self.assertEqual(book.style.font.size, 8)


if __name__ == "__main__":
    unittest.main()
