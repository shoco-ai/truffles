from abc import ABC, abstractmethod
from typing import List, Optional
from playwright.async_api import Page, Locator

class ListDetectionStrategy(ABC):
    def __init__(self):
        self._next_strategy: Optional['ListDetectionStrategy'] = None
    
    def set_next(self, strategy: 'ListDetectionStrategy') -> 'ListDetectionStrategy':
        self._next_strategy = strategy
        return strategy
    
    async def handle(self, page: Page) -> Optional[List[Locator]]:
        result = await self._detect(page)
        if result is None and self._next_strategy:
            return await self._next_strategy.handle(page)
        return result
    
    @abstractmethod
    async def _detect(self, page: Page) -> Optional[List[Locator]]:
        pass