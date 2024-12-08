from abc import ABC, abstractmethod
from typing import List, Optional
from playwright.async_api import Page, Locator


class ListDetectionStrategy(ABC):
    @abstractmethod
    async def detect(self, page: Page) -> Optional[List[Locator]]:
        pass
