from __future__ import annotations

from typing import Callable

from .algorithms import astar, best_first, bfs, dfs

# Each algorithm has the same call signature; registry is used by the CLI.
ALGORITHMS = {
    "bfs": bfs,
    "dfs_fixed": lambda **kw: dfs(**kw, randomized=False),
    "dfs_random": lambda **kw: dfs(**kw, randomized=True),
    "best_first": best_first,
    "astar": astar,
}

