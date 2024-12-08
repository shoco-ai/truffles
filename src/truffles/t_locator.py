from typing import Union
from playwright.async_api import Locator
from inspect import iscoroutinefunction

from .utils.wrap import wrap_collection


class TLocator:
    def __init__(self, locator: Union[Locator, "TLocator"]):
        assert isinstance(locator, Locator) or isinstance(
            locator, TLocator
        ), "locator must be a playwright Locator or TLocator"

        self._locator = locator

    def __getattr__(self, name: str):
        """Delegate any undefined attributes/methods to the underlying page object"""
        output = getattr(self._locator, name)

        # If it's a method, wrap the return value after calling
        if callable(output):
            if iscoroutinefunction(output):

                async def wrapped(*args, **kwargs):
                    result = await output(*args, **kwargs)
                    if isinstance(result, Locator):
                        return TLocator(result)
                    elif isinstance(result, (list, tuple, set, dict)):
                        return wrap_collection(result)
                    return result

                return wrapped
            else:

                def wrapped(*args, **kwargs):
                    result = output(*args, **kwargs)
                    if isinstance(result, Locator):
                        return TLocator(result)
                    elif isinstance(result, (list, tuple, set, dict)):
                        return wrap_collection(result)
                    return result

                return wrapped

        # Handle properties and other attributes
        if isinstance(output, Locator):
            return TLocator(output)
        elif isinstance(output, (list, tuple, set, dict)):
            return wrap_collection(output)
        return output

    def __dir__(self) -> list:
        """Return list of available attributes, including those from the page object"""
        return list(set(super().__dir__() + dir(self._locator)))

    @property
    def parent(self) -> "TLocator":
        return self.locator("..")
