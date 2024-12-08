from contextlib import asynccontextmanager
from contextvars import ContextVar
from threading import Lock
from typing import Optional

from langchain_core.language_models import BaseLanguageModel

_llm_context: ContextVar[Optional[BaseLanguageModel]] = ContextVar("llm", default=None)


class LLMManager:
    _lock = Lock()
    _default_model: Optional[BaseLanguageModel] = None

    @classmethod
    def initialize(cls, model: BaseLanguageModel) -> None:
        """Initialize the default model"""
        with cls._lock:
            cls._default_model = model
            _llm_context.set(model)

    @classmethod
    def get_model(cls) -> BaseLanguageModel:
        """Get the current model or default if none set"""
        model = _llm_context.get()
        if model is None:
            if cls._default_model is None:
                raise ValueError("LLM not initialized. Call initialize() first.")
            model = cls._default_model
            _llm_context.set(model)
        return model

    @classmethod
    def reset(cls) -> None:
        """Reset the model (useful for testing)"""
        with cls._lock:
            cls._default_model = None
            _llm_context.set(None)

    @classmethod
    @asynccontextmanager
    async def use_model(cls, model: BaseLanguageModel):
        """Temporarily use a different model within this context"""
        token = _llm_context.set(model)
        try:
            yield model
        finally:
            _llm_context.reset(token)
