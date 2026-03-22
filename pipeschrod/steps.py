"""
steps.py  —  All pipe-step classes used with the >> operator.

Each class inherits PipeStep and implements _apply(state).

Available steps
---------------
Potential steps   : Cornell, Harmonic, Coulomb, WoodsSaxon, Morse
Grid step         : Grid
Solver step       : Solve
Comparison step   : Compare
Visualisation step: Plot
Export step       : Export
Info step         : Summary
"""

from __future__ import annotations
import os
from typing import Optional

from .core import PipeStep
from .potentials import cornell, harmonic, coulomb, woods_saxon, morse


# ═══════════════════════════════════════════════════════════════════════════════
#  POTENTIAL STEPS
# ═══════════════════════════════════════════════════════════════════════════════

class Cornell(PipeStep):
    """
    Cornell (funnel) potential: V(r) = −4α/3r + b·r

    Optionally include hyperfine (type 2) or full spin-dependent (type 3)
    corrections.

    Parameters
    ----------
    alpha    : strong coupling  (default 0.5317, charmonium)
    b        : string tension   [GeV²]  (default 0.1497)
    C        : constant shift   [GeV]   (default 0.0)
    pot_type : 1 = Coulomb+Linear, 2 = +Hyperfine, 3 = +Spin-Orbit+Tensor

    Example
    -------
    >>> pipe >> Cornell(alpha=0.5317, b=0.1497)
    >>> pipe >> Cornell(alpha=0.471, b=0.192, pot_type=2)
    """
    def __init__(self,
                 alpha: float = 0.5317,
                 b: float = 0.1497,
                 C: float = 0.0,
                 pot_type: int = 1):
        self.alpha = alpha
        self.b = b
        self.C = C
        self.pot_type = pot_type

    def _apply(self, state: dict) -> None:
        state["pot_fn"] = cornell(
            alpha=self.alpha,
            b=self.b,
            C=self.C,
            m1=state["m1"],
            m2=state["m2"],
            L=state["L"],
            S=state["S"],
            J=state["J"],
            pot_type=self.pot_type,
        )


class Harmonic(PipeStep):
    """
    Quantum harmonic oscillator: V(r) = ½·mass·ω²·r²

    Exactly solvable benchmark potential.

    Example
    -------
    >>> pipe >> Harmonic(omega=1.0)
    """
    def __init__(self, omega: float = 1.0, mass: float = 1.0):
        self.omega = omega
        self.mass = mass

    def _apply(self, state: dict) -> None:
        state["pot_fn"] = harmonic(omega=self.omega, mass=self.mass)


class Coulomb(PipeStep):
    """
    Hydrogen-like Coulomb potential: V(r) = −Z·α_em / r

    Example
    -------
    >>> pipe >> Coulomb(Z=1.0)
    """
    def __init__(self, Z: float = 1.0, alpha_em: float = 1.0/137.036):
        self.Z = Z
        self.alpha_em = alpha_em

    def _apply(self, state: dict) -> None:
        state["pot_fn"] = coulomb(Z=self.Z, alpha_em=self.alpha_em)


class WoodsSaxon(PipeStep):
    """
    Woods-Saxon nuclear potential: V(r) = −V₀ / (1 + exp((r−R)/a))

    Example
    -------
    >>> pipe >> WoodsSaxon(V0=0.05, R=5.0, a=0.6)
    """
    def __init__(self, V0: float = 0.05, R: float = 5.0, a: float = 0.6):
        self.V0 = V0
        self.R = R
        self.a = a

    def _apply(self, state: dict) -> None:
        state["pot_fn"] = woods_saxon(V0=self.V0, R=self.R, a=self.a)


class Morse(PipeStep):
    """
    Morse potential: V(r) = Dₑ·(1 − exp(−a(r−rₑ)))² − Dₑ

    Example
    -------
    >>> pipe >> Morse(De=0.3, re=2.0, a=0.5)
    """
    def __init__(self, De: float = 0.3, re: float = 2.0, a: float = 0.5):
        self.De = De
        self.re = re
        self.a = a

    def _apply(self, state: dict) -> None:
        state["pot_fn"] = morse(De=self.De, re=self.re, a=self.a)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRID STEP
