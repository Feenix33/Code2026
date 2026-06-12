from page import Page, PageFactory
# import pprint

@PageFactory.register("line")
@PageFactory.register("lines")
class PageLines(Page):
    def __init__(self, title="None", spacing=20, **kwargs):
        super().__init__()
        self.title = title
        self.spacing = spacing

    def draw(self, canvas):
        spacing = self.get_style("spacing")
        print(f"Dimensions: {Page.max.x}, {Page.max.y}")
        print(f"Spacing: {spacing}")
        # y - Page.max.y - spacing