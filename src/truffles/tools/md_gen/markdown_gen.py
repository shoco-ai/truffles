import asyncio
import json
import os

import requests
from playwright.async_api import Page

from truffles.enhanced.page import TPage
from truffles.tools.base import BaseTool
from truffles.tools.md_gen.exceptions import (
    MarkdownGenKeyException,
    MarkdownGenResponseException,
)


@TPage.register_tool("to_markdown")
class MarkdownGen(BaseTool):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page

    async def execute(self, timeout: int = 10) -> str:
        """Execute the markdown generation.

        Returns:
            str: The complete markdown document
        """
        try:
            api_key = os.getenv("HTML_TO_MARKDOWN_API_KEY")
            if not api_key:
                raise MarkdownGenKeyException("HTML_TO_MARKDOWN_API_KEY is not set")
        except Exception:
            raise MarkdownGenKeyException(
                "HTML_TO_MARKDOWN_API_KEY is not set. This version uses the API offered by https://html-to-markdown.com/. You can get a free API key at https://html-to-markdown.com/api."
            )

        html_contents = [(await fr.content()) for fr in self.page.frames]
        markdown_results = []

        for html in html_contents:
            try:
                response = requests.post(
                    "https://api.html-to-markdown.com/v1/convert",
                    headers={
                        "X-API-Key": api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "html": html,
                        "domain": self.page.url,
                    },
                    timeout=timeout,
                )
            except requests.exceptions.Timeout:
                raise MarkdownGenResponseException("Failed to convert HTML to Markdown. Timeout.")
            if not response.ok:
                raise MarkdownGenResponseException(f"Failed to convert HTML to Markdown: {response.json()}")

            try:
                response_data = response.json()
                markdown_results.append(response_data["markdown"])
            except (json.JSONDecodeError, KeyError) as e:
                raise MarkdownGenResponseException(f"Failed to parse markdown response: {e}")

            await asyncio.sleep(0.5)  # give the server a sec to breathe

        # Combine all markdown results with double newlines between them
        return "\n\n".join(markdown_results)
