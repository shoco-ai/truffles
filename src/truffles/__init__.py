from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from playwright.async_api import Page

from truffles.context import ContextStore, MemoryContextStore, StoreManager
from truffles.enhanced.page import TPage
from truffles.models import DefaultModel
from truffles.tools.list_detector.list_detector import ListDetector
from truffles.tools.md_gen.markdown_gen import MarkdownGen
from truffles.tools.structure_locator.structure_locator import LocatorToDictTool

__all__ = ["ListDetector", "LocatorToDictTool", "MarkdownGen", "wrap", "__version__"]

__version__ = "0.1.0"


async def wrap(page: Page):
    """Wrap a playwright Page object in a TPage object."""
    return TPage(page)


async def start(
    context_store: ContextStore = MemoryContextStore(),
    model: BaseChatModel = ChatOpenAI(model="gpt-4o"),
):
    """Initialize the StoreManager and LLMManager."""
    StoreManager.initialize(context_store)
    DefaultModel.initialize(model)

    return
