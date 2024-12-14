from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage
from playwright.async_api import Locator
from pydantic import BaseModel, ValidationError

from truffles.enhanced.locator import TLocator
from truffles.models.default_model import DefaultModel
from truffles.tools.base import BaseTool

MAX_CHAR_LEN = 100000


@TLocator.register_tool("to_structure")
class LocatorToDictTool(BaseTool):
    """
    Convert locator content to a dictionary using a language model
    """

    def __init__(self, locator: Locator):
        super().__init__()
        self.locator = locator

    async def _exec_impl(self, element_text: str, structure: BaseModel) -> Dict:
        """Implementation of list getter"""

        # TODO: add implement cropped screenshot passing?

        model = DefaultModel.get_specific_model(model_size="small").with_structured_output(
            structure,
            include_raw=False,  # set to True for debugging
        )
        model = model.with_retry(
            retry_if_exception_type=(ValueError,),
            stop_after_attempt=2,
            wait_exponential_jitter=True,
        )

        messages = [
            SystemMessage(
                content="""You are an AI model that converts the visible text on a webpage to structured data.
                You always use the correct pydantic format if the element is relevant, else return None."""
            ),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": element_text,
                    },
                ]
            ),
        ]

        try:
            response = await model.ainvoke(messages)  # for debugging set `include_raw = True`
            return response

        except ValidationError:
            return None

    async def execute(self, structure: BaseModel) -> Dict:
        """Convert the locator content to a dictionary"""

        return await self._exec_impl(await self.locator.text_content(), structure)
