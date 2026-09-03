"""
Markdown page
Similar to text page but uses the markdown processor
"""
from pages.base import Page
from pages.factory import PageFactory
from processors.markdown import MarkdownProcessor
from processors.reportlab_style_gen import ReportLabStyleProvider
from models.page_details import MarkdownPageDetail
from reportlab.platypus import Frame, Paragraph, Spacer #, PageBreak
from collections import deque
from pprint import pprint

import logging
logger = logging.getLogger(__name__)

@PageFactory.register(
    "markdown",
    detail_class=MarkdownPageDetail,
    processor_class=MarkdownProcessor
)

class MarkdownPage(Page):

    def __init__(self, config, booklet_style, processor=None):
        super().__init__(config, booklet_style)
        self.processor = processor or MarkdownProcessor()
        self.style_provider = ReportLabStyleProvider(self.style)
        # FIFO for processed lines to reportlab format
        self.processed_lines = None


    def draw(self, resume=False):
        frame = Frame(0, 0, self.max.x, self.max.y)
        added = False

        if not resume:
            if self.config.file: # override text if there is a file
                # logger.debug(f"file={self.config.file}")
                self.config.text = self._read_file(self.config.file)
            #     logger.debug(f"Read {len(self.config.text)} lines from file {self.config.file}")
            # else:
            #     logger.debug ("There is no file")
        
            # process the text buffer into RL objects
            self.processed_lines = self.processor.process(self.config.text, self.style_provider,
                                                          titletext=self.config.titletext)

        # entry point to add to frame, start here on resume
        while self.processed_lines:
            item = self.processed_lines.popleft()
            # logger.debug(f"Adding item to frame: {item}")
            res = frame.add(item, self.canvas)
            if not res:
                if added:
                    logger.warning(f"TextPage.draw: Frame full, unable to add object.")
                    # put the line back on the queue
                    self.processed_lines.appendleft(item)
                else:
                    logger.warning(f"TextPage.draw: Frame too small to add first line")
                return False # not all processing complete
            added = True # successfully added at least one line to the frame
        return True # all processing complete
        
