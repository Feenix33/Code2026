"""
Base text page
Pages based on text page need a processor for content handline
"""
from pages.base import Page
from pages.factory import PageFactory
from processors.plain import PlainTextProcessor
from models.page_details import TextPageDetail
from models.reportlab_styles import ReportLabStyles
from reportlab.platypus import Frame, Paragraph #Spacer PageBreak
from reportlab.lib.styles import ParagraphStyle
from collections import deque
from pprint import pprint

import logging
logger = logging.getLogger(__name__)

@PageFactory.register(
    "text",
    detail_class=TextPageDetail,
    processor_class=PlainTextProcessor
)

class TextPage(Page):

    def __init__(self, config, booklet_style, processor=None):
        super().__init__(config, booklet_style)
        self.processor = processor or PlainTextProcessor()
        self.rl_styles = ReportLabStyles(self.style)
        # pprint (self.rl_styles.text)

        # if self.detail.spacer: space_after = self.style.font.size
        # else: space_after = 0
        space_after = self.style.font.size if self.detail.spacer else 0


        self.paragraph_style = self.rl_styles.body_style
        # ParagraphStyle(name="default", 
        #             fontName=self.style.font.name, 
        #             fontSize=self.style.font.size,
        #             textColor=self.style.font.color,
        #             spaceAfter=space_after,
        #         )

        # FIFO for processed lines to reportlab format
        self.processed_lines = None


    def draw(self, resume=False):
        if not resume:
            if self.config.file: # override text if there is a file
                logger.debug(f"file={self.config.file}")
                self.config.text = self.processor._read_file(self.config.file)
                logger.debug(f"Read {len(self.config.text)} lines from file {self.config.file}")
            else:
                logger.debug ("There is no file")
        
            self.processed_lines = self.processor.process(self.config.text)

        # logger.debug(f"TextPage.render: text len={len(text) if isinstance(text, (list, str, tuple)) else 'n/a'}")
        frame = Frame(0, 0, self.max.x, self.max.y)
        added = False
        while self.processed_lines:
            line = self.processed_lines.popleft()
            res = frame.add(Paragraph(line, self.paragraph_style), self.canvas)
            if not res:
                if added:
                    logger.warning(f"TextPage.draw: Frame full, unable to add line: {line[:20]}...")
                    # put the line back on the queue
                    self.processed_lines.appendleft(line)
                else:
                    logger.warning(f"TextPage.draw: Frame too small to add first line: {line[:20]}...")
                return False # not all processing complete
            added = True # successfully added at least one line to the frame
        return True # all processing complete
        