# ═══════════════════════════════════════════════════════════════════════════════

class Grid(PipeStep):
    """
    Set the radial grid parameters.

    Parameters
    ----------
    N    : number of grid points  (default 200)
    rmax : maximum radius [GeV⁻¹] (default 20.0)
    r0   : minimum radius [GeV⁻¹] (default 0.1)

    Example
    -------
    >>> pipe >> Grid(N=300, rmax=25.0)
    """
    def __init__(self,
                 N: int = 200,
                 rmax: float = 20.0,
                 r0: float = 0.1):
        self.N = N
        self.rmax = rmax
        self.r0 = r0

    def _apply(self, state: dict) -> None:
        state["N"] = self.N
        state["rmax"] = self.rmax
        state["r0"] = self.r0


# ═══════════════════════════════════════════════════════════════════════════════
#  SOLVE STEP
# ═══════════════════════════════════════════════════════════════════════════════

class Solve(PipeStep):
    """
    Run one or more solvers and store results in the pipe.

    Parameters
    ----------
    *methods : solver name(s) — any of:
               "Matrix", "Numerov", "FGH", "Salpeter", "all"
               Pass multiple: Solve("Matrix", "FGH")
               Pass "all":    Solve("all")

    Examples
    --------
    >>> pipe >> Solve("FGH")
    >>> pipe >> Solve("Matrix", "Numerov", "FGH", "Salpeter")
    >>> pipe >> Solve("all")
    """

    ALL_METHODS = ["Matrix", "Numerov", "FGH", "Salpeter"]

    def __init__(self, *methods: str):
        if not methods:
            methods = ("FGH",)
        if len(methods) == 1 and methods[0].lower() == "all":
            self.methods = self.ALL_METHODS
        else:
            for m in methods:
                if m not in self.ALL_METHODS:
                    raise ValueError(
                        f"Unknown method {m!r}. "
                        f"Choose from {self.ALL_METHODS} or 'all'."
                    )
            self.methods = list(methods)

    def _apply(self, state: dict) -> None:
        from .solvers import MatrixSolver, NumerovSolver
        from .solvers import FGHSolver, SalpeterSolver

        solver_map = {
            "Matrix": MatrixSolver,
            "Numerov": NumerovSolver,
            "FGH": FGHSolver,
            "Salpeter": SalpeterSolver,
        }

        if state["pot_fn"] is None:
            raise RuntimeError(
                "No potential set. Add a potential step before Solve().\n"
                "Example:  pipe >> Cornell(alpha=0.5, b=0.1) >> Solve('FGH')"
            )

        kw = {
            "N": state["N"],
            "rmax": state["rmax"],
            "r0": state["r0"],
            "m1": state["m1"],
            "m2": state["m2"],
            "L": state["L"],
            "S": state["S"],
            "J": state["J"],
        }

        for method in self.methods:
            solver = solver_map[method](**kw)
            res = solver.solve(state["pot_fn"])
            state["results"][method] = res
            state["active"] = method          # last solved = active

        state["methods"] = list(state["results"].keys())


# ═══════════════════════════════════════════════════════════════════════════════
#  COMPARE STEP
# ═══════════════════════════════════════════════════════════════════════════════

class Compare(PipeStep):
    """
    Print a rich side-by-side comparison of all computed results.

    Parameters
    ----------
    n_states : number of bound states to compare (default 6)

    Example
    -------
    >>> pipe >> Solve("all") >> Compare()
    >>> pipe >> Solve("all") >> Compare(n_states=4)
    """
    def __init__(self, n_states: int = 6):
        self.n_states = n_states

    def _apply(self, state: dict) -> None:
        from .reporter import SchrodReporter
        if not state["results"]:
            print("[PipeSchrod] Compare: no results — run Solve() first.")
            return
        rep = SchrodReporter(state["results"])
        rep.print_comparison(n_states=self.n_states)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUMMARY STEP
