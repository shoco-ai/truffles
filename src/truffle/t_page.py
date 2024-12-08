from playwright.async_api import Page, Locator
from typing import Callable, Type, Dict, TypeVar, Union
from .t_locator import TLocator
from inspect import iscoroutinefunction

from .utils.wrap import wrap_collection

from .tools.base import BaseTool

T = TypeVar("T", bound=BaseTool)


class TPage:
    """Enhanced Page class that adds additional functionality to Playwright's Page"""

    _tools: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[Type[T]], Type[T]]:
        def decorator(tool_class: Type[T]) -> Type[T]:
            if not issubclass(tool_class, BaseTool):
                raise TypeError(f"{tool_class.__name__} must inherit from BaseTool")
            if name in cls._tools:
                raise ValueError(f"Tool {name} already registered")
            cls._tools[name] = tool_class
            return tool_class

        return decorator

    def __init__(self, page: Union[Page, "TPage"]):
        assert isinstance(page, Page) or isinstance(
            page, TPage
        ), "page must be a playwright Page or TPage"
        self._page = page
        self._tool_instances = {}

    def __getattr__(self, name: str):
        """
        Delegate attributes/methods with the following priority:
        1. Native Playwright methods/properties
        2. Registered tools
        3. Raise AttributeError
        """
        # First try to get the native Playwright attribute
        try:
            output = getattr(self._page, name)

            # If it's a method, wrap the return value after calling
            if callable(output):
                if iscoroutinefunction(output):

                    async def wrapped(*args, **kwargs):
                        result = await output(*args, **kwargs)
                        if isinstance(result, Locator):
                            return TLocator(result)
                        elif isinstance(result, Page):
                            return TPage(result)
                        elif isinstance(result, (list, tuple, set, dict)):
                            return wrap_collection(result)
                        return result

                    return wrapped
                else:

                    def wrapped(*args, **kwargs):
                        result = output(*args, **kwargs)
                        if isinstance(result, Locator):
                            return TLocator(result)
                        elif isinstance(result, Page):
                            return TPage(result)
                        elif isinstance(result, (list, tuple, set, dict)):
                            return wrap_collection(result)
                        return result

                    return wrapped

            # Handle properties and other attributes
            if isinstance(output, Locator):
                return TLocator(output)
            elif isinstance(output, Page):
                return TPage(output)
            elif isinstance(output, (list, tuple, set, dict)):
                return wrap_collection(output)
            return output

        except AttributeError:
            if name in self._tools:
                if name not in self._tool_instances:
                    self._tool_instances[name] = self._tools[name](self)

                async def tool_wrapper(*args, **kwargs):
                    tool_instance = self._tool_instances[name]
                    result = await tool_instance.execute(*args, **kwargs)
                    # Wrap tool results
                    if isinstance(result, Locator):
                        return TLocator(result)
                    elif isinstance(result, Page):
                        return TPage(result)
                    elif isinstance(result, (list, tuple, set, dict)):
                        return wrap_collection(result)
                    return result

                return tool_wrapper

            # If neither exists, raise AttributeError
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute or tool '{name}'"
            )

    def __dir__(self) -> list:
        """Return list of available attributes, including those from the page object"""
        return list(set(super().__dir__() + dir(self._page)))
