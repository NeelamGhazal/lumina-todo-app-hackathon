# Task T012: Tool Registry
"""MCP Tool Registry and Registration System.

Provides a centralized registry for MCP tools with:
- Tool registration via decorator
- Tool lookup by name
- Tool listing for /mcp/tools endpoint

References:
- spec.md: FR-001 (5 MCP tools), FR-002 (MCP protocol)
- plan.md: Tool registration architecture
"""

from typing import Any, Callable, TypeVar

from pydantic import BaseModel

# Type for tool handler functions
ToolHandler = Callable[..., Any]
T = TypeVar("T", bound=BaseModel)


class ToolDefinition:
    """Definition of an MCP tool.

    Stores metadata and handler for a registered tool.
    """

    def __init__(
        self,
        name: str,
        description: str,
        handler: ToolHandler,
        params_model: type[BaseModel],
    ):
        """Initialize tool definition.

        Args:
            name: Tool identifier (e.g., "add_task")
            description: Human-readable description for agents
            handler: Async function that executes the tool
            params_model: Pydantic model for parameter validation
        """
        self.name = name
        self.description = description
        self.handler = handler
        self.params_model = params_model

    def to_dict(self) -> dict[str, Any]:
        """Convert to MCP tool definition format.

        Returns dict suitable for /mcp/tools response.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.params_model.model_json_schema(),
        }


class ToolRegistry:
    """Registry for MCP tools.

    Singleton-like registry that stores all registered tools.
    Tools are registered via the @register_tool decorator.
    """

    _instance: "ToolRegistry | None" = None
    _tools: dict[str, ToolDefinition]

    def __new__(cls) -> "ToolRegistry":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    def register(
        self,
        name: str,
        description: str,
        params_model: type[BaseModel],
    ) -> Callable[[ToolHandler], ToolHandler]:
        """Decorator to register a tool handler.

        Usage:
            @registry.register(
                name="add_task",
                description="Create a new task",
                params_model=AddTaskParams,
            )
            async def add_task(params: AddTaskParams, db: AsyncSession) -> dict:
                ...

        Args:
            name: Tool identifier
            description: Human-readable description
            params_model: Pydantic model for validation

        Returns:
            Decorator function
        """

        def decorator(handler: ToolHandler) -> ToolHandler:
            self._tools[name] = ToolDefinition(
                name=name,
                description=description,
                handler=handler,
                params_model=params_model,
            )
            return handler

        return decorator

    def get(self, name: str) -> ToolDefinition | None:
        """Get a tool by name.

        Args:
            name: Tool identifier

        Returns:
            ToolDefinition or None if not found
        """
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools.

        Returns:
            List of tool definitions for /mcp/tools response
        """
        return [tool.to_dict() for tool in self._tools.values()]

    def get_all(self) -> dict[str, ToolDefinition]:
        """Get all registered tools.

        Returns:
            Dictionary of name -> ToolDefinition
        """
        return self._tools.copy()

    def clear(self) -> None:
        """Clear all registered tools (for testing)."""
        self._tools.clear()


# Global registry instance
registry = ToolRegistry()


def register_tool(
    name: str,
    description: str,
    params_model: type[BaseModel],
) -> Callable[[ToolHandler], ToolHandler]:
    """Convenience decorator for tool registration.

    Usage:
        @register_tool(
            name="add_task",
            description="Create a new task for the user",
            params_model=AddTaskParams,
        )
        async def add_task(params: AddTaskParams, db: AsyncSession) -> dict:
            ...

    Args:
        name: Tool identifier (e.g., "add_task")
        description: Human-readable description for AI agents
        params_model: Pydantic model for parameter validation

    Returns:
        Decorator function
    """
    return registry.register(name, description, params_model)


# Export public API
__all__ = [
    "ToolDefinition",
    "ToolRegistry",
    "registry",
    "register_tool",
]