# ═══════════════════════════════════════════════════════════════════════════════

class Summary(PipeStep):
    """
    Print a detailed eigenvalue table for the active (most recent) result.

    Parameters
    ----------
    n_states : rows to show (default 8)
    method   : which result to summarise (default: last solved)

    Example
    -------
    >>> pipe >> Solve("FGH") >> Summary()
    >>> pipe >> Solve("all") >> Summary(method="Salpeter", n_states=5)
    """
    def __init__(self, n_states: int = 8, method: Optional[str] = None):
        self.n_states = n_states
        self.method = method

    def _apply(self, state: dict) -> None:
        from .reporter import SchrodReporter
        if not state["results"]:
            print("[PipeSchrod] Summary: no results yet — run Solve() first.")
            return
        key = self.method or state["active"]
        if key not in state["results"]:
            print(f"[PipeSchrod] Summary: method {key!r} not found.")
            return
        rep = SchrodReporter(state["results"][key])
        rep.print_summary()
        rep.print_eigenvalue_table(n_states=self.n_states)


# ═══════════════════════════════════════════════════════════════════════════════
#  PLOT STEP
# ═══════════════════════════════════════════════════════════════════════════════

_VALID_PLOTS = {
    "dashboard": "All-in-one: wave functions, potential, density, spectrum",
    "wavefunctions": "Normalised radial wave functions u(r)",
    "densities": "Radial probability densities |u(r)|²",
    "potential": "V(r) with bound-state energy levels",
    "spectrum": "Mass spectrum bar chart",
    "compare_wf": "1S wave function from all computed methods overlaid",
    "compare_E": "Side-by-side energy bar chart for all methods",
    "convergence": "Ground-state energy vs grid size N",
    "sensitivity": "Potential shape and E₁ vs parameter α or b",
}


