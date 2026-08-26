
from pages.base import Page
from pages.factory import PageFactory
from models.page_details import DailyPageDetail


@PageFactory.register(
    "daily",
    detail_class=DailyPageDetail
)
class DailyPage(Page):

    def render(self):

        detail = self.config.detail

        print(f"Start:     {detail.start}")
        print(f"End:       {detail.end}")
        print(f"Increment: {detail.increment}")
