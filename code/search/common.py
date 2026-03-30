from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Protocol


class Problem(Protocol):
    def initial_state(self) -> Any: ...

    def is_goal(self, state: Any) -> bool: ...

    def successors(self, state: Any) -> Iterable[tuple[str, Any, float]]: ...

    def state_key(self, state: Any) -> Any: ...

    def heuristic(self, state: Any) -> float: ...


@dataclass(frozen=True)
class SearchResult:
    algorithm: str
    case: str
    success: bool
    nodes_expanded: int
    time_ms: int
    path_cost: float
    path_len: int
    max_frontier: int
    action_path: list[str]

    def to_row(self) -> dict[str, Any]:
        row = {
            "case": self.case,
            "algorithm": self.algorithm,
            "success": self.success,
            "nodes_expanded": self.nodes_expanded,
            "time_ms": self.time_ms,
            "path_cost": self.path_cost,
            "path_len": self.path_len,
            "max_frontier": self.max_frontier,
        }
        return row

    def to_pretty_text(self) -> str:
        lines = [
            f"case={self.case}",
            f"algorithm={self.algorithm}",
            f"success={self.success}",
            f"nodes_expanded={self.nodes_expanded}",
            f"time_ms={self.time_ms}",
            f"path_cost={self.path_cost}",
            f"path_len={self.path_len}",
            f"max_frontier={self.max_frontier}",
        ]
        if self.action_path:
            lines.append("actions=" + " -> ".join(self.action_path))
        return "\n".join(lines)


@dataclass
class Node:
    state: Any
    parent: "Node | None"
    action: str | None
    g: float
    h: float

    @property
    def f(self) -> float:
        return self.g + self.h

    def iter_actions(self) -> list[str]:
        actions: list[str] = []
        n: Node | None = self
        while n is not None and n.action is not None:
            actions.append(n.action)
            n = n.parent
        actions.reverse()
        return actions
