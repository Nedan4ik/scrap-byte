from __future__ import annotations
from typing import Any


class ExecutionResult:
    def __init__(
        self,
        success: bool = True,
        output: str = "",
        error: str | None = None,
        result: Any = None,
    ):
        self.success = success
        self.output = output
        self.error = error
        self.result = result

    def __bool__(self) -> bool:
        return self.success

    def __repr__(self) -> str:
        status = "OK" if self.success else f"ERROR: {self.error}"
        return f"<ExecutionResult {status} output={repr(self.output)}>"
