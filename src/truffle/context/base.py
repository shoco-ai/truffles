from typing import Optional, Protocol
from abc import ABC, abstractmethod

class ContextRepository(ABC):
    """Abstract base class for selector hash repository"""
    
    @abstractmethod
    async def get_marker(self, page_hash: str, action_name: str) -> Optional[str]:
        """Get selector for a given page hash and action"""
        pass
        
    @abstractmethod
    async def store_marker(self, page_hash: str, action_name: str, selector: str) -> None:
        """Store selector for a given page hash and action"""
        pass
        
    @abstractmethod
    async def remove_marker(self, page_hash: str, action_name: str) -> None:
        """Remove selector for a given page hash and action"""
        pass