from playwright.async_api import Page
from .t_page import TPage

from .tools.list_detector.list_detector import ListDetector

__all__ = ["ListDetector", "wrap"]


async def wrap(page: Page):
    return TPage(page)
