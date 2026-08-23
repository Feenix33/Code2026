from config_parser import ConfigParser, ConfigEntry

parser = ConfigParser(
    special_types={"special_type"}
)

entries = parser.parse_file("parser.p8")

for entry in entries:
    print(entry.page_type)
    print(entry.options)
    print(entry.text)
