from playwright.async_api import Page, Browser
from .t_page import TPage

from .tools.list_detector.list_detector import ListDetector

async def wrap(page: Page):
    return TPage(page)