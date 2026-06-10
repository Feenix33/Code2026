from page import Page, PageFactory

@PageFactory.register("word")
class PageWord(Page):
    def __init__(self, title="Generic Word Page", **kwargs):
        super().__init__()
        self.title = title

    def draw(self, canvas):
        canvas.setFont("Helvetica", 12)
        canvas.drawCentredString(Page.mid.x, Page.mid.y, self.title)
