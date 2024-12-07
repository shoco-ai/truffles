from playwright.async_api import Page, Locator
from typing import List, Optional, Any, Callable, Type, Dict, TypeVar, Union
from .context import ContextManager
import asyncio
from .t_locator import TLocator
# from .tools.list_detector import ListDetector
from .context.state import ContextManager
from inspect import iscoroutinefunction

from .utils.wrap import wrap_collection

from .tools.base import BaseTool
T = TypeVar('T', bound=BaseTool)

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

    
    def __init__(self, page: Union[Page, 'TPage']):
        assert isinstance(page, Page) or isinstance(page, TPage), "page must be a playwright Page or TPage"
        self._page = page
        self._tool_instances = {}


    # async def get_main_list(
    #     self,
    #     detection_mode: str = "llm",
    #     force_detect: bool = False
    # ) -> List[TLocator]:
    #     """
    #     Get the main list from the page.
        
    #     Args:
    #         detection_mode: One of "basic", "statistical", "dynamic"
    #         force_detect: If True, bypass cache and force new detection
            
    #     Returns:
    #         List of TLocator objects representing list items
    #     """
    #     # Try to get cached selector if not forcing detection
    #     if not force_detect:
    #         page_state = await self.evaluate('document.documentElement.outerHTML')
    #         cached_selector = await ContextManager.get_marker(
    #             page_state=page_state,
    #             action_name="list_detection"
    #         )
            
    #         if cached_selector:
    #             items = await self.locator(cached_selector).all()
    #             if items:
    #                 return [TLocator(item) for item in items]
        
        
    #     marker = await self.list_detector.execute(self._page, strategy=detection_mode)

    #     if not marker:
    #         return None
        
    #     items = await self.get_list_by_wrapper(wrapper_selector=marker.get_selector())
            
    #     return items

    # async def get_list_by_item(
    #     self,
    #     item_selector: Optional[str] = None,
    #     item_attribute: Optional[dict] = None,
    #     match_mode: str = 'contains'  # Can be 'exact', 'contains', 'key_only', or 'value_only'
    # ) -> List[TLocator]:
    #     """
    #     Get list of items by item selector or attribute.
        
    #     Args:
    #         item_selector: XPath or CSS selector string to find items
    #         item_attribute: Dictionary of attributes to match elements
    #         match_mode: How to match attributes:
    #             - 'exact': Match both key and value (default)
    #             - 'key_only': Match elements that have the specified keys, regardless of value
    #             - 'value_only': Match elements that have the specified values, regardless of key
            
    #     Returns:
    #         List of TLocator objects representing the found items
        
    #     Raises:
    #         ValueError: If neither item_selector nor item_attribute is provided, or if both are provided
    #     """

    #     allowed_match_modes = ('exact', 'contains')

    #     # Input validation
    #     if item_selector and item_attribute:
    #         raise ValueError("Cannot provide both item_selector and item_attribute")
    #     if not item_selector and not item_attribute:
    #         raise ValueError("Must provide either item_selector or item_attribute")

    #     # Handle item_selector case
    #     if item_selector:
    #         elements = await self.locator(item_selector).all()
    #         return elements

    #     # Handle item_attribute case
    #     if match_mode not in allowed_match_modes:
    #         raise ValueError(f"match_mode must be one of: {allowed_match_modes}")
        
    #     if match_mode == 'exact':
    #         attribute_selector = ' and '.join([f'[{key}="{value}"]' for key, value in item_attribute.items()])
    #     else:
    #         attribute_selector = ' and '.join([f'[{key}~="{value}"]' for key, value in item_attribute.items()])


    #     elements = await self.locator(f"*{attribute_selector}").all()
    #     return elements

    # async def get_list_by_wrapper(
    #     self,
    #     wrapper_selector: Optional[str] = None,
    #     wrapper_attribute: Optional[dict] = None,
    #     match_mode: str = 'contains'
    # ) -> List[TLocator]:
    #     """
    #     Get list of items that are children of wrapper elements.
        
    #     Args:
    #         wrapper_selector: CSS/XPath selector for wrapper elements
    #         wrapper_attribute: Dictionary of attributes to match wrapper elements
    #         child_selector: Selector for child elements (defaults to all children)
    #         match_mode: How to match attributes ('exact' or 'contains')
            
    #     Returns:
    #         List of TLocator objects representing the child elements
            
    #     Raises:
    #         ValueError: If neither wrapper_selector nor wrapper_attribute is provided 
    #                   when AI assistance is not enabled
    #     """
    #     allowed_match_modes = ('exact', 'contains')

    #     wrappers = await self.get_list_by_item(
    #         item_selector=wrapper_selector,
    #         item_attribute=wrapper_attribute,
    #         match_mode=match_mode
    #     )

    #     all_children = []
    #     for wrapper in wrappers:
    #         children = await wrapper.locator(':scope > *').all()
    #         all_children.extend(children)
    

    #     return all_children


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