class Plot(PipeStep):
    """
    Generate one or more figures from the computed results.

    Parameters
    ----------
    *figures  : figure name(s) from the list below, or "all"
    n_states  : bound states to include        (default 4)
    save      : directory to save PNG files    (default None = display only)
    show      : call plt.show()                (default True)
    method    : which result to plot           (default: last solved)

    Available figures
    -----------------
    "dashboard"     — 4-panel overview (wf/potential/density/spectrum)
    "wavefunctions" — normalised u(r) grid
    "densities"     — |u(r)|² probability densities
    "potential"     — V(r) with energy levels
    "spectrum"      — mass spectrum bar chart
    "compare_wf"    — 1S wave function from all methods overlaid
    "compare_E"     — energy spectrum comparison across methods
    "convergence"   — ground-state energy vs N
    "sensitivity"   — potential and E₁ sensitivity to α or b
    "all"           — generate every figure above

    Examples
    --------
    >>> pipe >> Solve("FGH") >> Plot("dashboard")
    >>> pipe >> Solve("all") >> Plot("compare_E", "compare_wf")
    >>> pipe >> Solve("FGH") >> Plot("all", save="./figures")
    """
    def __init__(self,
                 *figures: str,
                 n_states: int = 4,
                 save: Optional[str] = None,
                 show: bool = True,
                 method: Optional[str] = None):
        if not figures:
            figures = ("dashboard",)
        if len(figures) == 1 and figures[0].lower() == "all":
            self.figures = list(_VALID_PLOTS.keys())
        else:
            for f in figures:
                if f not in _VALID_PLOTS:
                    raise ValueError(
                        f"Unknown figure {f!r}.\n"
                        f"Available: {list(_VALID_PLOTS.keys())} or 'all'."
                    )
            self.figures = list(figures)

        self.n_states = n_states
        self.save = save
        self.show = show
        self.method = method

    def _apply(self, state: dict) -> None:
        import matplotlib
        if not self.show:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from .plotter import SchrodPlotter

        if not state["results"]:
            print("[PipeSchrod] Plot: no results yet — run Solve() first.")
            return

        save_dir = self.save
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        # Primary result (single-method plots)
        key = self.method or state["active"]
        primary = state["results"].get(key)

        # Multi-method plotter
        p_multi = SchrodPlotter(state["results"], save_dir=save_dir)
        # Single plotter
        p_single = (SchrodPlotter(primary, save_dir=save_dir)
                    if primary else None)

        for fig_name in self.figures:
            fig, _ = None, None

            if fig_name == "dashboard" and p_single:
                fig, _ = p_single.dashboard(n_states=self.n_states)
            elif fig_name == "wavefunctions" and p_single:
                fig, _ = p_single.wave_functions(n_states=self.n_states)
            elif fig_name == "densities" and p_single:
                fig, _ = p_single.probability_densities(n_states=self.n_states)
            elif fig_name == "potential" and p_single:
                fig, _ = p_single.potential_and_levels(n_levels=self.n_states)
            elif fig_name == "spectrum" and p_single:
                fig, _ = p_single.spectrum(n_states=self.n_states + 2)
            elif fig_name == "compare_wf":
                fig, _ = p_multi.compare_wave_functions(n=0)
            elif fig_name == "compare_E":
                fig, _ = p_multi.compare_energies(n_states=self.n_states)
            elif fig_name == "convergence":
                fig, _ = p_multi.convergence(
                    potential_fn=state["pot_fn"],
                    m1=state["m1"], m2=state["m2"], L=state["L"])
            elif fig_name == "sensitivity":
                fig, _ = p_multi.parameter_sensitivity(
                    m1=state["m1"], m2=state["m2"])

            if fig is not None:
                if save_dir:
                    path = os.path.join(save_dir, f"{fig_name}.png")
                    fig.savefig(path, bbox_inches="tight",
                                facecolor="#0d1117", dpi=150)
                    print(f"  [PipeSchrod] Saved → {path}")
                if self.show:
                    plt.show()
                plt.close(fig)

# ═══════════════════════════════════════════════════════════════════════════════
#  EXPORT STEP
# ═══════════════════════════════════════════════════════════════════════════════

_VALID_FORMATS = {"csv", "json", "csv_compare"}



class Export(PipeStep):
    """
    Export computed results to CSV or JSON.

    Parameters
    ----------
    fmt    : "csv"         — eigenvalue table for the active result
             "json"        — full result summary as JSON
             "csv_compare" — multi-method comparison table
    path   : output file path  (default: auto-generated name)
    method : which result to export (default: active / last solved)

    Examples
    --------
    >>> pipe >> Solve("FGH") >> Export("csv", path="fgh_result.csv")
    >>> pipe >> Solve("all") >> Export("json") >> Export("csv_compare")
    """
    def __init__(self,
                 fmt: str = "csv",
                 path: Optional[str] = None,
                 method: Optional[str] = None):
        if fmt not in _VALID_FORMATS:
            raise ValueError(
                f"Unknown export format {fmt!r}. "
                f"Choose from {_VALID_FORMATS}."
            )
        self.fmt = fmt
        self.path = path
        self.method = method

    def _apply(self, state: dict) -> None:
        from .reporter import SchrodReporter

        if not state["results"]:
            print("[PipeSchrod] Export: no results — run Solve() first.")
            return

        key = self.method or state["active"]
        result = state["results"].get(key)

        if self.fmt == "csv":
            path = self.path or f"pipeschrod_{key or 'result'}.csv"
            SchrodReporter(result).save_csv(path)

        elif self.fmt == "json":
            path = self.path or f"pipeschrod_{key or 'result'}.json"
            SchrodReporter(result).save_json(path)

        elif self.fmt == "csv_compare":
            path = self.path or "pipeschrod_comparison.csv"
            SchrodReporter(state["results"]).save_comparison_csv(path)
