from abc import ABC, abstractmethod
from typing import Any


class BaseTask(ABC):
    """
    Abstract base class for all tasks that can be executed.
    Tasks represent higher-level operations that may involve multiple tool interactions.
    """

    def __init__(self):
        """
        Initialize the base task.

        Args:
            config: Optional configuration for the task
        """
        return

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """
        Execute the task with the given parameters.

        Args:
            **kwargs: Additional keyword arguments specific to the task

        Returns:
            The task execution result
        """
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"
