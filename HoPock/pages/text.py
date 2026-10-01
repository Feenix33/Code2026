"""
Base text page
Pages based on text page need a processor for content handline
"""
from pages.base import Page
from pages.factory import PageFactory
from processors.plain import SimpleTextProcessor
from processors.reportlab_style_gen import ReportLabStyleProvider
from models.page_details import TextPageDetail
from reportlab.platypus import Frame, Paragraph, Spacer #, PageBreak
from collections import deque
from pprint import pprint

import logging
logger = logging.getLogger(__name__)

@PageFactory.register(
    "text",
    detail_class=TextPageDetail,
    processor_class=SimpleTextProcessor
)

class TextPage(Page):

    def __init__(self, config, booklet_style, processor=None):
        super().__init__(config, booklet_style)
        self.processor = processor or SimpleTextProcessor()

        # handle the spacer page config in the styles rather than as an override
        # TODO: Do we need these lines?
        if self.style.body.space_after == 0 and self.detail.spacer:
            self.style.body.space_after = self.style.body.font.size
        if self.style.title.space_after == 0 and self.detail.spacer:
            self.style.title.space_after = self.style.title.font.size

        self.style_provider = ReportLabStyleProvider(self.style)

        # FIFO for processed lines to reportlab format
        self.processed_lines = None


    def draw(self, resume=False):
        frame = Frame(0, 0, self.max.x, self.max.y)
        added = False

        if not resume:
            if self.config.file: # override text if there is a file
                logger.debug(f"file={self.config.file}")
                # self.config.text = self.processor._read_file(self.config.file)
                self.config.text = self._read_file(self.config.file, self.detail.joinlines)
                # logger.debug(f"Read {len(self.config.text)} lines from file {self.config.file}")
                if self.config.titletext:
                    self.config.text.insert(0, self.config.titletext)
            else:
                logger.debug ("There is no file")
        
            #
            # process the text buffer into RL objects
            #

            # rlstyles:ReportLabStyles, space_after=None, first_line=False, blanks=False,
            self.processed_lines = self.processor.process(self.config.text, self.style_provider, #self.rl_styles,
                                                        space_after=self.detail.spacer, first_line=self.detail.firstline, blanks=self.detail.blanks,
                                                        title_style_name=self.detail.title_style, 
                                                        body_style_name=self.detail.body_style)

            # logger.debug(f"TextPage.draw: Processed {len(self.processed_lines)} lines into reportlab objects")
            # logger.debug(f"First line: {self.processed_lines[0] if len(self.processed_lines) > 0 else 'None'}")
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
        
