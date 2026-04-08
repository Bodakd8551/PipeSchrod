"""
╔══════════════════════════════════════════════════════════════════════╗
║                    P I P E S C H R O D                              ║
║   Quantum Bound-State Solver — Pipe-Chained Matrix Methods           ║
║                                                                      ║
║   Methods : Matrix  ·  Numerov  ·  FGH  ·  Salpeter                 ║
║   Syntax  : system >> potential >> grid >> solve >> plot             ║
║   Author  : Dr. Yasser Mustafa                                       ║
╚══════════════════════════════════════════════════════════════════════╝

Minimal usage
-------------
    from pipeschrod import PipeSchrod
    from pipeschrod.steps import Cornell, Grid, Solve, Plot, Export

    (
        PipeSchrod(m1=1.4495, m2=1.4495)
        >> Cornell(alpha=0.5317, b=0.1497)
        >> Grid(N=200, rmax=20.0)
        >> Solve("FGH")
        >> Plot("dashboard")
        >> Export("csv", path="charmonium.csv")
    )
"""

from .core      import PipeSchrod
from .steps     import (Cornell, Harmonic, Coulomb, WoodsSaxon, Morse,
                         Grid, Solve, Compare, Plot, Export, Summary)
from .potentials import cornell, harmonic, coulomb, woods_saxon, morse
from .solvers   import MatrixSolver, NumerovSolver, FGHSolver, SalpeterSolver
from .result    import SchrodResult
from .plotter   import SchrodPlotter
from .reporter  import SchrodReporter

__version__ = "1.1.0"
__author__  = "Dr. Yasser Mustafa"

__all__ = [
    # ── Core pipe object ──────────────────────────────────────────────
    "PipeSchrod",
    # ── Pipe steps  (used with >>) ────────────────────────────────────
    "Cornell", "Harmonic", "Coulomb", "WoodsSaxon", "Morse",
    "Grid", "Solve", "Compare", "Plot", "Export", "Summary",
    # ── Functional potential builders ─────────────────────────────────
    "cornell", "harmonic", "coulomb", "woods_saxon", "morse",
    # ── Solver classes (direct / advanced use) ─────────────────────────
    "MatrixSolver", "NumerovSolver", "FGHSolver", "SalpeterSolver",
    # ── Result / output objects ────────────────────────────────────────
    "SchrodResult", "SchrodPlotter", "SchrodReporter",
]
