"""
manual test for config parser
"""

from config_parser import ConfigParser

parser = ConfigParser() # 
entries = parser.parse_file("pocket.p8")

for entry in entries:
    print(f"[{entry.page_type} (", end='')
    print(f"{entry.options}", end='')
    print(")")
    if len(entry.text) > 0:
        print(f"    |{entry.text}")