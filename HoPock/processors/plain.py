"""
Plain text processor
"""
from processors.base import Processor
from collections import deque

class PlainTextProcessor(Processor):

    def process(self, text):
        # print (f"XXXX processing {len(text)} lines of text")
        queue = deque()
        for line in text:
            queue.append(line)  
        return queue