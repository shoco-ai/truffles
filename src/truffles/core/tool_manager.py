from inspect import iscoroutinefunction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .enhanced import Enhanced


class ToolManager:
    """Manages tool instances and execution for Enhanced objects"""

    def __init__(self, enhanced_obj: "Enhanced"):
        self._enhanced = enhanced_obj
        self._tool_instances = {}

    def __getattr__(self, name: str):
        """Handle tool execution with proper async/sync handling"""
        tools = self._enhanced.get_tools()

        if name not in tools:
            raise AttributeError(f"No tool named '{name}' registered for {self._enhanced.__class__.__name__}")

        if name not in self._tool_instances:
            tool_class = tools[name]
            self._tool_instances[name] = tool_class(self._enhanced)

        tool_instance = self._tool_instances[name]

        if iscoroutinefunction(tool_instance.execute):

            async def tool_wrapper(*args, **kwargs):
                result = await tool_instance.execute(*args, **kwargs)
                return self._enhanced._wrap_result(result)

        else:

            def tool_wrapper(*args, **kwargs):
                result = tool_instance.execute(*args, **kwargs)
                return self._enhanced._wrap_result(result)

        return tool_wrapper

    def __dir__(self) -> list:
        """List available tools"""
        return list(self._enhanced.get_tools().keys())
