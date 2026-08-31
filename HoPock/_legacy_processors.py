class AsciiProcessor:
    def process(self, file_path):
        with open(file_path, 'r') as f:
            text = f.read()
        return f"ASCII Text Layer:\n{text}"

class MarkdownProcessor:
    def process(self, file_path):
        with open(file_path, 'r') as f:
            text = f.read()
        # You can use a library like 'mistune' or 'markdown' here later
        return f"Rendered Markdown HTML/Text:\n{text}"

class ImageProcessor:
    def process(self, file_path):
        # Logic to return image path / bounding boxes
        return f"Image Object from {file_path}"

