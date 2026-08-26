class PageFactory:

    _pages = {}

    @classmethod
    def register(cls, name, detail_class=None):

        def decorator(page_class):

            cls._pages[name] = {
                "page_class": page_class,
                "detail_class": detail_class,
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
    def OLDget_detail_class(cls, name):
        return cls._pages[name]["detail_class"]


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
    def create(cls, name, config):
        page_class = cls.get_page_class(name)
        return page_class(config)

    @classmethod
    def create_detail(cls, name):

        detail_class = cls.get_detail_class(name)

        if detail_class is None:
            return None

        return detail_class()