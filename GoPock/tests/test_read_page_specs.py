import os
import tempfile
import unittest

from utils import read_page_specs


class ReadPageSpecsTests(unittest.TestCase):
    def test_processor_attribute_with_filename_becomes_text_page(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
            handle.write("processor=recipe path=local cChocoChip.txt\n")
            temp_name = handle.name

        try:
            specs = read_page_specs(temp_name)
            self.assertEqual(len(specs), 1)
            self.assertEqual(specs[0].page_type, "text")
            self.assertEqual(specs[0].attrs["processor"], "recipe")
            self.assertEqual(specs[0].attrs["path"], "local")
            self.assertEqual(specs[0].attrs["file"], "cChocoChip.txt")
        finally:
            os.remove(temp_name)

    def test_bare_recipe_keyword_becomes_text_page(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
            handle.write("recipe cLemon.txt\n")
            temp_name = handle.name

        try:
            specs = read_page_specs(temp_name)
            self.assertEqual(len(specs), 1)
            self.assertEqual(specs[0].page_type, "text")
            self.assertEqual(specs[0].attrs["processor"], "recipe")
            self.assertEqual(specs[0].attrs["file"], "cLemon.txt")
        finally:
            os.remove(temp_name)


if __name__ == "__main__":
    unittest.main()
