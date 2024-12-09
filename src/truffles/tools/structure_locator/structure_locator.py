from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage
from playwright.async_api import Locator
from pydantic import BaseModel, ValidationError

from truffles.enhanced.locator import TLocator
from truffles.models.config import LLMManager

from ..base import BaseTool

MAX_CHAR_LEN = 100000


@TLocator.register_tool("to_structure")
class LocatorToDictTool(BaseTool):
    """
    Locate the structure of the page.
    """

    def __init__(self, locator: Locator):
        super().__init__()
        self.locator = locator

    async def _exec_impl(self, element, structure: BaseModel) -> Dict:
        """Implementation of list getter"""

        # TODO: implement cropped screenshot passing

        print("structure", structure)
        print("element", element)

        model = LLMManager.get_model().with_structured_output(structure, include_raw=False)
        model = model.with_retry(
            retry_if_exception_type=(ValueError,),
            stop_after_attempt=2,
            wait_exponential_jitter=True,
        )

        visible_text = (await element.text_content())[:MAX_CHAR_LEN]

        messages = [
            SystemMessage(
                content="""You are an AI model that converts the visible text on a webpage to structured data.
                You always use the correct pydantic format if the element is relevant, else return None."""
            ),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": visible_text,
                    },
                ]
            ),
        ]

        try:
            response = await model.ainvoke(messages)  # for debugging set `include_raw = True`
            return response

        except ValidationError:
            return None

    async def execute(
        self,
        structure: BaseModel,
        per_element: bool = True,
        # automatic_filter: bool = True,  # TODO: add this in different pattern?
    ) -> Dict:
        """Convert the locator content to a dictionary"""

        if per_element:
            elements = await self.locator.all()
            if len(elements) > 1:
                structure = []
                for element in elements:
                    element_structure = await self._exec_impl(element, structure)
                    structure.append(element_structure)

                return structure

        return await self._exec_impl(self.locator, structure)
