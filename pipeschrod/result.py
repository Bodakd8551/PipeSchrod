"""
result.py  —  SchrodResult data container.

Stores every output of a solver call and exposes clean
derived properties (binding energies, node counts, radii, etc.).
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import List


@dataclass
class SchrodResult:
    """
    Container for a single PipeSchrod solver output.

    Core arrays
    -----------
    r          : radial grid [GeV⁻¹],       shape (N,)
    energies   : all N eigenvalues [GeV]
    psi        : normalised eigenvectors,    shape (N, N)
    potential  : V(r) on the grid,           shape (N,)
    V_eff      : V(r) + centrifugal barrier, shape (N,)

    Derived properties (computed on demand)
    ----------------------------------------
    bound_indices       → indices below the open-threshold
    bound_energies      → eigenvalues below threshold [GeV]
    binding_energies_mev→ (E − 2m) × 1000 [MeV]
    bound_psi           → wave functions for bound states
    bound_prob          → |u(r)|² for bound states
    n_bound             → number of bound states
    node_count(n)       → sign changes in nth wave function
    mean_radius(n)      → ⟨r⟩ [GeV⁻¹]
    rms_radius(n)       → √⟨r²⟩ [GeV⁻¹]
    """

    method    : str
    r         : np.ndarray
    energies  : np.ndarray
    psi       : np.ndarray
    potential : np.ndarray
    V_eff     : np.ndarray
    L         : int   = 0
    S         : int   = 1
    J         : int   = 1
    m1        : float = 1.4495
    m2        : float = 1.4495
    N         : int   = 200
    rmax      : float = 20.0
    pot_name  : str   = "unknown"
    params    : dict  = field(default_factory=dict)
    cpu_time  : float = 0.0

    # ── Auto-computed fields ──────────────────────────────────────────────────

    mu        : float = field(init=False)
    threshold : float = field(init=False)
    h         : float = field(init=False)

    def __post_init__(self):
        self.mu        = self.m1 * self.m2 / (self.m1 + self.m2)
        self.threshold = self.m1 + self.m2
        self.h         = float(self.r[1] - self.r[0])

    # ── Bound-state detection ─────────────────────────────────────────────────

    @property
    def open_threshold(self) -> float:
        """Physical open-flavour threshold above which the meson dissociates."""
        return self.threshold + min(3.0, 2.5 / self.mu)

    @property
    def bound_indices(self) -> List[int]:
        return [i for i, E in enumerate(self.energies)
                if E < self.open_threshold]

    @property
    def bound_energies(self) -> np.ndarray:
        return self.energies[self.bound_indices]

    @property
    def binding_energies_mev(self) -> np.ndarray:
        return (self.bound_energies - self.threshold) * 1000.0

    @property
    def bound_psi(self) -> np.ndarray:
        return self.psi[self.bound_indices]

    @property
    def bound_prob(self) -> np.ndarray:
        return self.bound_psi ** 2

    @property
    def n_bound(self) -> int:
        return len(self.bound_indices)

    # ── Spectroscopic helpers ─────────────────────────────────────────────────

    @property
    def L_label(self) -> str:
        return ["S", "P", "D", "F", "G", "H"][min(self.L, 5)]

    def state_label(self, n: int) -> str:
        return f"{n+1}{self.L_label}"

    # ── Derived observables ───────────────────────────────────────────────────

    def node_count(self, n: int) -> int:
        u = self.bound_psi[n]
        return int(np.sum((u[:-1] * u[1:]) < 0))

    def mean_radius(self, n: int) -> float:
        u2 = self.bound_psi[n] ** 2
        return float(np.trapz(self.r * u2, self.r))

    def rms_radius(self, n: int) -> float:
        u2 = self.bound_psi[n] ** 2
        return float(np.sqrt(np.trapz(self.r**2 * u2, self.r)))

    def psi_at_origin(self, n: int) -> float:
        u0, r0 = self.bound_psi[n, 0], self.r[0]
        return float((u0 / r0) ** 2)

    # ── Export helpers ────────────────────────────────────────────────────────

    def summary_dict(self) -> dict:
        rows = []
        for n in range(self.n_bound):
            rows.append({
                "n"          : n + 1,
                "State"      : self.state_label(n),
                "E_GeV"      : round(float(self.bound_energies[n]), 6),
                "E_MeV"      : round(float(self.bound_energies[n]) * 1000, 3),
                "BE_MeV"     : round(float(self.binding_energies_mev[n]), 3),
                "Nodes"      : self.node_count(n),
                "mean_r"     : round(self.mean_radius(n), 4),
                "rms_r"      : round(self.rms_radius(n), 4),
            })
        return {
            "method"   : self.method,
            "potential": self.pot_name,
            "params"   : self.params,
            "grid"     : {"N": self.N, "rmax": self.rmax, "h": round(self.h, 6)},
            "physics"  : {"m1": self.m1, "m2": self.m2, "mu": round(self.mu, 6),
                          "L": self.L, "S": self.S, "J": self.J,
                          "threshold": round(self.threshold, 6)},
            "cpu_s"    : round(self.cpu_time, 4),
            "states"   : rows,
        }

    def __repr__(self) -> str:
        E1 = f"{self.bound_energies[0]:.5f}" if self.n_bound else "—"
        return (f"SchrodResult(method={self.method!r}, "
                f"n_bound={self.n_bound}, E1={E1} GeV, "
                f"cpu={self.cpu_time*1000:.1f}ms)")
