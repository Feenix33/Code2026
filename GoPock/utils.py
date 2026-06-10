import shlex

from data_classes import PageSpec


def set_nested_attr(obj, path, value):
    # print("SETTING:", path, "=", value, "on", obj)

    parts = path.split(".")
    current = obj

    for part in parts[:-1]:
        print("  traversing:", part, "->", getattr(current, part))
        current = getattr(current, part)

    setattr(current, parts[-1], value)


def get_nested_attr(obj, path):
    current = obj
    for part in path.split("."):
        current = getattr(current, part)
    return current


def convert_value(value):
    value = value.strip()

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    return value


def parse_attributes(text):
    attrs = {}
    tokens = shlex.split(text)

    for token in tokens:
        if "=" not in token:
            continue

        key, value = token.split("=", 1)
        attrs[key] = convert_value(value)
    return attrs


def read_page_specs(filename):
    specs = []

    with open(filename, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    line_number = 0

    while line_number < len(lines):
        raw_line = lines[line_number]
        line = raw_line.strip()
        line_number += 1

        if not line:
            continue

        if line.startswith("#"):
            continue

        spec_start_line = line_number

        if line.endswith("{"):
            page_type = line[:-1].strip()
            attrs = {}

            while line_number < len(lines):
                block_line = lines[line_number].strip()
                line_number += 1
                if block_line == "}":
                    break

                if not block_line:
                    continue

                if block_line.startswith("#"):
                    continue

                attrs.update(parse_attributes(block_line))
        else:
            parts = shlex.split(line)
            page_type = parts[0]
            attrs_text = line[len(page_type):]
            attrs = parse_attributes(attrs_text)

        specs.append(PageSpec(page_type=page_type, attrs=attrs, line_number=spec_start_line))

    return specs


def build_book(book, specs, page_factory):
    for spec in specs:
        if spec.page_type == "book":
            for key, value in spec.attrs.items():
                try:
                    set_nested_attr(book.config, key, value)
                except AttributeError:
                    print(f"WARNING line {spec.line_number}: unknown book setting '{key}'")
            continue

        if spec.page_type == "defaults":
            for key, value in spec.attrs.items():
                try:
                    set_nested_attr(book.style, key, value)
                except AttributeError:
                    print(f"WARNING line {spec.line_number}: unknown style attribute '{key}'")
            continue

        # print(f"Creating page of type '{spec.page_type}' with attributes {spec.attrs}")
        page = page_factory.create(spec.page_type, **spec.attrs)
        if page is None:
            print(f"WARNING line {spec.line_number}: unknown page type '{spec.page_type}'")
            continue

        page.overrides = spec.attrs
        book.add_page(page)
