from typing import List, Optional
from playwright.async_api import Page, Locator
from .base import ListDetectionStrategy

class WrapperStrategy(ListDetectionStrategy):
    async def _detect(self, page: Page) -> Optional[List[Locator]]:
        # Common wrapper selectors
        wrapper_selectors = [
            'ul', 'ol',  # Standard list elements
            '[role="list"]',  # ARIA list role
            '.list', '.list-container',  # Common list class names
            '[class*="list"]',  # Classes containing "list"
            'div:has(> div:nth-child(1):first-of-type + div)'  # Repeated div patterns
        ]
        
        for selector in wrapper_selectors:
            try:
                wrapper = await page.wait_for_selector(selector, timeout=1000)
                if wrapper:
                    # Get all immediate children that look like list items
                    items = await wrapper.locator('> *').all()
                    if len(items) > 1:  # Must have at least 2 items to be considered a list
                        return items
            except:
                continue
                
        return None