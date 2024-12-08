from typing import Any, Union

from playwright.async_api import Locator

from ..core.enhanced import Enhanced
from ..utils.wrap import wrap_collection


class TLocator(Enhanced):
    def __init__(self, locator: Union[Locator, "TLocator"]):
        assert isinstance(locator, Locator) or isinstance(
            locator, TLocator
        ), "locator must be a playwright Locator or TLocator"
        super().__init__(locator)

    def _wrap_result(self, result: Any) -> Any:
        if isinstance(result, Locator):
            return TLocator(result)
        elif isinstance(result, (list, tuple, set, dict)):
            return wrap_collection(result)
        return result

    @property
    def parent(self) -> "TLocator":
        return self.locator("..")
