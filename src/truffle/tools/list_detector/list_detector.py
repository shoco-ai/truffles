from enum import Enum
from typing import List, Optional, Dict, Type
from playwright.async_api import Page, Locator
from ..base import BaseTool
from .strategies.base import ListDetectionStrategy
from .strategies.wrapper_strategy import WrapperStrategy
from .strategies.item_strategy import ItemStrategy
from ...context.state import ContextManager

class DetectionMode(Enum):
    BASIC = "basic"        # Uses simple wrapper and item strategies
    STATISTICAL = "statistical"  # Uses pattern matching and frequency analysis
    DYNAMIC = "dynamic"    # Uses AI and dynamic analysis

class ListDetector(BaseTool):
    def __init__(self):
        super().__init__()
        # Strategy factories for each mode
        self._strategy_factories: Dict[DetectionMode, callable] = {
            DetectionMode.BASIC: self._create_basic_chain,
            DetectionMode.STATISTICAL: self._create_statistical_chain,
            DetectionMode.DYNAMIC: self._create_dynamic_chain
        }
        
    def _create_basic_chain(self) -> ListDetectionStrategy:
        wrapper = WrapperStrategy()
        item = ItemStrategy()
        wrapper.set_next(item)
        return wrapper
        
    def _create_statistical_chain(self) -> ListDetectionStrategy:
        # TODO: Implement statistical strategies
        return self._create_basic_chain()
        
    def _create_dynamic_chain(self) -> ListDetectionStrategy:
        # TODO: Implement AI-driven strategies
        return self._create_basic_chain()
    
    async def execute(
        self, 
        page: Page, 
        mode: DetectionMode = DetectionMode.BASIC,
        **kwargs
    ) -> Optional[List[Locator]]:
        # Get strategy chain for requested mode
        strategy = self._strategy_factories[mode]()
        
        # Try to detect list
        items = await strategy.handle(page)
        if not items:
            return None
            
        # If successful, store the selector for future use
        if items and len(items) > 0:
            # Store the first item's selector as the marker
            # This assumes items[0] has a valid selector property
            selector = await items[0].evaluate('el => el.tagName + el.className')
            page_hash = await page.evaluate('document.documentElement.outerHTML')
            await ContextManager.store_marker(
                page_hash=page_hash,
                action_name="list_detection",
                selector=selector
            )
            
        return items

    def get_prompt(self) -> str:
        return "Identify list structure in the page"
    
    @property
    def name(self) -> str:
        return "list_detector"
