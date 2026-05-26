"""
core/orchestration/tool_planner.py

WHY THIS IS A SEPARATE LAYER:
  In the old architecture, tool execution was mixed into the router.
  The router returned strings like "browser_request" or "file_operation"
  which were then handled... somewhere. This meant:

  1. No separation between "which model" and "which tool"
  2. Tool + reasoning requests were impossible to express
  3. Adding a new tool type required editing router logic

  ToolPlanner is now a dedicated layer that:
  - Reads tool_type from RouteDecision
  - Dispatches to the right tool executor
  - Returns a ToolResult that can be injected into the model's context
  - Is completely independent of model selection

  This means:
  - DeepSeek can receive browser results as context (reasoning + tools)
  - Qwen can receive file operation confirmations (tools only)
  - New tools are added here, not in the router

EXTENSION POINTS:
  Adding a new tool:
  1. Add its pattern to CognitionAssessor._tool_patterns
  2. Add its executor here in ToolPlanner._executors
  3. Add tool_type to the Literal in signal.py
  That's it. Router and classifier don't need changes.
"""

from dataclasses import dataclass
from typing import Optional, Callable, Any


@dataclass
class ToolResult:
    """
    Result of a tool execution, to be injected into model context.
    """
    success: bool
    tool_type: str
    output: Optional[str] = None
    error: Optional[str] = None

    def to_context_string(self) -> str:
        if self.success:
            return f"[Tool: {self.tool_type}]\n{self.output}"
        return f"[Tool: {self.tool_type} FAILED]\n{self.error}"


class ToolPlanner:
    """
    Dispatches tool execution based on tool_type.
    Completely independent of model selection logic.
    """

    def __init__(self):
        # Registry pattern: tool_type → executor callable
        # Add new tools here without touching router or classifier
        self._executors: dict[str, Callable] = {
            "browser": self._execute_browser,
            "file_system": self._execute_file_system,
            "terminal": self._execute_terminal,
            "code_execution": self._execute_code,
            "memory_retrieval": self._execute_memory_retrieval,
        }

    def execute(self, tool_type: Optional[str], message: str) -> Optional[ToolResult]:
        """
        Executes the appropriate tool for a given tool_type.
        Returns None if no tool is needed or tool_type is unknown.
        """
        if not tool_type:
            return None

        executor = self._executors.get(tool_type)

        if not executor:
            return ToolResult(
                success=False,
                tool_type=tool_type or "unknown",
                error=f"No executor registered for tool_type='{tool_type}'",
            )

        try:
            return executor(message)
        except Exception as e:
            return ToolResult(
                success=False,
                tool_type=tool_type,
                error=str(e),
            )

    # ── Tool executors (stub implementations — replace with real integrations) ─

    def _execute_browser(self, message: str) -> ToolResult:
        """
        Execute browser/web search tool.
        Replace with your actual browser integration.
        """
        # TODO: integrate with your browser agent
        return ToolResult(
            success=False,
            tool_type="browser",
            error="Browser tool not yet integrated",
        )

    def _execute_file_system(self, message: str) -> ToolResult:
        """
        Execute file system operations.
        Replace with your actual file system tool.
        """
        # TODO: integrate with your file system agent
        return ToolResult(
            success=False,
            tool_type="file_system",
            error="File system tool not yet integrated",
        )

    def _execute_terminal(self, message: str) -> ToolResult:
        """
        Execute terminal/shell commands.
        Replace with your actual terminal integration.
        """
        # TODO: integrate with your terminal agent
        return ToolResult(
            success=False,
            tool_type="terminal",
            error="Terminal tool not yet integrated",
        )

    def _execute_code(self, message: str) -> ToolResult:
        """
        Execute code compilation/running.
        """
        return ToolResult(
            success=False,
            tool_type="code_execution",
            error="Code execution tool not yet integrated",
        )

    def _execute_memory_retrieval(self, message: str) -> ToolResult:
        """
        Retrieve from long-term memory store.
        """
        return ToolResult(
            success=False,
            tool_type="memory_retrieval",
            error="Memory retrieval tool not yet integrated",
        )