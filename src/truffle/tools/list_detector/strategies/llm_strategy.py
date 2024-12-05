from typing import Optional, List
from pydantic import BaseModel, Field
from playwright.async_api import Page, Locator
from langchain import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage
from truffle.models.config import LLMManager
from .base import ListDetectionStrategy
import base64
from PIL import Image
import io


class DetectionOutput(BaseModel):
    selector: str = Field(description="A substring present in a list element in the texts language that can be used to CTRL+F the element.")
    # confidence: float = Field(description="Confidence score between 0 and 1")

class ListDetectionOutput(BaseModel):
    items: List[DetectionOutput] # = Field(description="A list of detected items (this wraps the output)")



class LLMStrategy(ListDetectionStrategy):
    async def _get_candidates(self, page: Page) -> Optional[List[Locator]]:
        """AI-powered detection using LLM"""
        
        # Initialize the model with structured output
        model = LLMManager.get_model().with_structured_output(
            ListDetectionOutput, 
            include_raw=True
        )
        model = model.with_retry(
            retry_if_exception_type=(ValueError,),
            stop_after_attempt=2,
            wait_exponential_jitter=True
        )

        # Take a screenshot of the full page
        screenshot_bytes = await page.screenshot(full_page=True)

        # Crop the image to keep upper left corner within 8000x8000
        with Image.open(io.BytesIO(screenshot_bytes)) as img:
            width, height = img.size
            crop_width = min(width, 8000)
            crop_height = min(height, 8000)
            # Crop from (0,0) to (crop_width, crop_height)
            img = img.crop((0, 0, crop_width, crop_height))
            output = io.BytesIO()
            img.save(output, format='PNG')
            screenshot_bytes = output.getvalue()

        screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
        image_data_url = f"data:image/png;base64,{screenshot_base64}"

        # Create messages for the chat model
        messages = [
            SystemMessage(
                content=f"""
                You are an AI model that detects list elements on a webpage and 
                outputs **always** in the correct pydantic format. If you are making up the output say so."""
            ),
            HumanMessage(content=[
                {"type": "text", "text": "Analyze the following webpage screenshot and text and return a list of distinct list items."},
                # {"type": "text", "text": f"{(await page.text_content())[:2000]}"},
                {
                    "type": "image_url", 
                    "image_url": {"url": image_data_url}
                }
            ])
        ]

        response = await model.ainvoke(messages)


        return response

    async def detect(self, page: Page) -> Optional[List[Locator]]:
        candidates = await self._get_candidates(page)
        
        # TODO: playwright get_by_text/bs4?/lowest common parent -> done
        
        return candidates