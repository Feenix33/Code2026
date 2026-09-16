import mistune
from mistune.renderers.markdown import MarkdownRenderer


class QueueRenderer(MarkdownRenderer):
    """Custom renderer that intercepts Markdown blocks into a flat queue.
    
    Inheriting from MarkdownRenderer automatically processes nested inline styles 
    (bold, italics, code) into formatted strings.
    """

    def __init__(self):
        super().__init__()
        self.queue = []

    # --- BLOCK HANDLERS ---
    def heading(self, token: dict, state: mistune.BlockState) -> str:
        text = self.render_children(token, state)
        level = token['attrs']['level']
        self.queue.append((f"h{level}", text))
        return ""

    def paragraph(self, token: dict, state: mistune.BlockState) -> str:
        text = self.render_children(token, state)
        self.queue.append(("paragraph", text))
        return ""

    def list(self, token: dict, state: mistune.BlockState) -> str:
        ordered = token['attrs'].get('ordered', False)
        style = "numbered_list" if ordered else "bullet_list"
        
        # Iterate over individual list items in children
        for item_token in token.get('children', []):
            item_text = self.render_children(item_token, state).strip()
            if item_text:
                self.queue.append((style, item_text))
        return ""

    def block_quote(self, token: dict, state: mistune.BlockState) -> str:
        text = self.render_children(token, state)
        self.queue.append(("blockquote", text.strip()))
        return ""

    def block_code(self, token: dict, state: mistune.BlockState) -> str:
        code = token.get('raw', '')
        self.queue.append(("code_block", code.strip()))
        return ""

    # --- CATCH-ALL FOR UNHANDLED TYPES ---
    def __getattr__(self, name: str):
        """Silently catch and skip any unhandled markdown tokens (e.g. tables, thematic breaks)."""
        def skip_handler(token: dict, state: mistune.BlockState):
            return ""
        return skip_handler


def parse_markdown_to_queue(md_text: str) -> list[tuple[str, str]]:
    renderer = QueueRenderer()
    markdown = mistune.create_markdown(renderer=renderer, plugins=['table'])
    markdown(md_text)
    return renderer.queue


# --- Test ---
md_input = """
# Chapter 1

This is a **paragraph** with *italics* and ***bold italics***.

## Lists Section

- Bullet item 1 with **bold**
- Bullet item 2

1. Numbered step 1
2. Numbered step 2 with *italics*

> A blockquote with **bold** text.

| Unhandled | Table |
| --------- | ----- |
| Skipped   | Cell  |
"""

parsed_queue = parse_markdown_to_queue(md_input)

for style, text in parsed_queue:
    print(f"{style:<15} -> {text}")