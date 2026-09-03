"""
Base processor
Processor should use _read_file to get the text
Use their process() to convert to reportlab format
Reportlab styles should be passed
"""
from abc import ABC, abstractmethod
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

class Processor(ABC):

    @abstractmethod
    def process(self, text, rlstyles, **kwargs):
        pass

    # def _read_file(self, file_path):
    #     try:
    #         # Read the file and split into a list of strings
    #         string_array = file_path.read_text(encoding='utf-8').splitlines()
    #         logger.debug(f"Read raw text file {file_path} with {len(string_array)} lines")


    #     except FileNotFoundError:
    #         # print(f"Error: The file '{file_path}' does not exist.")
    #         logger.error (f"Error: The file '{file_path}' does not exist.")
    #         # Initialize an empty list or handle the fallback here
    #         string_array = []

    #     return string_array
