from pages.factory import PageFactory


class DummyProcessor:
    pass


def test_register_store_processor_class():
    @PageFactory.register("demo", processor_class=DummyProcessor)
    class DemoPage:
        pass

    assert PageFactory.get_processor_class("demo") is DummyProcessor
