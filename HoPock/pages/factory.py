import copy

class PageFactory:

    _pages = {}

    @classmethod
    def register(
        cls,
        name,
        detail_class=None,
        processor_class=None,
        expands_to=None
    ):

        def decorator(page_class):

            cls._pages[name] = {
                "page_class": page_class,
                "detail_class": detail_class,
                "processor_class": processor_class,
                "expands_to": expands_to,
            }

            return page_class

        return decorator

    @classmethod
    def is_registered(cls, name):
        return name in cls._pages

    @classmethod
    def get_page_class(cls, name):
        return cls._pages[name]["page_class"]

    @classmethod
    def get_detail_class(cls, name):
        if name not in cls._pages:
            raise ValueError(
                f"Unknown page type '{name}'. "
                f"Registered page types: "
                f"{list(cls._pages.keys())}"
            )
        return cls._pages[name]["detail_class"]

    @classmethod
    def get_processor_class(cls, name):
        if name not in cls._pages:
            raise ValueError(
                f"Unknown page type '{name}'. "
                f"Registered page types: "
                f"{list(cls._pages.keys())}"
            )
        return cls._pages[name]["processor_class"]

    @classmethod
    def create(cls, page_config, booklet_style):
        page_type = page_config.page_type
        page_class = cls.get_page_class(page_type)

        if page_class is None:
            raise ValueError(
                f"Unknown page type: {page_type}"
            )

        processor_class = cls.get_processor_class(page_type)

        if processor_class is not None:
            return page_class(
                page_config,
                booklet_style,
                processor_class()
            )

        return page_class(page_config, booklet_style)

    @classmethod
    def create_detail(cls, name):

        detail_class = cls.get_detail_class(name)

        if detail_class is None:
            return None

        return detail_class()

    @classmethod
    def expand(cls, page_config):

        page_type = page_config.page_type

        if page_type not in cls._pages:
            raise ValueError(f"Unknown page type '{page_type}'")

        entry = cls._pages[page_type]
        expanded_types = entry.get("expands_to")

        if not expanded_types:
            return [page_config]

        result = []

        for page_type in expanded_types:
            expanded_config = copy.copy(page_config)
            expanded_config.page_type = page_type
            result.append(expanded_config)

        return result