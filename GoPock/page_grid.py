from page import Page, PageFactory
from reportlab.lib.units import inch
# import pprint

@PageFactory.register("grid")
class PageGrid(Page):
    def __init__(self, title="None", spacing=0.25, **kwargs):
        super().__init__()
        self.title = title
        self.spacing = spacing

    def _calculate_spacing(self):
        """Calculate grid spacing based on gridX, gridY, or default spacing."""
        gridX = self.get_style('gridX')
        gridY = self.get_style('gridY')
        
        print (f"DEBUG: {self.debugID} gridX: {gridX}, gridY: {gridY}")
        # Both None: use default spacing
        if gridX is None and gridY is None:
            spacing = self.get_style('spacing') * inch
            return spacing, spacing
        
        # Only gridX: use it for both dimensions
        if gridX is not None and gridY is None:
            spacingX = Page.max.x / gridX
            return spacingX, spacingX

        # Only gridY: use it for both dimensions
        if gridY is not None and gridX is None:
            spacingY = Page.max.y / gridY
            return spacingY, spacingY
        
        # Both set: calculate independently
        spacingX = self.max.x / gridX
        spacingY = self.max.y / gridY
        return spacingX, spacingY

    def _draw_grid_lines(self, canvas, spacingX, spacingY, max=Page.max):
        """Draw vertical and horizontal grid lines."""
        # canvas.setStrokeColor(self.colorGrid)
        
        for x in range(0, int(max.x), int(spacingX)):
            canvas.line(x, 0, x, max.y)
        
        for y in range(int(max.y), 0, -int(spacingY)):
            canvas.line(0, y, max.x, y)


    def draw(self, canvas):
        spacing = self.get_style("spacing") * inch
        spacingX, spacingY = self._calculate_spacing()
        print(f"{self.debugID} spacingX: {spacingX}, spacingY: {spacingY}")
        #self._draw_grid_lines(canvas, spacingX, spacingY)
        colorLine = self.get_style("colorLine")

        # draw the lines
        canvas.setStrokeColor(colorLine)
        self._draw_grid_lines(canvas, spacingX, spacingY)

        # y = Page.max.y - spacing # start at top
        # while y > 0:
        #     canvas.line(0, y, Page.max.x, y)
        #     y -= spacing
        
        # x = 0
        # while x < Page.max.x:
        #     canvas.line(x, 0, x, Page.max.y)
        #     x += spacing