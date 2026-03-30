from __future__ import annotations

"""
ISS 机器人维护任务（Part B 的“谜题/问题设置”）

这是一个典型的“任务规划 = 状态空间搜索”问题：
- 状态（ISSState）记录机器人所在舱段、物品位置、以及维修进度
- 动作（successors）生成下一步可达状态：移动、拾取/放下、拆旧滤芯、装新滤芯
- 目标（is_goal）判断任务是否完成（新滤芯已安装 + 回到观测舱 + 工具箱归还）

核心约束（让问题有“新意”，但不至于爆炸）：
- 单物品携带：工具箱/新滤芯/旧滤芯一次只能携带一个（carried）
- 代价：Node_2 <-> Airlock 的移动代价为 2，其余边为 1
"""

from dataclasses import dataclass
from typing import Any, Iterable


def base_iss_map() -> dict[str, list[str]]:
    # ISS 舱段连接图（无向图用双向邻接表表达）
    return {
        "Storage_PMM": ["Node_3"],
        "Node_3": ["Storage_PMM", "Observatory", "Node_2"],
        "Observatory": ["Node_3"],
        "Node_2": ["Node_3", "US_Lab", "Airlock"],
        "US_Lab": ["Node_2"],
        "Airlock": ["Node_2"],
    }


def base_move_cost(a: str, b: str) -> float:
    # 移动代价：Airlock 这条边更“重”（代价=2），其他边代价=1
    if (a, b) in {("Node_2", "Airlock"), ("Airlock", "Node_2")}:
        return 2.0
    return 1.0


@dataclass(frozen=True)
class ISSState:
    # 物品位置用字符串表达；特殊值 "carried" 表示当前被机器人携带
    robot_loc: str
    new_filter_loc: str  # Storage_PMM / US_Lab / Node_2 / Node_3 / Airlock / Observatory / carried
    old_filter_loc: str  # US_Lab / Storage_PMM / carried
    toolbox_loc: str  # Storage_PMM / US_Lab / carried
    old_filter_removed: bool
    new_filter_installed: bool


def _carried_item(state: ISSState) -> str | None:
    # 单物品携带：三个物品里最多只能有一个位置是 "carried"
    for name, loc in (
        ("new_filter", state.new_filter_loc),
        ("old_filter", state.old_filter_loc),
        ("toolbox", state.toolbox_loc),
    ):
        if loc == "carried":
            return name
    return None

# 辅助函数：根据物品名和目标位置，生成新的状态
# （用于 Pick/Drop 动作）
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
    # 为启发式函数预计算最短路距离表 d(room_i, room_j)（小图，直接对每个源点跑 Dijkstra）
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
        # 目标：新滤芯已装好 + 机器人到 Observatory + （可选）工具箱已归还 Storage_PMM
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
        # 启发式（Waypoint / 分阶段目标）：
        # 依照“必须完成的子目标顺序”列出剩余必经房间，然后把这些房间之间的最短路距离相加。
        # 这相当于一个放松问题（忽略部分约束带来的绕路），通常是可采纳的 admissible heuristic。
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
        # 1) Move：移动到相邻房间（带移动代价）
        for to_room in self._map[state.robot_loc]:
            yield (f"Move({to_room})", _move_robot(state, to_room), base_move_cost(state.robot_loc, to_room))

        carried = _carried_item(state)

        # 2) Pick：如果没携带物品，可以拾取当前房间内的物品（代价=0）
        if carried is None:
            for obj, loc in (
                ("toolbox", state.toolbox_loc),
                ("new_filter", state.new_filter_loc),
                ("old_filter", state.old_filter_loc),
            ):
                if loc == state.robot_loc:
                    nxt = _set_loc(state, obj, "carried")
                    yield (f"Pick({obj})", nxt, 0.0)

        # 3) Drop：把携带的物品放到当前房间（代价=0）
        if carried is not None:
            obj = carried
            nxt = _set_loc(state, obj, state.robot_loc)
            yield (f"Drop({obj})", nxt, 0.0)

        # 4) US_Lab 专属动作：拆旧滤芯、装新滤芯（都要求工具箱在 US_Lab 或被携带）
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
    # 实验用的三档难度（你也可以继续加 case）
    return ["easy", "medium", "hard"]


def build_case_problem(case_name: str) -> ISSRobotProblem:
    # 将字符串 case_name 映射到不同的初始状态（从而制造不同难度）
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
