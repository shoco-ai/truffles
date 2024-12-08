from typing import Any, Union

from playwright.async_api import Locator, Page

from ..core.enhanced import Enhanced
from ..utils.wrap import wrap_collection
from .locator import TLocator


class TPage(Enhanced):
    def __init__(self, page: Union[Page, "TPage"]):
        assert isinstance(page, Page) or isinstance(page, TPage), "page must be a playwright Page or TPage"
        super().__init__(page)

    def _wrap_result(self, result: Any) -> Any:
        if isinstance(result, Locator):
            return TLocator(result)
        elif isinstance(result, Page):
            return TPage(result)
        elif isinstance(result, (list, tuple, set, dict)):
            return wrap_collection(result)
        return result
