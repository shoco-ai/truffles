from typing import List, Optional

from bs4 import BeautifulSoup
from playwright.async_api import Locator, Page

from ...context.state import ContextManager
from ...enhanced.locator import TLocator

# from ...t_page import TPage
# from ...t_locator import TLocator
from ...enhanced.page import TPage
from ..base import BaseTool
from .strategies.llm_strategy import LLMStrategy

ALLOWED_MATCH_MODES = ("exact", "contains")


@TPage.register_tool("get_main_list")
class ListDetector(BaseTool):
    """
    Main list detection tool that uses AI and caching to efficiently detect lists.
    """

    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self._soup: Optional[BeautifulSoup] = None

    async def _get_list_by_item(
        self,
        item_selector: Optional[str] = None,
        item_attribute: Optional[dict] = None,
        match_mode: str = "contains",  # Can be 'exact', 'contains', 'key_only', or 'value_only'
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

        ALLOWED_MATCH_MODES = ("exact", "contains")

        # Input validation
        if item_selector and item_attribute:
            raise ValueError("Cannot provide both item_selector and item_attribute")
        if not item_selector and not item_attribute:
            raise ValueError("Must provide either item_selector or item_attribute")

        # Handle item_selector case
        if item_selector:
            elements = await self.page.locator(item_selector).all()
            return elements

        # Handle item_attribute case
        if match_mode not in ALLOWED_MATCH_MODES:
            raise ValueError(f"match_mode must be one of: {ALLOWED_MATCH_MODES}")

        if match_mode == "exact":
            attribute_selector = " and ".join([f'[{key}="{value}"]' for key, value in item_attribute.items()])
        else:
            attribute_selector = " and ".join([f'[{key}~="{value}"]' for key, value in item_attribute.items()])

        elements = await self.locator(f"*{attribute_selector}").all()
        return elements

    async def _get_list_by_wrapper(
        self,
        wrapper_selector: Optional[str] = None,
        wrapper_attribute: Optional[dict] = None,
        match_mode: str = "contains",
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

        wrappers = await self._get_list_by_item(
            item_selector=wrapper_selector,
            item_attribute=wrapper_attribute,
            match_mode=match_mode,
        )

        all_children = []
        for wrapper in wrappers:
            children = await wrapper.locator(":scope > *").all()
            all_children.extend(children)

        return all_children

    async def execute(self, strategy: str = "llm", force_detect: bool = False, **kwargs) -> Optional[List[Locator]]:
        # TODO: make this nice and extensible
        detection_strategies = ["basic", "statistical", "llm"]
        if strategy not in detection_strategies:
            raise ValueError(f"Invalid strategy '{strategy}'. Must be one of: {detection_strategies}")

        page_state = await self.page.evaluate("document.documentElement.outerHTML")

        # try to get cached result first
        if not force_detect:
            cached_marker = await ContextManager.get_marker(page_state=page_state, action_name="list_detector")

            if cached_marker:
                return await self._get_list_by_wrapper(wrapper_selector=cached_marker.get_selector())

        # Detect lists using requested strategy
        marker = await self._detect_list(strategy)
        if not marker:
            return None

        await ContextManager.store_marker(page_state=page_state, action_name="list_detector", marker=marker)

        items = await self._get_list_by_wrapper(wrapper_selector=marker.get_selector())

        return [TLocator(item) for item in items]

    async def _detect_list(
        self,
        strategy: str,
    ) -> Optional[List[Locator]]:
        if strategy == "llm":
            llm_strategy = LLMStrategy()
            return await llm_strategy.detect(self.page)
        else:
            raise NotImplementedError(f"Detection strategy {strategy} not implemented yet. Want to help?")

    @property
    def name(self) -> str:
        return "list_detector"
