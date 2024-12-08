import base64
import io
import os
from collections import Counter
from typing import Callable, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup, Tag
from langchain_core.messages import HumanMessage, SystemMessage
from PIL import Image
from playwright.async_api import Locator, Page
from pydantic import BaseModel, Field

from truffles.context import AttributeMarker
from truffles.models.config import LLMManager

from ..utils import (
    count_tags_in_soup,
    find_elements_with_text,
    find_lowest_common_ancestor,
    get_attr_list,
)
from .base import ListDetectionStrategy


class DetectionOutput(BaseModel):
    selector: str = Field(
        description="A substring present in a list element in the texts language that can be used to CTRL+F the element."
    )
    # confidence: float = Field(description="Confidence score between 0 and 1")


class ListDetectionOutput(BaseModel):
    items: List[DetectionOutput]  # = Field(description="A list of detected items (this wraps the output)")


def find_candidate_elements(soup: BeautifulSoup, identifiers: List[dict]) -> List[Tuple[Tag, str]]:
    """Find all elements matching the given identifiers"""
    candidates = []
    for identifier in identifiers:
        elements = find_elements_with_text(soup, identifier.selector)
        if elements:
            candidates.extend(elements)
    return list(set(candidates))


def analyze_common_ancestors(element_candidates: List[Tuple[Tag, str]], attr_extractor: Callable) -> List[str]:
    """Analyze common ancestors of candidate elements and extract attributes"""
    attrs = []
    for el1, _ in element_candidates:
        for el2, _ in element_candidates:
            common_ancestor = find_lowest_common_ancestor(el1, el2)
            if isinstance(common_ancestor, Tag):
                attrs.extend(attr_extractor(common_ancestor))
    return attrs


def calculate_normalized_counts(attr_counts: Counter, total_tags: Counter) -> Dict[str, float]:
    """Calculate normalized counts for attributes"""
    normalized_counts = {}
    for attr, count in attr_counts.items():
        if total_tags[attr] > 0:
            normalized_counts[attr] = count / total_tags[attr]
    return normalized_counts


class LLMStrategy(ListDetectionStrategy):
    """
    Strategy that uses an LLM to detect list elements.
    """

    async def _get_candidates(self, page: Page) -> Optional[List[Locator]]:
        """AI-powered detection using LLM"""

        # Initialize the model with structured output
        model = LLMManager.get_model().with_structured_output(ListDetectionOutput, include_raw=False)
        model = model.with_retry(
            retry_if_exception_type=(ValueError,),
            stop_after_attempt=2,
            wait_exponential_jitter=True,
        )

        # Take a screenshot of the full page
        screenshot_bytes = await page.screenshot(full_page=True)  # Add logging to confirm save

        # Crop the image to keep upper left corner within 8000x8000
        with Image.open(io.BytesIO(screenshot_bytes)) as img:
            width, height = img.size
            crop_width = min(width, 2 * height)
            crop_height = min(height, 2 * width)
            # Crop from (0,0) to (crop_width, crop_height)
            img = img.crop((0, 0, crop_width, crop_height))

            output = io.BytesIO()
            img.save(output, format="PNG")
            screenshot_bytes = output.getvalue()

            # Save cropped image for debugging
            os.makedirs("./tmp", exist_ok=True)
            img.save("./tmp/cropped_screenshot.png")

        screenshot_base64 = base64.b64encode(screenshot_bytes).decode()

        image_data_url = f"data:image/png;base64,{screenshot_base64}"

        # Create messages for the chat model
        messages = [
            SystemMessage(
                content="""You are an AI model that detects list elements on a webpage and
                outputs **always** in the correct pydantic format. If you are making up the output say so."""
            ),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Analyze the following webpage screenshot and text and return a list of distinct list items.",
                    },
                    # TODO: add text
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ]
            ),
        ]

        response = await model.ainvoke(messages)  # for debugging set `include_raw = True`
        return response

    async def _string_to_wrap_selectors(
        self,
        page: Page,
        list_element_candidates: List[str],
        use_attr_keys: bool = False,
    ) -> List[Locator]:
        """Get list candidates from a string of HTML"""

        soup_list = [BeautifulSoup(await fr.content(), "html.parser") for fr in page.frames]
        overall_counts = {}

        for soup in soup_list:
            # Find candidate elements
            element_candidates = find_candidate_elements(soup, list_element_candidates)

            # Analyze common ancestors and get attributes
            # TODO: This is a bit of a hack, implement a better way
            possible_attrs = analyze_common_ancestors(element_candidates, get_attr_list)

            # Count and normalize attributes
            attr_counts = Counter(possible_attrs)
            total_tags = count_tags_in_soup(soup)
            normalized_counts = calculate_normalized_counts(attr_counts, total_tags)

            overall_counts.update(normalized_counts)

        return overall_counts

    async def detect(self, page: Page) -> Optional[List[Locator]]:
        string_candidates = await self._get_candidates(page)

        wrapper_value_candidates = await self._string_to_wrap_selectors(
            page, string_candidates.items, use_attr_keys=False
        )

        if not wrapper_value_candidates:
            return None

        best_wrapper_attribute = max(wrapper_value_candidates, key=wrapper_value_candidates.get)

        marker = AttributeMarker(
            attribute_dict={best_wrapper_attribute[0]: best_wrapper_attribute[1]},
            match_mode="contains",
        )

        return marker
