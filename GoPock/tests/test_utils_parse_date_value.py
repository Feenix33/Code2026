import datetime
import unittest
from unittest.mock import patch

from utils import parse_date_value


class ParseDateValueTests(unittest.TestCase):
    def test_accepts_month_number_string(self):
        with patch("utils._today_date", return_value=datetime.date(2026, 7, 15)):
            self.assertEqual(parse_date_value("3"), datetime.date(2026, 3, 1))

    def test_accepts_month_number_integer(self):
        with patch("utils._today_date", return_value=datetime.date(2026, 7, 15)):
            self.assertEqual(parse_date_value(7), datetime.date(2026, 7, 1))

    def test_accepts_three_letter_month_name_case_insensitively(self):
        with patch("utils._today_date", return_value=datetime.date(2026, 7, 15)):
            self.assertEqual(parse_date_value("Jan"), datetime.date(2026, 1, 1))
            self.assertEqual(parse_date_value("jAn"), datetime.date(2026, 1, 1))

    def test_accepts_zero_for_current_month(self):
        with patch("utils._today_date", return_value=datetime.date(2026, 7, 15)):
            self.assertEqual(parse_date_value("0"), datetime.date(2026, 7, 1))

    def test_accepts_positive_offset_across_year_boundary(self):
        with patch("utils._today_date", return_value=datetime.date(2026, 12, 10)):
            self.assertEqual(parse_date_value("+1"), datetime.date(2027, 1, 1))

    def test_accepts_negative_offset_across_year_boundary(self):
        with patch("utils._today_date", return_value=datetime.date(2026, 1, 10)):
            self.assertEqual(parse_date_value("-1"), datetime.date(2025, 12, 1))


if __name__ == "__main__":
    unittest.main()
