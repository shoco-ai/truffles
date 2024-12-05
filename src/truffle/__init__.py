from playwright.async_api import Page, Browser
from .t_page import TPage

async def wrap(page: Page):
    return TPage(page)