from contextvars import ContextVar, Token
from typing import Optional
from langchain_core.language_models import BaseLanguageModel
from contextlib import asynccontextmanager


_llm_context: ContextVar[Optional[BaseLanguageModel]] = ContextVar("llm", default=None)


class LLMManager:
    _llm_context: ContextVar[Optional[BaseLanguageModel]] = ContextVar(
        "llm", default=None
    )

    @classmethod
    def initialize(cls, model: BaseLanguageModel) -> None:
        cls._llm_context.set(model)

    @classmethod
    def get_model(cls) -> BaseLanguageModel:
        model = cls._llm_context.get()
        if model is None:
            raise ValueError("LLM not initialized")
        return model

    @classmethod
    def set_model(cls, model: BaseLanguageModel) -> Token:
        """Manually set model and return token for reset"""
        return cls._llm_context.set(model)

    @classmethod
    def reset(cls, token: Token) -> None:
        """Reset context using token"""
        cls._llm_context.reset(token)

    @classmethod
    @asynccontextmanager
    async def use_model(cls, model: BaseLanguageModel):
        """Temporarily use a different model within this context"""
        token = cls.set_model(model)
        try:
            yield model
        finally:
            cls.reset(token)
