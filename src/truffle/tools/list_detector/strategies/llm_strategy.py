from typing import Optional, List
from pydantic import BaseModel, Field
from playwright.async_api import Page, Locator
from langchain import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage
from truffle.models.config import LLMManager
from .base import ListDetectionStrategy


class DetectionOutput(BaseModel):
    selector: str = Field(description="A substring present in a list element in the texts language.")
    confidence: float = Field(description="Confidence score between 0 and 1")

class ListDetectionOutput(BaseModel):
    items: List[DetectionOutput] = Field(description="A list of detected list items")



class LLMStrategy(ListDetectionStrategy):
    async def detect(self, page: Page) -> Optional[List[Locator]]:
        """AI-powered detection using LLM"""

        # Initialize the model with structured output
        model = LLMManager.get_model().with_structured_output(ListDetectionOutput)

        # Take a screenshot of the full page
        screenshot_bytes = await page.screenshot(full_page=True)

        # Generate prompt using Langchain's message format
        prompt = [
            SystemMessage(content="You are an AI model that detects list elements on a webpage."),
            HumanMessage(
                content = await page.content() + screenshot_bytes
            )
        ]

        # Create an LLMChain with the model and prompt
        chain = LLMChain(model=model, prompt=prompt)

        # Get LLM response
        response = await chain.ainvoke()

        # Parse response to get a list of ListDetectionOutput
        output = [DetectionOutput(**item) for item in response]

        # Convert ListDetectionOutput to Locator objects
        locators = [Locator(page, item.selector) for item in output]

        return locators