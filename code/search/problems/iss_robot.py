from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


def base_iss_map() -> dict[str, list[str]]:
    return {
        "Storage_PMM": ["Node_3"],
        "Node_3": ["Storage_PMM", "Observatory", "Node_2"],
        "Observatory": ["Node_3"],
        "Node_2": ["Node_3", "US_Lab", "Airlock"],
        "US_Lab": ["Node_2"],
        "Airlock": ["Node_2"],
    }


def base_move_cost(a: str, b: str) -> float:
    if (a, b) in {("Node_2", "Airlock"), ("Airlock", "Node_2")}:
        return 2.0
    return 1.0


@dataclass(frozen=True)
class ISSState:
    robot_loc: str
    new_filter_loc: str  # Storage_PMM / US_Lab / Node_2 / Node_3 / Airlock / Observatory / carried
    old_filter_loc: str  # US_Lab / Storage_PMM / carried
    toolbox_loc: str  # Storage_PMM / US_Lab / carried
    old_filter_removed: bool
    new_filter_installed: bool


def _carried_item(state: ISSState) -> str | None:
    # Only one object may be carried at a time (toolbox/filter/old filter).
    for name, loc in (
        ("new_filter", state.new_filter_loc),
        ("old_filter", state.old_filter_loc),
        ("toolbox", state.toolbox_loc),
    ):
        if loc == "carried":
            return name
    return None


def _set_loc(state: ISSState, obj: str, loc: str) -> ISSState:
    if obj == "new_filter":
        return ISSState(state.robot_loc, loc, state.old_filter_loc, state.toolbox_loc, state.old_filter_removed, state.new_filter_installed)
    if obj == "old_filter":
        return ISSState(state.robot_loc, state.new_filter_loc, loc, state.toolbox_loc, state.old_filter_removed, state.new_filter_installed)
    if obj == "toolbox":
        return ISSState(state.robot_loc, state.new_filter_loc, state.old_filter_loc, loc, state.old_filter_removed, state.new_filter_installed)
    raise ValueError(obj)


def _move_robot(state: ISSState, to_room: str) -> ISSState:
    return ISSState(to_room, state.new_filter_loc, state.old_filter_loc, state.toolbox_loc, state.old_filter_removed, state.new_filter_installed)


def _shortest_paths(iss_map: dict[str, list[str]]) -> dict[tuple[str, str], float]:
    # Dijkstra from every node (small graph; simpler than precomputing with Floyd).
    import heapq

    dist_all: dict[tuple[str, str], float] = {}
    nodes = list(iss_map.keys())
    for src in nodes:
        dist: dict[str, float] = {src: 0.0}
        heap: list[tuple[float, str]] = [(0.0, src)]
        while heap:
            d, u = heapq.heappop(heap)
            if d != dist.get(u, d):
                continue
            for v in iss_map[u]:
                nd = d + base_move_cost(u, v)
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v))
        for dst, d in dist.items():
            dist_all[(src, dst)] = d
    return dist_all


