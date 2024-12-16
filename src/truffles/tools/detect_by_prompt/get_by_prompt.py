from playwright.async_api import Page
from pydantic import BaseModel, Field

from truffles import TRUFFLES_ATTRIBUTE_ID
from truffles.enhanced.page import TPage
from truffles.models import DefaultModel
from truffles.tools.base import BaseTool
from truffles.tools.detect_by_prompt.recursor import traverse
from truffles.utils.ax_tree.generate import generate_ax_tree


class Output(BaseModel):
    match: str = Field(
        description="Result of the search. 'found' if the content matches the prompt very well, 'partial' if the prompt is found but there are more elements (these will then be inspected separately), 'not_found' if the prompt is not found",
        format="['found', 'partial', 'not_found']",
    )


@TPage.register_tool("get_by_prompt")
class GetByPrompt(BaseTool):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page

    async def execute(self, prompt: str):
        ax_tree = await generate_ax_tree(self.page)

        model = DefaultModel.get_model().with_structured_output(Output).with_retry()

        truffle_ids = await traverse(ax_tree, model, prompt)

        if len(truffle_ids) == 0:
            return None

        return self.page.locator(f"{TRUFFLES_ATTRIBUTE_ID}={truffle_ids[0]}")
