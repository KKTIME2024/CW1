from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from statistics import mean, pstdev

from search.problems.iss_robot import build_case_problem, list_cases, list_heuristics
from search.registry import ALGORITHMS


# CLI：用于快速跑单个算法/案例，或批量跑实验并导出 CSV
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="comp2611-cw1-b")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # run：单次运行（一个 case + 一个算法）
    run = sub.add_parser("run", help="Run one algorithm on one case")
    run.add_argument("--case", default="easy", help="Case name (easy/medium/hard)")
    run.add_argument("--algo", default="astar", choices=sorted(ALGORITHMS.keys()))
    run.add_argument("--heuristic", default="waypoints", choices=list_heuristics())
    run.add_argument("--seed", type=int, default=0, help="Seed for randomized DFS")
    run.add_argument("--max-nodes", type=int, default=10000)
    run.add_argument("--no-loop-check", action="store_true")

    # experiment：批量实验（cases x algos），dfs_random 会按不同 seed 重复多次
    exp = sub.add_parser("experiment", help="Run a standard experiment matrix")
    exp.add_argument("--heuristic", default="all", choices=["all"] + list_heuristics())
    exp.add_argument("--seeds", type=int, default=5, help="How many seeds for randomized DFS")
    exp.add_argument("--max-nodes", type=int, default=10000)
    exp.add_argument("--no-loop-check", action="store_true")
    exp.add_argument("--csv", default="", help="Write results to CSV path")

    return parser


# 以 Markdown 表格格式输出，方便直接粘贴到报告
def _print_markdown_table(rows: list[dict], *, cols: list[str]) -> None:
    if not rows:
        print("(no results)")
        return

    print("| " + " | ".join(cols) + " |")
    print("|" + "|".join(["---"] * len(cols)) + "|")
    for row in rows:
        print("| " + " | ".join(str(row.get(c, "")) for c in cols) + " |")

def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return (float("nan"), float("nan"))
    if len(values) == 1:
        return (float(values[0]), 0.0)
    return (float(mean(values)), float(pstdev(values)))


def _summarize_results(raw_rows: list[dict]) -> list[dict]:
    # group by (case, algorithm, heuristic)
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for r in raw_rows:
        algo = str(r["algorithm"])
        heur = str(r.get("heuristic", "n/a"))
        # uninformed algorithms don't use heuristic; keep the summary table clean
        if algo in {"bfs", "dfs_fixed", "dfs_random"}:
            heur = "n/a"
        key = (str(r["case"]), algo, heur)
        groups[key].append(r)

    summary: list[dict] = []
    for (case, algo, heur), rs in sorted(groups.items()):
        runs = len(rs)
        succ = [x for x in rs if x.get("success") is True]
        success_rate = (len(succ) / runs) if runs else 0.0

        nodes_mean, nodes_std = _mean_std([float(x["nodes_expanded"]) for x in succ])
        time_mean, time_std = _mean_std([float(x["time_ms"]) for x in succ])
        cost_mean, cost_std = _mean_std([float(x["path_cost"]) for x in succ])
        len_mean, len_std = _mean_std([float(x["path_len"]) for x in succ])

        summary.append(
            {
                "case": case,
                "algorithm": algo,
                "heuristic": heur,
                "runs": runs,
                "success_rate": round(success_rate, 3),
                "nodes_mean": round(nodes_mean, 3),
                "nodes_std": round(nodes_std, 3),
                "time_ms_mean": round(time_mean, 3),
                "time_ms_std": round(time_std, 3),
                "path_cost_mean": round(cost_mean, 3),
                "path_cost_std": round(cost_std, 3),
                "path_len_mean": round(len_mean, 3),
                "path_len_std": round(len_std, 3),
            }
        )

    return summary


def main(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "run":
        problem = build_case_problem(args.case, heuristic_name=args.heuristic)
        fn = ALGORITHMS[args.algo]
        res = fn(
            problem=problem,
            case=args.case,
            max_nodes=args.max_nodes,
            loop_check=not args.no_loop_check,
            seed=args.seed,
        )
        print(res.to_pretty_text())
        return 0 if res.success else 2

    if args.cmd == "experiment":
        heuristics = list_heuristics() if args.heuristic == "all" else [args.heuristic]
        results = []
        for case in list_cases():
            for algo_name, fn in ALGORITHMS.items():
                if algo_name == "dfs_random":
                    for s in range(args.seeds):
                        results.append(
                            fn(
                                problem=build_case_problem(case, heuristic_name=heuristics[0]),
                                case=case,
                                max_nodes=args.max_nodes,
                                loop_check=not args.no_loop_check,
                                seed=s,
                            )
                        )
                elif algo_name in {"best_first", "astar"}:
                    for h in heuristics:
                        results.append(
                            fn(
                                problem=build_case_problem(case, heuristic_name=h),
                                case=case,
                                max_nodes=args.max_nodes,
                                loop_check=not args.no_loop_check,
                                seed=0,
                            )
                        )
                else:
                    results.append(
                        fn(
                            problem=build_case_problem(case, heuristic_name=heuristics[0]),
                            case=case,
                            max_nodes=args.max_nodes,
                            loop_check=not args.no_loop_check,
                            seed=0,
                        )
                    )
        raw_rows = [r.to_row() for r in results]
        summary_rows = _summarize_results(raw_rows)
        _print_markdown_table(
            summary_rows,
            cols=[
                "case",
                "algorithm",
                "heuristic",
                "runs",
                "success_rate",
                "nodes_mean",
                "nodes_std",
                "time_ms_mean",
                "time_ms_std",
                "path_cost_mean",
                "path_cost_std",
                "path_len_mean",
                "path_len_std",
            ],
        )
        if args.csv:
            # 导出汇总 CSV（含 mean/std）：便于直接进报告或做图
            with open(args.csv, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=sorted(summary_rows[0].keys()))
                w.writeheader()
                w.writerows(summary_rows)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