class ISSRobotProblem:
    def __init__(
        self,
        *,
        iss_map: dict[str, list[str]],
        start_state: ISSState,
        goal_robot_loc: str = "Observatory",
        require_toolbox_returned: bool = True,
    ) -> None:
        self._map = iss_map
        self._start = start_state
        self._goal_robot_loc = goal_robot_loc
        self._require_toolbox_returned = require_toolbox_returned
        self._dist = _shortest_paths(iss_map)

    def initial_state(self) -> ISSState:
        return self._start

    def is_goal(self, state: ISSState) -> bool:
        if not state.new_filter_installed:
            return False
        if state.robot_loc != self._goal_robot_loc:
            return False
        if self._require_toolbox_returned and state.toolbox_loc != "Storage_PMM":
            return False
        return True

    def state_key(self, state: ISSState) -> Any:
        return state

    def heuristic(self, state: ISSState) -> float:
        # Waypoint heuristic: sum shortest-path distances through remaining mandatory rooms (relaxed constraints).
        def d(a: str, b: str) -> float:
            return self._dist.get((a, b), float("inf"))

        W: list[str] = []
        if not state.old_filter_removed:
            if state.toolbox_loc != "carried" and state.toolbox_loc != state.robot_loc:
                W.append(state.toolbox_loc)
            W.append("US_Lab")
        elif state.old_filter_loc != "Storage_PMM":
            W.append("Storage_PMM")
        elif not state.new_filter_installed:
            if state.new_filter_loc != "carried" and state.new_filter_loc != state.robot_loc:
                W.append(state.new_filter_loc)
            W.append("US_Lab")
        elif state.toolbox_loc != "Storage_PMM":
            W.append("Storage_PMM")

        if state.robot_loc != self._goal_robot_loc:
            W.append(self._goal_robot_loc)

        if not W:
            return 0.0

        total = d(state.robot_loc, W[0])
        for i in range(len(W) - 1):
            total += d(W[i], W[i + 1])
        return total

    def successors(self, state: ISSState) -> Iterable[tuple[str, ISSState, float]]:
        # Moves
        for to_room in self._map[state.robot_loc]:
            yield (f"Move({to_room})", _move_robot(state, to_room), base_move_cost(state.robot_loc, to_room))

        carried = _carried_item(state)

        # Pick actions
        if carried is None:
            for obj, loc in (
                ("toolbox", state.toolbox_loc),
                ("new_filter", state.new_filter_loc),
                ("old_filter", state.old_filter_loc),
            ):
                if loc == state.robot_loc:
                    nxt = _set_loc(state, obj, "carried")
                    yield (f"Pick({obj})", nxt, 0.0)

        # Drop actions
        if carried is not None:
            obj = carried
            nxt = _set_loc(state, obj, state.robot_loc)
            yield (f"Drop({obj})", nxt, 0.0)

        # US_Lab actions
        if state.robot_loc == "US_Lab":
            toolbox_present = state.toolbox_loc in {"carried", "US_Lab"}
            if toolbox_present and (not state.old_filter_removed) and state.old_filter_loc == "US_Lab":
                # Removal doesn't automatically pick the old filter (keeps carry constraint simple).
                yield (
                    "Remove_Old_Filter",
                    ISSState(
                        robot_loc=state.robot_loc,
                        new_filter_loc=state.new_filter_loc,
                        old_filter_loc=state.old_filter_loc,
                        toolbox_loc=state.toolbox_loc,
                        old_filter_removed=True,
                        new_filter_installed=state.new_filter_installed,
                    ),
                    0.0,
                )

            if toolbox_present and state.old_filter_removed and (not state.new_filter_installed) and state.new_filter_loc == "carried":
                yield (
                    "Install_New_Filter",
                    ISSState(
                        robot_loc=state.robot_loc,
                        new_filter_loc="US_Lab",
                        old_filter_loc=state.old_filter_loc,
                        toolbox_loc=state.toolbox_loc,
                        old_filter_removed=state.old_filter_removed,
                        new_filter_installed=True,
                    ),
                    0.0,
                )


def list_cases() -> list[str]:
    return ["easy", "medium", "hard"]


def build_case_problem(case_name: str) -> ISSRobotProblem:
    if case_name == "easy":
        iss_map = base_iss_map()
        start = ISSState(
            robot_loc="Node_3",
            new_filter_loc="Storage_PMM",
            old_filter_loc="US_Lab",
            toolbox_loc="Storage_PMM",
            old_filter_removed=False,
            new_filter_installed=False,
        )
        return ISSRobotProblem(iss_map=iss_map, start_state=start)

    if case_name == "medium":
        iss_map = base_iss_map()
        start = ISSState(
            robot_loc="Airlock",
            new_filter_loc="Storage_PMM",
            old_filter_loc="US_Lab",
            toolbox_loc="US_Lab",
            old_filter_removed=False,
            new_filter_installed=False,
        )
        return ISSRobotProblem(iss_map=iss_map, start_state=start)

    if case_name == "hard":
        iss_map = base_iss_map()
        start = ISSState(
            robot_loc="Node_3",
            new_filter_loc="Node_2",
            old_filter_loc="US_Lab",
            toolbox_loc="Storage_PMM",
            old_filter_removed=False,
            new_filter_installed=False,
        )
        return ISSRobotProblem(iss_map=iss_map, start_state=start)

    raise ValueError(f"Unknown case: {case_name}")
