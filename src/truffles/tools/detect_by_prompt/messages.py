from langchain_core.messages import HumanMessage, SystemMessage


def get_prompt(node, prompt):
    messages = [
        SystemMessage(
            content="""You are an AI vision model that detects if the content matches the prompt query.
            You **always** use the correct pydantic format."""
        ),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "CONTENT: " + node["properties"]["text"] + "\n",
                },
                {"type": "text", "text": "PROMPT: " + prompt},
            ]
        ),
    ]

    return messages
