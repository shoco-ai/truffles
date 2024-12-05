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
        ]
        
        for selector in wrapper_selectors:

            all_candidate_lists = []
            try:
                wrapper = await page.wait_for_selector(selector, timeout=1000)
                if wrapper:
                    # Get all immediate children that look like list items
                    items = await wrapper.locator('> *').all()
                    all_candidate_lists.append(items)
            except:
                continue
                
        return wrapper_lists