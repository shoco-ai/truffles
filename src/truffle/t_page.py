from playwright.async_api import Page, Locator
from typing import List, Optional, Any, Callable
from .context import ContextManager
import asyncio
from .t_locator import TLocator
from .tools.list_detector import ListDetector, DetectionMode
from .context.state import ContextManager
from inspect import iscoroutinefunction

from .utils.wrap import wrap_collection

class TPage:
    """Enhanced Page class that adds additional functionality to Playwright's Page"""
    
    def __init__(self, page: Page):
        self._page = page
        self._current_page = 1
        self._list_detector = None  # Lazy initialization
        
    @property
    def list_detector(self) -> ListDetector:
        if self._list_detector is None:
            self._list_detector = ListDetector()
        return self._list_detector
    
    async def _get_page_hash(self) -> str:
        """Get unique hash for current page state"""

        # TODO: do this
        # Implementation depends on your specific needs
        raise NotImplementedError("Page hash not implemented")
        return await self.evaluate('document.documentElement.outerHTML')
        

    async def _ai_find_entry_point(self, action_name: str) -> str:
        """Use AI to find the needed function input"""
        # Implementation of AI selector finding logic
        # This would use LangChain or similar to analyze the page and return a selector
        raise NotImplementedError("AI selector finding not implemented")
        

    async def _execute_function(self, 
                                action_name: str,
                                selector: Optional[str],
                                action: Callable[[str], Any]) -> Any:
        """Execute action with fallback to AI if needed"""
        if selector:
            try:
                return await action(selector)
            except Exception as e:
                print(f"Error with provided selector: {e}")
                
        # Try getting selector from store
        page_hash = await self._get_page_hash()
        stored_selector = await ContextManager.get_marker(page_hash, action_name)
        
        if stored_selector:
            try:
                result = await action(stored_selector)
                return result
            except Exception:
                # Remove failed selector and try AI approach
                await ContextManager.remove_marker(page_hash, action_name)
                
        # AI approach
        try:
            ai_selector = await self._ai_find_entry_point(action_name)
            result = await action(ai_selector)
            await ContextManager.store_marker(page_hash, action_name, ai_selector)
            return result
        except Exception as e:
            raise Exception(f"Failed to find valid selector for {action_name}: {e}")

    async def get_main_list(
        self,
        detection_mode: str = "dynamic",
        force_detect: bool = False
    ) -> List[TLocator]:
        """
        Get the main list from the page.
        
        Args:
            detection_mode: One of "basic", "statistical", "dynamic"
            force_detect: If True, bypass cache and force new detection
            
        Returns:
            List of TLocator objects representing list items
        """
        # Try to get cached selector if not forcing detection
        if not force_detect:
            page_state = await self.evaluate('document.documentElement.outerHTML')
            cached_selector = await ContextManager.get_marker(
                page_state=page_state,
                action_name="list_detection"
            )
            
            if cached_selector:
                items = await self.locator(cached_selector).all()
                if items:
                    return [TLocator(item) for item in items]
        
        # Convert string mode to enum
        try:
            mode = DetectionMode(detection_mode.lower())
        except ValueError:
            raise ValueError(
                f"Invalid detection mode: {detection_mode}. "
                f"Must be one of: {[m.value for m in DetectionMode]}"
            )
        
        # Perform detection
        raise NotImplementedError("List detection not implemented and self._page!!")
        items = await self.list_detector.execute(self._page, mode=mode)
        if not items:
            raise Exception(
                f"Could not detect list structure using {detection_mode} mode"
            )
            
        return [TLocator(item) for item in items]

    async def get_list_by_item(
        self,
        item_selector: Optional[str] = None,
        item_attribute: Optional[dict] = None,
        match_mode: str = 'contains'  # Can be 'exact', 'contains', 'key_only', or 'value_only'
    ) -> List[TLocator]:
        """
        Get list of items by item selector or attribute.
        
        Args:
            item_selector: XPath or CSS selector string to find items
            item_attribute: Dictionary of attributes to match elements
            match_mode: How to match attributes:
                - 'exact': Match both key and value (default)
                - 'key_only': Match elements that have the specified keys, regardless of value
                - 'value_only': Match elements that have the specified values, regardless of key
            
        Returns:
            List of TLocator objects representing the found items
        
        Raises:
            ValueError: If neither item_selector nor item_attribute is provided, or if both are provided
        """

        allowed_match_modes = ('exact', 'contains')

        # Input validation
        if item_selector and item_attribute:
            raise ValueError("Cannot provide both item_selector and item_attribute")
        if not item_selector and not item_attribute:
            raise ValueError("Must provide either item_selector or item_attribute")

        # Handle item_selector case
        if item_selector:
            elements = await self.locator(item_selector).all()
            return [TLocator(element) for element in elements]

        # Handle item_attribute case
        if match_mode not in allowed_match_modes:
            raise ValueError(f"match_mode must be one of: {allowed_match_modes}")
        
        if match_mode == 'exact':
            attribute_selector = ' and '.join([f'[{key}="{value}"]' for key, value in item_attribute.items()])
        else:
            attribute_selector = ' and '.join([f'[{key}~="{value}"]' for key, value in item_attribute.items()])

        # TODO: add key_only and value_only match modes

        elements = await self.locator(f"*{attribute_selector}").all()
        print("elements type", type(elements[0]))
        return elements

    async def get_list_by_wrapper(
        self,
        wrapper_selector: Optional[str] = None,
        wrapper_attribute: Optional[dict] = None,
        match_mode: str = 'contains'
    ) -> List[TLocator]:
        """
        Get list of items that are children of wrapper elements.
        
        Args:
            wrapper_selector: CSS/XPath selector for wrapper elements
            wrapper_attribute: Dictionary of attributes to match wrapper elements
            child_selector: Selector for child elements (defaults to all children)
            match_mode: How to match attributes ('exact' or 'contains')
            
        Returns:
            List of TLocator objects representing the child elements
            
        Raises:
            ValueError: If neither wrapper_selector nor wrapper_attribute is provided 
                      when AI assistance is not enabled
        """
        allowed_match_modes = ('exact', 'contains')

        wrappers = await self.get_list_by_item(
            item_selector=wrapper_selector,
            item_attribute=wrapper_attribute,
            match_mode=match_mode
        )

        all_children = []
        for wrapper in wrappers:
            children = await wrapper.locator(':scope > *').all()
            all_children.extend(children)
    

        return all_children

    async def paginate(
		prompt: str = None,
	):
        """
        Similar to above. If conventional selector/attribute given, operate as playwright would, otherwise
        try to AI this.
        """
        raise NotImplementedError("Pagination not implemented")
            
        return await self._execute_function(
            "paginate",
            next_button_selector,
            paginate_action
        )

    async def wait_for_network_idle(self, timeout: int = 5000):
        """Wait for network connections to be idle"""
        await self.wait_for_load_state('networkidle', timeout=timeout)

    async def scroll_to_bottom(self, timeout: int = 5000):
        """Scroll to the bottom of the page"""
        await self.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await self.wait_for_network_idle(timeout)

    @property
    def current_page(self) -> int:
        """Get the current page number"""
        return self._current_page

    def __getattr__(self, name: str):
        """Delegate any undefined attributes/methods to the underlying page object"""
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

    def __dir__(self) -> list:
        """Return list of available attributes, including those from the page object"""
        return list(set(super().__dir__() + dir(self._page)))