import os
import tempfile
import unittest
from unittest.mock import patch

from page_text import TextPage


class TextPagePathResolutionTests(unittest.TestCase):
    def test_resolves_relative_file_from_current_directory_by_default(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with patch("page_text.os.getcwd", return_value=tempdir):
                page = TextPage(file="notes.txt")
                self.assertEqual(page._resolve_full_path("notes.txt", None), os.path.join(tempdir, "notes.txt"))

    def test_resolves_dot_relative_subpath_from_current_directory(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with patch("page_text.os.getcwd", return_value=tempdir):
                page = TextPage(file="./alpha/file.txt")
                self.assertEqual(page._resolve_full_path("./alpha/file.txt", None), os.path.join(tempdir, "alpha", "file.txt"))


if __name__ == "__main__":
    unittest.main()
