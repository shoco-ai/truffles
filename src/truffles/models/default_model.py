from typing import Optional

from langchain_core.language_models import BaseLanguageModel


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

    # TODO: add function class "use model of type X" like small, small w vision, etc.
    # and then you can either add all needed open-source API keys, or set your own
    # model use strings.
