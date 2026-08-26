from pages.base import Page
from pages.factory import PageFactory
from models.page_details import CalendarPageDetail

@PageFactory.register("calendar", detail_class=CalendarPageDetail)
class CalendarPage(Page):
    def render(self):

        detail = self.config.detail

        print(f"Calendar page")
