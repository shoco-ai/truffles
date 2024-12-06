from typing import List, Optional, Dict, Any
from enum import Enum
from bs4 import BeautifulSoup, Tag
from collections import Counter
from langchain_core.language_models import BaseLanguageModel
from playwright.async_api import Page, Locator

from ..base import BaseTool
from ...models.config import LLMManager
from ...context.state import ContextManager
from ...context.marker import SimpleMarker
from .strategies.llm_strategy import LLMStrategy


class ListDetector(BaseTool):
    """
    Enhanced list detection tool that combines traditional parsing with AI capabilities.
    Supports multiple detection strategies and caches results for improved performance.
    """
    
    def __init__(self):
        super().__init__()
        self._soup: Optional[BeautifulSoup] = None
        
    async def execute(
        self,
        page: Page,
        strategy: str = "llm",
        **kwargs
    ) -> Optional[List[Locator]]:

        detection_strategies = ["basic", "statistical", "llm"]
        if strategy not in detection_strategies:
            raise ValueError(f"Invalid strategy '{strategy}'. Must be one of: {detection_strategies}")
        
        # Get page content and create soup
        
        # Try to get cached result first
        page_state = await page.evaluate('document.documentElement.outerHTML')
        cached_marker = await ContextManager.get_marker(page_state, "list_detection")
        
        if cached_marker:
            # FIX: I WANT TO HAVE A TPAGE/TLOCATOR SO I CAN WRAP MARKERS HERE WHY DO CIRCULAR IMPORTS HATE ME
            items = await page.locator(cached_marker.get_selector()).all()
            if items:
                return items
        
        # Detect lists using requested strategy
        marker = await self._detect_lists(page, strategy)
        if not marker:
            return None

        await ContextManager.store_marker(
            page_state=page_state,
            action_name="list_detection",
            marker=marker
        )
        
        return marker
        
    async def _detect_lists(
        self,
        page: Page,
        strategy: str,
    ) -> Optional[List[Locator]]:
        if strategy == "llm":
            llm_strategy = LLMStrategy()
            return await llm_strategy.detect(page)
        else:
            raise NotImplementedError(f"Detection strategy {strategy} not implemented yet. Want to help?")
            

    async def _basic_detection(self, page: Page) -> Optional[List[Locator]]:
        """Basic detection using common HTML patterns"""

        # TODO: Implment this.

        selectors = [
            'ul > li',
            'ol > li',
            '[role="list"] > [role="listitem"]',
            '.list > .list-item',
            '.items > .item',
            'article',
        ]
        
        for selector in selectors:
            items = await page.locator(selector).all()
            if len(items) > 1:
                return items
        return None
        
    async def _statistical_detection(self, page: Page) -> Optional[List[Locator]]:
        """Statistical detection using frequency analysis"""
        # Find repeated patterns in DOM structure
        raise NotImplementedError("Needs to be added.")

    @property 
    def name(self) -> str:
        return "list_detector"
