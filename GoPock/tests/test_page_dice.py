import unittest

from data_classes import Font
from page_dice import PageDice


class PageDiceDefaultsTests(unittest.TestCase):
    def test_page_dice_defaults_to_courier_size_8_for_body_font(self):
        page = PageDice()
        font = page.get_style("font")

        self.assertIsInstance(font, Font)
        self.assertEqual(font.name, "Courier")
        self.assertEqual(font.size, 8)

    def test_page_dice_keeps_title_font_unchanged(self):
        page = PageDice()
        title_font = page.get_style("fontTitle")

        self.assertIsNone(title_font)

    def test_page_dice_allows_font_override_from_page_config(self):
        page = PageDice()
        page.overrides["font.size"] = 11

        font = page.get_style("font")

        self.assertEqual(font.size, 11)


if __name__ == "__main__":
    unittest.main()
