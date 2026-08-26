from pages.base import Page
from pages.factory import PageFactory
from models.page_details import DailyPageDetail

@PageFactory.register(
    "lines"
)
class LinesPage(Page):

    def render(self):
        # detail = self.config.detail
        print ("Render lines page")

