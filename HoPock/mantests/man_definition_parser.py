"""
manual test for config parser
"""

from definition_parser import DefinitionParser

parser = DefinitionParser() # 
entries = parser.parse_file("pocket.p8")

# for entry in entries:
#     print(f"[{entry.page_type} (", end='')
#     print(f"{entry.options}", end='')
#     print(")")
#     if len(entry.text) > 0:
#         print(f"    |{entry.text}")

for entry in entries:
    print(entry)