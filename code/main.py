from __future__ import annotations

import argparse
import csv
import sys

from search.problems.iss_robot import build_case_problem, list_cases
from search.registry import ALGORITHMS


# CLI：用于快速跑单个算法/案例，或批量跑实验并导出 CSV
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="comp2611-cw1-b")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # run：单次运行（一个 case + 一个算法）
    run = sub.add_parser("run", help="Run one algorithm on one case")
    run.add_argument("--case", default="easy", help="Case name (easy/medium/hard)")
    run.add_argument("--algo", default="astar", choices=sorted(ALGORITHMS.keys()))
    run.add_argument("--seed", type=int, default=0, help="Seed for randomized DFS")
    run.add_argument("--max-nodes", type=int, default=10000)
    run.add_argument("--no-loop-check", action="store_true")

    # experiment：批量实验（cases x algos），dfs_random 会按不同 seed 重复多次
    exp = sub.add_parser("experiment", help="Run a standard experiment matrix")
    exp.add_argument("--seeds", type=int, default=5, help="How many seeds for randomized DFS")
    exp.add_argument("--max-nodes", type=int, default=10000)
    exp.add_argument("--no-loop-check", action="store_true")
    exp.add_argument("--csv", default="", help="Write results to CSV path")

    return parser


# 以 Markdown 表格格式输出，方便直接粘贴到报告
def _print_markdown_table(rows: list[dict]) -> None:
    if not rows:
        print("(no results)")
        return

    cols = [
        "case",
        "algorithm",
        "success",
        "nodes_expanded",
        "time_ms",
        "path_cost",
        "path_len",
    ]
    print("| " + " | ".join(cols) + " |")
    print("|" + "|".join(["---"] * len(cols)) + "|")
    for row in rows:
        print("| " + " | ".join(str(row.get(c, "")) for c in cols) + " |")


def main(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "run":
        problem = build_case_problem(args.case)
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
        results = []
        for case in list_cases():
            for algo_name, fn in ALGORITHMS.items():
                if algo_name == "dfs_random":
                    for s in range(args.seeds):
                        results.append(
                            fn(
                                problem=build_case_problem(case),
                                case=case,
                                max_nodes=args.max_nodes,
                                loop_check=not args.no_loop_check,
                                seed=s,
                            )
                        )
                else:
                    results.append(
                        fn(
                            problem=build_case_problem(case),
                            case=case,
                            max_nodes=args.max_nodes,
                            loop_check=not args.no_loop_check,
                            seed=0,
                        )
                    )
        rows = [r.to_row() for r in results]
        _print_markdown_table(rows)
        if args.csv:
            # 导出 CSV：便于在 Excel/Sheets 里画图、算平均值
            with open(args.csv, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=sorted(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
