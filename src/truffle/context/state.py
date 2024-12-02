from contextvars import ContextVar
from typing import Optional
from threading import Lock
from .base import ContextRepository
from .exceptions import ContextError

_repository_context: ContextVar[Optional[ContextRepository]] = ContextVar('repository', default=None)

class ContextManager:
    """
    Thread and task-safe context manager for repository access.
    Uses contextvars for task isolation and threading.Lock for thread safety.
    """
    _lock = Lock()
    _default_repository: Optional[ContextRepository] = None
    
    @classmethod
    def initialize(cls, repository: ContextRepository) -> None:
        """Initialize the default repository"""
        with cls._lock:
            cls._default_repository = repository
            _repository_context.set(repository)
    
    @classmethod
    def get_repository(cls) -> ContextRepository:
        """Get the current repository or default if none set"""
        repo = _repository_context.get()
        if repo is None:
            if cls._default_repository is None:
                raise ContextError("Context repository not initialized. Call initialize() first.")
            repo = cls._default_repository
            _repository_context.set(repo)
        return repo
    
    @classmethod
    async def get_marker(cls, page_hash: str, action_name: str) -> Optional[str]:
        """Get selector from current repository"""
        return await cls.get_repository().get_selector(page_hash, action_name)
    
    @classmethod
    async def store_marker(cls, page_hash: str, action_name: str, selector: str) -> None:
        """Store selector in current repository"""
        await cls.get_repository().store_selector(page_hash, action_name, selector)
    
    @classmethod
    async def remove_marker(cls, page_hash: str, action_name: str) -> None:
        """Remove selector from current repository"""
        await cls.get_repository().remove_selector(page_hash, action_name)
    
    @classmethod
    def reset(cls) -> None:
        """Reset the repository (useful for testing)"""
        with cls._lock:
            cls._default_repository = None
            _repository_context.set(None)