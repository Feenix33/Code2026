
from pages.base import Page
from pages.factory import PageFactory
from models.page_details import DailyPageDetail

import logging
logger = logging.getLogger(__name__)

@PageFactory.register(
    "daily",
    detail_class=DailyPageDetail
)
class DailyPage(Page):
    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)
        # logger.debug ("Daily created")
        # logger.debug ("Effective Style")
        # logger.debug (self.style)
        # logger.debug ("Detail")
        # logger.debug (self.config.detail)

    def render(self):

        detail = self.config.detail
        logger.debug ("Rendering a daily")

        # print(f"Start:     {detail.start}")
        # print(f"End:       {detail.end}")
        # print(f"Increment: {detail.increment}")
