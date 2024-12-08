from typing import List, Optional

from playwright.async_api import Locator, Page, TimeoutError

from .base import ListDetectionStrategy


class ItemStrategy(ListDetectionStrategy):
    async def _detect(self, page: Page) -> Optional[List[Locator]]:
        # Common item selectors
        item_selectors = [
            "li",  # Standard list items
            '[role="listitem"]',  # ARIA listitem role
            ".item",
            ".list-item",  # Common item class names
            '[class*="item"]',  # Classes containing "item"
            "article",
        ]

        all_candidate_lists = []
        for selector in item_selectors:
            try:
                items = await page.locator(selector).all()
                if items:  # Must have at least 2 items to be considered a list
                    # Verify items have similar structure
                    all_candidate_lists.append(items)
            except TimeoutError:
                continue

        return all_candidate_lists
