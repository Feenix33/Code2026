import os
import tempfile
import unittest

from utils import read_page_specs


class ShorthandParserTests(unittest.TestCase):
    def test_shorthand_processor_keeps_trailing_attributes_as_page_args(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
            handle.write("recipe ./tests/cChocoChip.txt {font.size=8}\n")
            temp_name = handle.name

        try:
            specs = read_page_specs(temp_name)
            self.assertEqual(len(specs), 1)
            self.assertEqual(specs[0].page_type, "text")
            self.assertEqual(specs[0].attrs["processor"], "recipe")
            self.assertEqual(specs[0].attrs["file"], "./tests/cChocoChip.txt")
            self.assertEqual(specs[0].attrs["font.size"], 8)
        finally:
            os.remove(temp_name)


if __name__ == "__main__":
    unittest.main()
