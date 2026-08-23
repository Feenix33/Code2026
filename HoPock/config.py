import os

def parse_p8_file(file_path):
    """
    Reads a .p8 file. Example line format: 
    markdown:chapter1.md
    ascii:notes.txt
    image:photo.jpg
    internal:current_month
    """
    pages = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): # skip empty lines or comments
                continue
                
            if ":" in line:
                processor, target = line.split(":", 1)
                pages.append({"processor": processor.strip(), "target": target.strip()})
            else:
                # Default to ascii if no processor is specified
                pages.append({"processor": "ascii", "target": line})
    return pages

