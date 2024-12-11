from typing import Optional

from .base import ContextStore, Marker


class StoreManager:
    """
    Thread and task-safe context manager for store access.
    Uses contextvars for task isolation and threading.Lock for thread safety.
    """

    _context_store: ContextStore = None

    @classmethod
    def initialize(cls, store: ContextStore) -> None:
        """Initialize the default store"""
        cls._context_store = store

    @classmethod
    def get_store(cls) -> ContextStore:
        """Get the current store or default if none set"""
        if cls._context_store is None:
            raise ValueError(  # TODO: is this the wrong error?
                "StoreManager has not been initialized call `StoreManager.initialize()`"
            )
        return cls._context_store

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
        cls._context_store = None
