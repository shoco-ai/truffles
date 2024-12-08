from contextvars import ContextVar
from threading import Lock
from typing import Optional

from .base import ContextStore, Marker
from .exceptions import ContextError

_store_context: ContextVar[Optional[ContextStore]] = ContextVar("store", default=None)


class ContextManager:
    """
    Thread and task-safe context manager for store access.
    Uses contextvars for task isolation and threading.Lock for thread safety.
    """

    _lock = Lock()
    _default_store: Optional[ContextStore] = None

    @classmethod
    def initialize(cls, store: ContextStore) -> None:
        """Initialize the default store"""
        with cls._lock:
            cls._default_store = store
            _store_context.set(store)

    @classmethod
    def get_store(cls) -> ContextStore:
        """Get the current store or default if none set"""
        repo = _store_context.get()
        if repo is None:
            if cls._default_store is None:
                raise ContextError("Context store not initialized. Call initialize() first.")
            repo = cls._default_store
            _store_context.set(repo)
        return repo

    @classmethod
    async def get_marker(cls, page_state: str, action_name: str) -> Optional[Marker]:
        """Get selector from current store"""
        return await cls.get_store().get_marker(page_state, action_name)

    @classmethod
    async def store_marker(cls, page_state: str, action_name: str, marker: Marker) -> None:
        """Store selector in current store"""
        await cls.get_store().store_marker(page_state, action_name, marker)

    @classmethod
    async def remove_marker(cls, page_state: str, action_name: str, marker: Marker) -> None:
        """Remove selector from current store if it matches the provided marker"""
        await cls.get_store().remove_marker(page_state, action_name, marker)

    @classmethod
    def reset(cls) -> None:
        """Reset the store (useful for testing)"""
        with cls._lock:
            cls._default_store = None
            _store_context.set(None)
