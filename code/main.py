from __future__ import annotations

import argparse
import csv
import sys

from search.experiments import run_experiment_matrix, run_single
from search.registry import ALGORITHMS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="comp2611-cw1-b")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run one algorithm on one case")
    run.add_argument("--case", default="easy", help="Case name (easy/medium/hard)")
    run.add_argument("--algo", default="astar", choices=sorted(ALGORITHMS.keys()))
    run.add_argument("--seed", type=int, default=0, help="Seed for randomized DFS")
    run.add_argument("--max-nodes", type=int, default=10000)
    run.add_argument("--no-loop-check", action="store_true")

    exp = sub.add_parser("experiment", help="Run a standard experiment matrix")
    exp.add_argument("--seeds", type=int, default=5, help="How many seeds for randomized DFS")
    exp.add_argument("--max-nodes", type=int, default=10000)
    exp.add_argument("--no-loop-check", action="store_true")
    exp.add_argument("--csv", default="", help="Write results to CSV path")

    return parser


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
        res = run_single(
            case_name=args.case,
            algorithm=args.algo,
            max_nodes=args.max_nodes,
            loop_check=not args.no_loop_check,
            seed=args.seed,
        )
        print(res.to_pretty_text())
        return 0 if res.success else 2

    if args.cmd == "experiment":
        results = run_experiment_matrix(
            seeds=args.seeds,
            max_nodes=args.max_nodes,
            loop_check=not args.no_loop_check,
        )
        rows = [r.to_row() for r in results]
        _print_markdown_table(rows)
        if args.csv:
            with open(args.csv, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=sorted(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
