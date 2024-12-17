from langchain_core.messages import HumanMessage, SystemMessage

from truffles.utils.ax_tree.generate import get_node_text


def get_prompt(node, prompt):
    messages = [
        SystemMessage(
            content="""You are an AI model that detects if the text of web elements in the passed content matches the prompt.
            You **always** use the correct pydantic format."""
        ),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "CONTENT: " + get_node_text(node) + "\n",
                },
                {"type": "text", "text": "PROMPT: " + prompt},
            ]
        ),
    ]

    return messages
