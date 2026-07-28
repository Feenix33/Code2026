import unittest

from page_daily import DailyPage


class DailyPageFlipTests(unittest.TestCase):
    def test_flip_uses_constructor_argument_and_swaps_title_format(self):
        page = DailyPage(titleFormat=r"%b %w\t%m", flip=1)

        self.assertTrue(page.flip)
        self.assertEqual(page.titleFormat, "%m\t%b %w")

    def test_flip_title_format_handles_escaped_tabs(self):
        page = DailyPage()

        self.assertEqual(page.flip_title_format(r"%d%b\t\t%a"), "%a\t\t%d%b")


if __name__ == "__main__":
    unittest.main()
