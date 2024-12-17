import base64

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from truffles.enhanced.locator import TLocator
from truffles.models import DefaultModel


class TrufflesAssertionError(Exception):
    pass


def expect(locator: TLocator):
    return TrufflesLocatorAssertions(locator)


def get_prompt(component_text, sc_bytes, prompt):
    sc_base64 = base64.b64encode(sc_bytes).decode()

    image_data_url = f"data:image/png;base64,{sc_base64}"

    messages = [
        SystemMessage(
            content="""You are an AI model that gets web pages or parts of web pages and decide whether the input property is fulfilled.
            You **always** use the correct pydantic format."""
        ),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "component text: " + component_text,
                },
                {"type": "image_url", "image_url": {"url": image_data_url}},
                {"type": "text", "text": f"PROPERTY TO BE CHECKED: {prompt}"},
            ]
        ),
    ]

    return messages


class TrufflesLocatorAssertions:
    def __init__(self, locator: TLocator):
        self._t_locator = locator

    async def to_have_property(self, prompt: str):
        sc_bytes = await self._t_locator.screenshot()

        with open("assert_loc_screenshot.png", "wb") as f:
            f.write(sc_bytes)

        sc_text = await self._t_locator.text_content()

        class Assertion(BaseModel):
            is_fulfilled: bool = Field(description="Whether the property is fulfilled")
            reason: str = Field(description="Reason for your decision. Up to 10 words.")

        model = DefaultModel.get_model()
        model = model.with_structured_output(Assertion).with_retry()

        model_output = await model.ainvoke(get_prompt(sc_text, sc_bytes, prompt))

        if not hasattr(model_output, "is_fulfilled"):
            raise Exception(f"Assertion failed: {model_output.json()}")

        if not model_output.is_fulfilled:
            raise TrufflesAssertionError(f"Assertion failed: {model_output.reason}")

        return model_output.json()
