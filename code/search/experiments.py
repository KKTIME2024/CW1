from __future__ import annotations

from dataclasses import dataclass

from .common import SearchResult
from .problems.iss_robot import build_case_problem, list_cases
from .registry import ALGORITHMS


def run_single(
    *,
    case_name: str,
    algorithm: str,
    max_nodes: int,
    loop_check: bool,
    seed: int,
) -> SearchResult:
    problem = build_case_problem(case_name)
    fn = ALGORITHMS[algorithm]
    return fn(problem=problem, case=case_name, max_nodes=max_nodes, loop_check=loop_check, seed=seed)


def run_experiment_matrix(
    *,
    seeds: int,
    max_nodes: int,
    loop_check: bool,
) -> list[SearchResult]:
    results: list[SearchResult] = []
    for case in list_cases():
        for algo_name, fn in ALGORITHMS.items():
            if algo_name == "dfs_random":
                for s in range(seeds):
                    results.append(
                        fn(problem=build_case_problem(case), case=case, max_nodes=max_nodes, loop_check=loop_check, seed=s)
                    )
            else:
                results.append(fn(problem=build_case_problem(case), case=case, max_nodes=max_nodes, loop_check=loop_check, seed=0))
    return results

