"""
core.py  —  PipeSchrod pipe-chain engine.

Every >> call returns a new PipeSchrod, so chains are:
  • Immutable  : each step produces a fresh object; originals are unchanged.
  • Composable : any sub-chain can be stored and extended later.
  • Lazy       : Solve() triggers computation; earlier steps only set state.

Internal state dict keys
------------------------
  m1, m2        quark masses          [GeV]
  L, S, J       quantum numbers
  pot_fn        callable V(r)
  N             grid points
  rmax          max radius            [GeV⁻¹]
  r0            min radius            [GeV⁻¹]
  methods       list of solver names to run
  results       dict  {method: SchrodResult}
  active        name of the "primary" result used by Plot / Export
"""

from __future__ import annotations
from copy import deepcopy
from typing import Any


class PipeSchrod:
    """
    The central pipe object.  Instantiate with physical parameters,
    then chain >> steps to build a complete quantum calculation.

    Parameters
    ----------
    m1, m2 : quark masses [GeV]  (default: charmonium 1.4495 GeV)
    L, S, J: quantum numbers     (default: S-wave, spin-triplet)

    Examples
    --------
    >>> from pipeschrod import PipeSchrod
    >>> from pipeschrod.steps import Cornell, Grid, Solve, Plot

    >>> pipe = PipeSchrod(m1=1.4495, m2=1.4495)
    >>> (pipe >> Cornell(alpha=0.5317, b=0.1497)
    ...       >> Grid(N=200, rmax=20.0)
    ...       >> Solve("FGH")
    ...       >> Plot("dashboard"))

    # Reuse the same base pipe for different solvers
    >>> base = pipe >> Cornell(alpha=0.5317, b=0.1497) >> Grid(N=200)
    >>> fgh_result  = base >> Solve("FGH")
    >>> sal_result  = base >> Solve("Salpeter")
    """

    def __init__(self,
                 m1:  float = 1.4495,
                 m2:  float = 1.4495,
                 L:   int   = 0,
                 S:   int   = 1,
                 J:   int   = 1):
        self._state: dict[str, Any] = {
            "m1"     : m1,
            "m2"     : m2,
            "L"      : L,
            "S"      : S,
            "J"      : J,
            "pot_fn" : None,
            "N"      : 200,
            "rmax"   : 20.0,
            "r0"     : 0.1,
            "methods": [],
            "results": {},
            "active" : None,
        }

    # ── Pipe operator ─────────────────────────────────────────────────────────

    def __rshift__(self, step: "PipeStep") -> "PipeSchrod":
        """
        Apply a pipe step and return a new PipeSchrod with updated state.
        Usage:  pipe >> Cornell(...) >> Grid(...) >> Solve("FGH")
        """
        if not callable(step):
            raise TypeError(
                f">> operand must be a PipeStep, got {type(step).__name__!r}.\n"
                f"Hint: use PipeSchrod(m1=...) >> Cornell(...) >> Solve(...)"
            )
        new_pipe = PipeSchrod.__new__(PipeSchrod)
        new_pipe._state = deepcopy(self._state)
        step._apply(new_pipe._state)
        return new_pipe

    # ── Convenience accessors ─────────────────────────────────────────────────

    @property
    def result(self) -> "SchrodResult | None":
        """Return the primary (most recently solved) result."""
        active = self._state.get("active")
        if active:
            return self._state["results"].get(active)
        results = self._state["results"]
        if results:
            return next(reversed(results.values()))
        return None

    @property
    def results(self) -> dict:
        """Return all computed results as {method: SchrodResult}."""
        return self._state["results"]

    def __getitem__(self, method: str) -> "SchrodResult":
        """pipe["FGH"] → the FGH SchrodResult."""
        return self._state["results"][method]

    # ── Pretty print ─────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        s      = self._state
        pot    = getattr(s.get("pot_fn"), "__name__", "none")
        solved = list(s["results"].keys()) or ["—"]
        return (
            f"PipeSchrod("
            f"m1={s['m1']}, m2={s['m2']}, "
            f"L={s['L']}, S={s['S']}, J={s['J']} | "
            f"pot={pot} | N={s['N']}, rmax={s['rmax']} | "
            f"solved={solved})"
        )

    def _repr_html_(self) -> str:
        """Jupyter-friendly HTML representation."""
        s   = self._state
        pot = getattr(s.get("pot_fn"), "__name__", "—")
        rows = ""
        for meth, res in s["results"].items():
            if res.n_bound > 0:
                E1 = f"{res.bound_energies[0]:.5f}"
                nb = res.n_bound
            else:
                E1, nb = "—", 0
            rows += (
                f"<tr><td><b>{meth}</b></td>"
                f"<td>{E1} GeV</td><td>{nb}</td>"
                f"<td>{res.cpu_time*1000:.1f} ms</td></tr>"
            )
        if not rows:
            rows = "<tr><td colspan='4' style='color:#888'>No solvers run yet — add >> Solve(...)</td></tr>"
        return f"""
        <div style='font-family:monospace;background:#0d1117;color:#e6edf3;
                    padding:16px;border-radius:8px;border:1px solid #30363d'>
          <b style='color:#58a6ff'>PipeSchrod</b> &nbsp;
          m&#x2081;={s['m1']} &nbsp; m&#x2082;={s['m2']} &nbsp;
          L={s['L']} S={s['S']} J={s['J']} &nbsp;
          pot=<span style='color:#ffa657'>{pot}</span> &nbsp;
          N={s['N']} rmax={s['rmax']}<br><br>
          <table style='border-collapse:collapse;font-size:13px'>
            <tr style='color:#8b949e'>
              <th style='padding:4px 12px 4px 0'>Method</th>
              <th style='padding:4px 12px'>E&#x2081;</th>
              <th style='padding:4px 12px'>Bound states</th>
              <th style='padding:4px 12px'>CPU</th>
            </tr>
            {rows}
          </table>
        </div>"""


# ── Base class for all pipe steps ─────────────────────────────────────────────

class PipeStep:
    """
    Abstract base for all >> steps.
    Subclasses implement _apply(state: dict) -> None.
    """
    def __call__(self, state: dict) -> None:
        self._apply(state)

    def _apply(self, state: dict) -> None:   # pragma: no cover
        raise NotImplementedError

    def __repr__(self) -> str:
        attrs = {k: v for k, v in self.__dict__.items()
                 if not k.startswith("_")}
        args  = ", ".join(f"{k}={v!r}" for k, v in attrs.items())
        return f"{self.__class__.__name__}({args})"
