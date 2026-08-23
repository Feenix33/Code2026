from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 1. Create the canvas
my_canvas = canvas.Canvas("output.pdf", pagesize=letter)

# 2. Begin a text object at x=100, y=700 points
text_object = my_canvas.beginText(100, 700)

# 3. Set font name and size
text_object.setFont("Helvetica", 14)

# 4. Add text lines
text_object.textLine("This is the first line using drawText.")
text_object.textLine("This is the second line automatically spaced below.")
longLine = "This is a very long line. "*10
text_object.textLine(longLine)

# 5. Draw the text object onto the canvas
my_canvas.drawText(text_object)

# 6. Save the PDF page
my_canvas.showPage()
my_canvas.save()

