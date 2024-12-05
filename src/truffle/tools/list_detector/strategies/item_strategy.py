from typing import List, Optional
from playwright.async_api import Page, Locator
from .base import ListDetectionStrategy

class ItemStrategy(ListDetectionStrategy):
    async def _detect(self, page: Page) -> Optional[List[Locator]]:
        # Common item selectors
        item_selectors = [
            'li',  # Standard list items
            '[role="listitem"]',  # ARIA listitem role
            '.item', '.list-item',  # Common item class names
            '[class*="item"]',  # Classes containing "item"
            'article',
        ]

        all_candidate_lists = []
        for selector in item_selectors:
            try:
                items = await page.locator(selector).all()
                if items:  # Must have at least 2 items to be considered a list
                    # Verify items have similar structure
                    all_candidate_lists.append(items)
            except:
                continue
                
        return all_candidate_lists
    
    async def _verify_similar_structure(self, items: List[Locator]) -> bool:
        try:
            # Compare the first two items' structure
            if len(items) < 2:
                return False
                
            # Get DOM structure of first two items
            structure1 = await items[0].evaluate('el => el.children.length')
            structure2 = await items[1].evaluate('el => el.children.length')
            
            # Basic similarity check - just compare number of children
            # Could be enhanced to check class names, tag types, etc.
            return structure1 == structure2
        except:
            return False