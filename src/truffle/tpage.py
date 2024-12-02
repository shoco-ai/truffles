from playwright.async_api import Page, Locator
from typing import List, Optional, Any, Callable
from .context_repository import ContextRepository
import asyncio
from .tlocator import TLocator

class TPage:
    """Enhanced Page class that adds additional functionality to Playwright's Page"""
    
    def __init__(self, page: Page):
        self.page = page
        self._current_page = 1
        
    async def _get_page_hash(self) -> str:
        """Get unique hash for current page state"""
        # Implementation depends on your specific needs
        raise NotImplementedError("Page hash not implemented")
        return await self.page.evaluate('document.documentElement.outerHTML')
        

    async def _ai_find_selector(self, action_name: str) -> str:
        """Use AI to find appropriate selector"""
        # Implementation of AI selector finding logic
        # This would use LangChain or similar to analyze the page and return a selector
        raise NotImplementedError("AI selector finding not implemented")
        

    async def _execute_with_selector_strategy(self, 
                                            action_name: str,
                                            selector: Optional[str],
                                            action: Callable[[str], Any]) -> Any:
        """Execute action with fallback to AI if needed"""
        if selector:
            try:
                return await action(selector)
            except Exception as e:
                print(f"Error with provided selector: {e}")
                
        # Try getting selector from repository
        page_hash = await self._get_page_hash()
        stored_selector = await self.hash_repository.get_selector(page_hash, action_name)
        
        if stored_selector:
            try:
                result = await action(stored_selector)
                return result
            except Exception:
                # Remove failed selector and try AI approach
                await self.hash_repository.remove_selector(page_hash, action_name)
                
        # AI approach
        try:
            ai_selector = await self._ai_find_selector(action_name)
            result = await action(ai_selector)
            await self.hash_repository.store_selector(page_hash, action_name, ai_selector)
            return result
        except Exception as e:
            raise Exception(f"Failed to find valid selector for {action_name}: {e}")

    async def get_main_list(
        prompt: str = None,
    ):
        """
        If all attributes are empty, the class attempts to use the PageContext 
        to find a working selector for this function. If prompt, then we do
        some agentql things. If selector or attribute we are conventional.
        
        Returns: list[TElement]
        """

        return await self._execute_with_selector_strategy(
            "main_list",
            selector,
            list_action
        )

    async def get_list_by_items(
        self,
        item_selector: str = None,
        item_attribute: dict = None,
        match_mode: str = 'exact'  # Can be 'exact', 'key_only', or 'value_only'
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
        """
        if item_selector and item_attribute:
            raise ValueError("Cannot provide both item_selector and item_attribute")
            
        if item_selector:
            elements = await self.page.locator(item_selector).all()
        elif item_attribute:
            if match_mode == 'exact':
                # Exact key-value matching
                attribute_selector = ' and '.join([f'[{key}="{value}"]' for key, value in item_attribute.items()])
                elements = await self.page.locator(f"*{attribute_selector}").all()
            elif match_mode == 'key_only':
                # Match elements that have all specified keys
                attribute_selector = ' and '.join([f'[{key}]' for key in item_attribute.keys()])
                elements = await self.page.locator(f"*{attribute_selector}").all()
            elif match_mode == 'value_only':
                # Match elements that have any of the specified values
                value_conditions = ' or '.join([
                    f'[*="{value}"]' for value in item_attribute.values()
                ])
                elements = await self.page.locator(f"*:is({value_conditions})").all()
            else:
                raise ValueError("match_mode must be one of: 'exact', 'key_only', 'value_only'")
        else:
            return await self._execute_with_selector_strategy(
                "list_items",
                None,
                lambda selector: self.page.locator(selector).all()
            )
            
        return [TLocator(element) for element in elements]

    async def get_list_by_wrapper(
        wrapper_selector: str = None,
        wrapper_attribute: {} = None,
    ):
        """
        Get list of items by wrapper selector or attribute.
        """
        if wrapper_selector and wrapper_attribute:
            raise ValueError("Cannot provide both wrapper_selector and wrapper_attribute")
        raise NotImplementedError("Not implemented")


    async def paginate(
		prompt: str = None,
	):
        """
        Similar to above. If conventional selector/attributegiven, operate as playwright would, otherwise
        try to AI this.
        """
            
        return await self._execute_with_selector_strategy(
            "paginate",
            next_button_selector,
            paginate_action
        )

    async def wait_for_network_idle(self, timeout: int = 5000):
        """Wait for network connections to be idle"""
        await self.page.wait_for_load_state('networkidle', timeout=timeout)

    async def scroll_to_bottom(self, timeout: int = 5000):
        """Scroll to the bottom of the page"""
        await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await self.wait_for_network_idle(timeout)

    @property
    def current_page(self) -> int:
        """Get the current page number"""
        return self._current_page

    def __getattr__(self, name: str):
        """Delegate any undefined attributes/methods to the underlying page object"""
        output = getattr(self.page, name)

        if isinstance(output, Locator):
            return TLocator(output)

        return output

    def __dir__(self) -> list:
        """Return list of available attributes, including those from the page object"""
        return list(set(super().__dir__() + dir(self.page)))