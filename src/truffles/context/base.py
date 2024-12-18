import hashlib
from abc import ABC, abstractmethod
from typing import Optional

from truffles.context.marker import Marker


class ContextStore(ABC):
    """Abstract base class for selector hash store"""

    def _process_page_state(self, page_state: str) -> str:
        """Process the page state to generate a key"""
        # For now, hash the page state
        return hashlib.sha256(page_state.encode("utf-8")).hexdigest()

    @abstractmethod
    async def get_marker(self, page_state: str, action_name: str, marker_id: Optional[str] = None) -> Optional[Marker]:
        """Get marker for a given page hash and action"""
        pass

    @abstractmethod
    async def store_marker(
        self,
        page_state: str,
        action_name: str,
        marker: Marker,
        marker_id: Optional[str] = None,
    ) -> None:
        """Store marker for a given page hash and action"""
        pass

    @abstractmethod
    async def remove_marker(
        self,
        page_state: str,
        action_name: str,
        marker: Marker,
        marker_id: Optional[str] = None,
    ) -> None:
        """Remove marker for a given page hash and action if it matches the provided marker"""
        pass
