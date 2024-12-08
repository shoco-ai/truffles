from inspect import iscoroutinefunction
from typing import Any, Dict, Type, TypeVar

from ..tools.base import BaseTool
from .tool_manager import ToolManager

T = TypeVar("T", bound=BaseTool)


class Enhanced:
    """Base class that provides registry and delegation capabilities to wrapped objects"""

    _tool_registry: Dict[Type, Dict[str, Type[BaseTool]]] = {}

    def __init__(self, wrapped_obj: Any):
        self._wrapped = wrapped_obj
        # Create a tool manager specific to this instance's class
        self.tools = ToolManager(self)

    @classmethod
    def register_tool(cls, name: str):
        """Register a tool for this specific Enhanced subclass"""

        def decorator(tool_class: Type[T]) -> Type[T]:
            if not issubclass(tool_class, BaseTool):
                raise TypeError(f"{tool_class.__name__} must inherit from BaseTool")

            # Initialize registry for this class if it doesn't exist
            if cls not in cls._tool_registry:
                cls._tool_registry[cls] = {}

            if name in cls._tool_registry[cls]:
                raise ValueError(f"Tool {name} already registered for {cls.__name__}")

            cls._tool_registry[cls][name] = tool_class
            return tool_class

        return decorator

    def _wrap_result(self, result: Any) -> Any:
        """Override this method in subclasses to customize result wrapping"""
        return result

    def __getattr__(self, name: str):
        """Delegate undefined attributes to wrapped object"""
        output = getattr(self._wrapped, name)

        if iscoroutinefunction(output):

            async def wrapped(*args, **kwargs):
                result = await output(*args, **kwargs)
                return self._wrap_result(result)

            return wrapped

        elif callable(output):

            def wrapped(*args, **kwargs):
                result = output(*args, **kwargs)
                return self._wrap_result(result)

            return wrapped

        return self._wrap_result(output)

    def __dir__(self) -> list:
        return list(set(super().__dir__() + dir(self._wrapped)))

    @classmethod
    def get_tools(cls) -> Dict[str, Type[BaseTool]]:
        """Get all tools registered for this specific class"""
        return cls._tool_registry.get(cls, {})
