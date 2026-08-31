"""
Base text page
Pages based on text page need a processor for content handline
"""
from pages.base import Page
from pages.factory import PageFactory
from processors.plain import PlainTextProcessor
from models.page_details import TextPageDetail
from reportlab.platypus import Frame, Paragraph #Spacer PageBreak
from reportlab.lib.styles import ParagraphStyle

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

        # if self.detail.spacer: space_after = self.style.font.size
        # else: space_after = 0
        space_after = self.style.font.size if self.detail.spacer else 0
        if self.config.file:
            logger.debug(f"TextPage.__init__: file={self.config.file}")

        self.paragraph_style = ParagraphStyle(name="default", 
                    fontName=self.style.font.name, 
                    fontSize=self.style.font.size,
                    textColor=self.style.font.color,
                    spaceAfter=space_after,
                )

    def draw(self):
        text = self.processor.process(self.config.text)
        logger.debug(f"TextPage.render: text len={len(text) if isinstance(text, (list, str, tuple)) else 'n/a'}")
        frame = Frame(0, 0, self.max.x, self.max.y)
        for line in self.config.text:
            res = frame.add(Paragraph(line, self.paragraph_style), self.canvas)
        
