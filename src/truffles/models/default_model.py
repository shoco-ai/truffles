from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI

# LangchainGoogleGenAI has a bug with the structured output (even the cursor autocomplete knows it)
# from langchain_google_genai import ChatGoogleGenerativeAI


MODEL_SIZES = ["small", "standard", "large"]

# OpenAI model mapping
OPENAI_MODELS = {
    "small": "gpt-4o-mini",
    "standard": "gpt-4o",
    "large": "o1-preview",
}

# Anthropic model mapping
ANTHROPIC_MODELS = {
    "small": "claude-3-5-haiku-latest",
    "standard": "claude-3-5-sonnet-latest",
    "large": "claude-3-opus-20240229",
}

# GOOGLE_MODELS = {
#     "small": "gemini-1.5-flash-8b",
#     "standard": "gemini-1.5-flash",
#     "large": "gemini-1.5-pro",
# }


class DefaultModel:
    _default_model: Optional[BaseLanguageModel] = None

    @classmethod
    def initialize(cls, model: BaseLanguageModel):
        cls._default_model = model

    @classmethod
    def get_model(cls):
        if cls._default_model is None:
            raise ValueError("The default model is not set, call: DefaultModel.initialize()")
        return cls._default_model

    @classmethod
    def reset(cls):
        cls._default_model = None

    @classmethod
    def get_specific_model(cls, model_size: str = "standard"):
        if model_size not in MODEL_SIZES:
            raise ValueError(f"Model size must be one of: {MODEL_SIZES}")

        current_model = cls.get_model()

        # Detect if current model is Anthropic
        if isinstance(current_model, ChatAnthropic):
            return ChatAnthropic(model=ANTHROPIC_MODELS[model_size])

        # Detect if current model is OpenAI
        if isinstance(current_model, ChatOpenAI):
            return ChatOpenAI(model=OPENAI_MODELS[model_size])

        # # Detect if current model is Google
        # if isinstance(current_model, ChatGoogleGenerativeAI):
        #     return ChatGoogleGenerativeAI(model=GOOGLE_MODELS[model_size])

        raise ValueError("Unsupported model type. Only OpenAI and Anthropic models are supported.")
