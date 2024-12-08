from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# TODO: improve this


class BaseTool(ABC):
    """
    Abstract base class for all tools that process content using LLM interactions.
    Tools can perform tasks like structure recognition, pagination detection, etc.
    """

    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base tool.

        Args:
            model_config: Optional configuration for the LLM model being used
        """
        self.model_config = model_config or {}

    @abstractmethod
    async def execute(self, content: Any, **kwargs) -> Any:
        """
        Execute the function on the given content.

        Args:
            content: The content to process
            **kwargs: Additional keyword arguments specific to the function

        Returns:
            The processed result
        """
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
