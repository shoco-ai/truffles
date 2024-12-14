import asyncio
from typing import Any, Callable, Optional, Type

from pydantic import BaseModel

from truffles.enhanced.page import TPage
from truffles.tasks.task import BaseTask


class ListingTask(BaseTask):
    def __init__(self, page: str | TPage, schema: Type[BaseModel], pre_run: Optional[Callable] = None):
        super().__init__()

        assert isinstance(page, (str, TPage)), "page must be a string or a truffles TPage object"

        self.page_url = page if isinstance(page, str) else None
        self.page = page if isinstance(page, TPage) else None
        self.schema = schema
        self.pre_run = pre_run

    async def _initialize_page(self):
        if self.page_url:
            from playwright.async_api import async_playwright

            import truffles

            p = await async_playwright().start()
            browser = await p.chromium.launch()
            truffles_page = await truffles.wrap(await browser.new_page())
            await truffles_page.goto(self.page_url)
            self.page = truffles_page

    async def run(self, **kwargs) -> Any:
        # Initialize page if needed
        if self.page_url:
            await self._initialize_page()

        if self.pre_run:
            await self.pre_run(self.page)

        locators = await self.page.tools.get_main_list()
        results = await asyncio.gather(*[loc.tools.to_structure(self.schema) for loc in locators])

        return results
