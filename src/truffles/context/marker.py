from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


class Marker(ABC):
    """Abstract base class for markers that can be used to locate elements"""

    @abstractmethod
    def to_dict(self) -> Dict:
        """Convert marker to dictionary for serialization"""
        pass

    @abstractmethod
    def from_dict(cls, data: Dict) -> "Marker":
        """Create marker from dictionary"""
        pass

    @abstractmethod
    def get_selector(self) -> str:
        """Get the selector string for this marker"""
        pass


@dataclass
class SimpleMarker(Marker):
    """Simple marker that stores a single selector string"""

    selector: str
    selector_type: str = "css"  # can be "css" or "xpath"

    def to_dict(self) -> Dict:
        return {
            "type": "simple",
            "selector": self.selector,
            "selector_type": self.selector_type,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SimpleMarker":
        return cls(selector=data["selector"], selector_type=data["selector_type"])

    def get_selector(self) -> str:
        return self.selector


@dataclass
class AttributeMarker(Marker):
    """Marker that uses attribute matching"""

    attribute_dict: Dict[str, str]
    match_mode: str = "contains"  # can be "exact" or "contains"

    def to_dict(self) -> Dict:
        return {
            "type": "attribute",
            "attribute_dict": self.attribute_dict,
            "match_mode": self.match_mode,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AttributeMarker":
        return cls(attribute_dict=data["attribute_dict"], match_mode=data["match_mode"])

    def get_selector(self) -> str:
        if self.match_mode == "exact":
            return " and ".join([f'[{key}="{value}"]' for key, value in self.attribute_dict.items()])
        elif self.match_mode == "contains":
            return " and ".join([f'[{key}~="{value}"]' for key, value in self.attribute_dict.items()])
        else:
            raise ValueError(f"Invalid match mode: {self.match_mode}")
