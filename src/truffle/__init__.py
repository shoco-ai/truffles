from playwright.async_api import Page
from .t_page import TPage
from playwright.async_api import Browser

async def wrap(browser: Browser):
    page = await browser.new_page()
    return TPage(page)