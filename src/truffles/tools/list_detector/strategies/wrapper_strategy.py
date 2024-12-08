from typing import List, Optional

from playwright.async_api import Locator, Page, TimeoutError

from .base import ListDetectionStrategy


class WrapperStrategy(ListDetectionStrategy):
    async def _detect(self, page: Page) -> Optional[List[Locator]]:
        # Common wrapper selectors
        wrapper_selectors = [
            "ul",
            "ol",  # Standard list elements
            '[role="list"]',  # ARIA list role
            ".list",
            ".list-container",  # Common list class names
            '[class*="list"]',  # Classes containing "list"
        ]

        all_candidate_lists = []
        for selector in wrapper_selectors:
            try:
                wrapper = await page.wait_for_selector(selector, timeout=1000)
                if wrapper:
                    # Get all immediate children that look like list items
                    items = await wrapper.locator("> *").all()
                    if items:  # Only add non-empty lists
                        all_candidate_lists.append(items)
            except TimeoutError:
                continue

        # Return the longest list or None if no lists were found
        return max(all_candidate_lists, key=len, default=None)
