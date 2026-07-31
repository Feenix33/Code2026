from page import Page, PageFactory
import PIL
# import pprint


@PageFactory.register("image")
class PageImage(Page):
    def __init__(self, title="Image Page", **kwargs):
        super().__init__()
        # Set defaults
        self.title = title

    def draw(self, canvas):
        wordFont = self.get_style("fontTitle")
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        titleFormat = self.get_style("titleFormat")
        # pageDate = self.get_style("date")
        image1 = self.get_style("file")
        image2 = self.get_style("file2")

        mgn = 10
        x = mgn
        y = mgn
        ww = self.max.x - (2*mgn)
        hh = self.max.y - (2 * mgn)
        if image1 is not None:
            if image2 is None:
                canvas.drawImage(image1, x, y, width=ww, height=hh) #, mask=None)
            else:
                hh = (hh - (2 * mgn)) / 2
                canvas.drawImage(image2, x, y, width=ww, height=hh)  # , mask=None)
                y += hh + 2*mgn
                canvas.drawImage(image1, x, y, width=ww, height=hh)  # , mask=None)
