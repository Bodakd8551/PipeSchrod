"""
potentials.py  —  Potential energy functions.

All potentials accept a numpy array r (GeV⁻¹) and return V(r) in GeV.
Each function returns a callable compatible with every PipeSchrod solver.
"""

from __future__ import annotations
import numpy as np
from typing import Callable

PotFn = Callable[[np.ndarray], np.ndarray]


def cornell(alpha:    float = 0.5317,
            b:        float = 0.1497,
            C:        float = 0.0,
            m1:       float = 1.4495,
            m2:       float = 1.4495,
            L:        int   = 0,
            S:        int   = 1,
            J:        int   = 1,
            pot_type: int   = 1,
            sigma:    float = 1.1412) -> PotFn:
    """
    Cornell (funnel) potential: V(r) = −4α/3r + b·r + C

    Types
    -----
    1 : Coulomb + Linear                          (default)
    2 : Type 1 + Gaussian-smeared hyperfine
    3 : Type 2 + spin-orbit coupling + tensor force
    """
    if   J == L + 1: T_op = -L / (6*(2*L+3))    if L > 0 else 0.0
    elif J == L:     T_op = 1.0 / 6
    elif J == L - 1: T_op = (L+1.0) / (6*(2*L-1)) if L > 0 else 0.0
    else:            T_op = 0.0

    spin_fac = 0.5*S*(S+1) - 0.75

    def _V(r: np.ndarray) -> np.ndarray:
        r  = np.asarray(r, dtype=float)
        V  = -4.0*alpha / (3.0*r) + b*r + C
        if pot_type >= 2:
            g  = (sigma/np.sqrt(np.pi))**3 * np.exp(-(sigma*r)**2)
            V += 32.0*alpha*np.pi / (9.0*m1*m2) * g * spin_fac
        if pot_type >= 3 and L > 0:
            LS = 0.5*(J*(J+1) - L*(L+1) - S*(S+1))
            V += (1.0/(m1*m2)) * (2.0*alpha/r**3 - b/(2.0*r)) * LS
            V += (4.0*alpha / r**3) * T_op
        return V

    _V.__name__ = f"cornell_type{pot_type}"
    _V.params   = dict(alpha=alpha, b=b, C=C, m1=m1, m2=m2,
                       L=L, S=S, J=J, pot_type=pot_type, sigma=sigma)
    return _V


def harmonic(omega: float = 1.0, mass: float = 1.0) -> PotFn:
    """V(r) = ½·mass·ω²·r²  — exactly solvable benchmark."""
    def _V(r): return 0.5 * mass * omega**2 * np.asarray(r)**2
    _V.__name__ = "harmonic"; _V.params = dict(omega=omega, mass=mass)
    return _V


def coulomb(Z: float = 1.0, alpha_em: float = 1/137.036) -> PotFn:
    """V(r) = −Z·α_em / r  — hydrogen-like Coulomb."""
    def _V(r): return -Z * alpha_em / np.asarray(r)
    _V.__name__ = "coulomb"; _V.params = dict(Z=Z, alpha_em=alpha_em)
    return _V


def woods_saxon(V0: float = 0.05, R: float = 5.0, a: float = 0.6) -> PotFn:
    """V(r) = −V₀ / (1 + exp((r−R)/a))  — nuclear shell model."""
    def _V(r): return -V0 / (1.0 + np.exp((np.asarray(r) - R) / a))
    _V.__name__ = "woods_saxon"; _V.params = dict(V0=V0, R=R, a=a)
    return _V


def morse(De: float = 0.3, re: float = 2.0, a: float = 0.5) -> PotFn:
    """V(r) = Dₑ·(1 − exp(−a(r−rₑ)))² − Dₑ  — molecular vibrations."""
    def _V(r):
        x = np.asarray(r)
        return De * (1.0 - np.exp(-a*(x-re)))**2 - De
    _V.__name__ = "morse"; _V.params = dict(De=De, re=re, a=a)
    return _V
