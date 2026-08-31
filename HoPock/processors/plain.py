"""
Plain text processor
"""
from processors.base import Processor


class PlainTextProcessor(Processor):

    def process(self, text):
        # process text
        return text