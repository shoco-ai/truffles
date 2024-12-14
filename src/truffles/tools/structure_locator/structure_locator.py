from typing import Dict

from playwright.async_api import Locator
from pydantic import BaseModel, Field, ValidationError

from truffles.enhanced.locator import TLocator
from truffles.models.default_model import DefaultModel
from truffles.tools.base import BaseTool
from truffles.tools.structure_locator.exceptions import StructureLocatorOutputValidationError
from truffles.tools.structure_locator.messages import struct_locator_message

MAX_CHAR_LEN = 100000


@TLocator.register_tool("to_structure")
class LocatorToDictTool(BaseTool):
    """
    Convert locator content to a dictionary
    """

    def __init__(self, locator: Locator):
        super().__init__()
        self.locator = locator

    async def _exec_impl(self, element_text: str, structure: BaseModel, filter_relevance: bool = True) -> Dict:
        """Implementation of list getter"""

        # TODO: add implement cropped screenshot passing?

        # add relevance filtering
        class RelevanceFilter(structure):
            is_relevant: bool = Field(description="Is this element relevant to the passed schema?")

        model = DefaultModel.get_specific_model(model_size="small").with_structured_output(
            RelevanceFilter if filter_relevance else structure,
            include_raw=False,  # set to True for debugging
        )
        model = model.with_retry(
            retry_if_exception_type=(ValueError,),
            stop_after_attempt=2,
            wait_exponential_jitter=True,
        )

        messages = struct_locator_message(element_text)

        try:
            response = await model.ainvoke(messages)  # for debugging set `include_raw = True`
        except ValidationError:
            raise StructureLocatorOutputValidationError("Error validating LLM output")

        if filter_relevance:
            if not response.is_relevant:
                return None
            else:
                response_dict = response.model_dump(exclude={"is_relevant"})
                return structure.model_validate(response_dict)
        else:
            return response

    async def execute(self, structure: BaseModel, filter_relevance: bool = True) -> Dict:
        """Convert the locator content to a dictionary"""

        return await self._exec_impl(await self.locator.text_content(), structure, filter_relevance)
