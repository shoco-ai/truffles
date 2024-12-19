import json
from typing import Dict, Optional

from truffles.context.base import ContextStore
from truffles.context.exceptions import ContextError
from truffles.context.marker import AttributeMarker, Marker, SimpleMarker


class MemoryContextStore(ContextStore):
    """In-memory implementation of context store"""

    def __init__(self):
        self._store: Dict[str, Dict[str, Dict]] = {}
        self._manual_id_store: Dict[str, Dict[str, Dict]] = {}

    async def get_marker(self, page_state: str, action_name: str, marker_id: Optional[str] = None) -> Optional[Marker]:
        """Get marker for a given page state and action"""

        marker_data = None

        if marker_id:
            marker_data = self._manual_id_store.get(marker_id, None)

        if not marker_data:  # not found so far, check the big page state
            page_hash = self._process_page_state(page_state)
            if page_hash not in self._store:
                return None

            marker_data = self._store[page_hash].get(action_name)
            if not marker_data:
                return None

            # store it for next time, since it was requested and not found
            if marker_id:
                self._manual_id_store[marker_id] = marker_data

        # Create appropriate marker type based on stored data
        marker_type = marker_data["type"]
        if marker_type == "simple":
            return SimpleMarker.from_dict(marker_data)
        elif marker_type == "attribute":
            return AttributeMarker.from_dict(marker_data)
        else:
            raise ContextError(f"Unknown marker type: {marker_type}")

    async def store_marker(
        self,
        page_state: str,
        action_name: str,
        marker: Marker,
        marker_id: Optional[str] = None,
    ) -> None:
        """Store marker for a given page state and action"""
        page_hash = self._process_page_state(page_state)
        if page_hash not in self._store:
            self._store[page_hash] = {}

        self._store[page_hash][action_name] = marker.to_dict()
        if marker_id:
            self._manual_id_store[marker_id] = marker.to_dict()

    async def remove_marker(
        self,
        page_state: str,
        action_name: str,
        marker: Marker,
        marker_id: Optional[str] = None,
    ) -> None:
        """Remove marker for a given page state and action if it matches the provided marker"""
        page_hash = self._process_page_state(page_state)
        if page_hash in self._store and action_name in self._store[page_hash]:
            stored_marker_data = self._store[page_hash][action_name]
            stored_marker = Marker.from_dict(stored_marker_data)
            if stored_marker == marker:
                del self._store[page_hash][action_name]

        if marker_id:
            del self._manual_id_store[marker_id]

    def to_json(self) -> str:
        """Convert store to JSON string"""
        return json.dumps({"memory_store": self._store, "manual_id_store": self._manual_id_store})

    @classmethod
    def from_json(cls, json_str: str) -> "MemoryContextStore":
        """Create store from JSON string"""
        store = cls()
        store._store = json.loads(json_str)["memory_store"]
        store._manual_id_store = json.loads(json_str)["manual_id_store"]
        return store
