from playwright.async_api import Page
from .enhanced.page import TPage
from .context import ContextManager, MemoryContextStore, ContextStore
from .models import LLMManager

from .tools.list_detector.list_detector import ListDetector

from langchain_anthropic import ChatAnthropic

from langchain_core.language_models.chat_models import BaseChatModel

__all__ = ["ListDetector", "wrap"]


async def wrap(page: Page):
    """Wrap a playwright Page object in a TPage object."""
    return TPage(page)


async def astart(
    context_store: ContextStore = MemoryContextStore(),
    model: BaseChatModel = ChatAnthropic(model="claude-3-5-sonnet-20240620"),
):
    """Initialize the context manager and LLM manager."""
    ContextManager.initialize(context_store)
    LLMManager.initialize(model)

    return
