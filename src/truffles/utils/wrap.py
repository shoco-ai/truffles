from playwright.async_api import Locator, Page


def wrap_collection(collection):
    """Recursively wrap nested collections containing Page or Locator objects."""

    from ..enhanced.locator import TLocator
    from ..enhanced.page import TPage

    if isinstance(collection, dict):
        return {
            key: (
                TLocator(value)
                if isinstance(value, Locator)
                else (
                    TPage(value)
                    if isinstance(value, Page)
                    else (wrap_collection(value) if isinstance(value, (list, tuple, set, dict)) else value)
                )
            )
            for key, value in collection.items()
        }

    return type(collection)(
        (
            TLocator(item)
            if isinstance(item, Locator)
            else (
                TPage(item)
                if isinstance(item, Page)
                else (wrap_collection(item) if isinstance(item, (list, tuple, set, dict)) else item)
            )
        )
        for item in collection
    )
