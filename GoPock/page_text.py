from page import Page, PageFactory
from reportlab.platypus import Frame, Paragraph

@PageFactory.register("text")
class TextPage(Page):
    def __init__(self, text="", title="Generic Text Page", **kwargs):
        super().__init__()
        self.text = text
        self.title = title

    def draw(self, canvas):
        mgn = 10
        frame = Frame(mgn, mgn, self.max.x - mgn, self.max.y - mgn, showBoundary=1)
        currentStyle = self.buildParagraphStyle()
        obj = Paragraph(self.text, currentStyle)
        frame.add(obj, canvas)
