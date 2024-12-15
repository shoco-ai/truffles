from typing import List

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage


def struct_locator_message(element_text: str, links: List[str]) -> List[BaseMessage]:
    messages = [
        SystemMessage(
            content="""You are an AI model that converts the visible text on a webpage to structured data.
            You **always** use the correct pydantic format."""
        ),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Links: [" + "\n".join(links) + "\n]",
                },
                {
                    "type": "text",
                    "text": element_text,
                },
            ]
        ),
    ]

    # if prompt:
    #     messages.append(HumanMessage(content=f"Additional instructions: {prompt}"))

    return messages
