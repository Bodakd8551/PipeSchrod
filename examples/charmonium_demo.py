"""
PipeSchrod  —  Charmonium Spectroscopy Demo
============================================
Shows every >> chain pattern: single solver, all solvers,
comparison, figures, and data export.

Run:
    python examples/charmonium_demo.py
"""

import sys, os

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")

from pipeschrod import PipeSchrod
from pipeschrod.steps import (Cornell, Grid, Solve,
                               Compare, Summary, Plot, Export)

OUT = "./pipeschrod_output"
os.makedirs(OUT, exist_ok=True)

print()
print("╔══════════════════════════════════════════════════════╗")
print("║            PipeSchrod  —  Charmonium Demo            ║")
print("║          Dr. Yasser Mustafa  ·  pipeschrod           ║")
print("╚══════════════════════════════════════════════════════╝")
print()

# ── 1. Base pipe (reused across all demos) ────────────────────────────────────
base = (
    PipeSchrod(m1=1.4495, m2=1.4495, L=0, S=1, J=1)
    >> Cornell(alpha=0.5317, b=0.1497)
    >> Grid(N=200, rmax=20.0)
)

print("Base pipe:", base)

# ── 2. Single FGH solve + summary + dashboard ─────────────────────────────────
print("\n── Single FGH solve ──────────────────────────────────────────────────")
fgh_pipe = (
    base
    >> Solve("FGH")
    >> Summary(n_states=6)
)

# ── 3. Run all four solvers in one chain ──────────────────────────────────────
print("\n── All four solvers ──────────────────────────────────────────────────")
all_pipe = (
    base
    >> Solve("all")
    >> Compare(n_states=6)
)

# ── 4. Generate all figures ───────────────────────────────────────────────────
print("\n── Generating figures ────────────────────────────────────────────────")
(
    fgh_pipe
    >> Plot("dashboard",     save=OUT, show=False)
    >> Plot("wavefunctions", save=OUT, show=False)
    >> Plot("densities",     save=OUT, show=False)
    >> Plot("potential",     save=OUT, show=False)
    >> Plot("spectrum",      save=OUT, show=False)
)

(
    all_pipe
    >> Plot("compare_wf",  save=OUT, show=False)
    >> Plot("compare_E",   save=OUT, show=False)
    >> Plot("convergence", save=OUT, show=False)
    >> Plot("sensitivity", save=OUT, show=False)
)

# ── 5. Export data ────────────────────────────────────────────────────────────
print("\n── Exporting data ────────────────────────────────────────────────────")
(
    fgh_pipe
    >> Export("csv",  path=f"{OUT}/fgh_charmonium.csv")
    >> Export("json", path=f"{OUT}/fgh_charmonium.json")
)
(
    all_pipe
    >> Export("csv_compare", path=f"{OUT}/comparison_all_methods.csv")
)

# ── 6. Bottomonium in one chain ───────────────────────────────────────────────
print("\n── Bottomonium (Υ, bb̄) ──────────────────────────────────────────────")
(
    PipeSchrod(m1=4.67, m2=4.67)
    >> Cornell(alpha=0.471, b=0.192)
    >> Grid(N=200, rmax=20.0)
    >> Solve("FGH", "Salpeter")
    >> Compare(n_states=4)
    >> Plot("dashboard", save=OUT, show=False)
    >> Export("csv", path=f"{OUT}/bottomonium.csv")
)

# ── 7. Hyperfine correction (Cornell type 2) ──────────────────────────────────
print("\n── Charmonium with hyperfine correction (type 2) ────────────────────")
(
    PipeSchrod(m1=1.4495, m2=1.4495)
    >> Cornell(alpha=0.5317, b=0.1497, pot_type=2)
    >> Grid(N=200, rmax=20.0)
    >> Solve("Matrix", "FGH")
    >> Compare(n_states=4)
)

# ── 8. P-wave states ──────────────────────────────────────────────────────────
print("\n── P-wave states (L=1) ──────────────────────────────────────────────")
(
    PipeSchrod(m1=1.4495, m2=1.4495, L=1, S=1, J=1)
    >> Cornell(alpha=0.5317, b=0.1497)
    >> Grid(N=200, rmax=20.0)
    >> Solve("FGH")
    >> Summary(n_states=4)
)

# ── 9. Access results directly ───────────────────────────────────────────────
print("\n── Direct result access ─────────────────────────────────────────────")
pipe    = base >> Solve("FGH")
result  = pipe.result                  # primary SchrodResult
print(f"  pipe.result        : {result}")
print(f"  E1 (GeV)           : {result.bound_energies[0]:.6f}")
print(f"  B.E. 1S (MeV)      : {result.binding_energies_mev[0]:.3f}")
print(f"  Mean radius 1S     : {result.mean_radius(0):.4f} GeV⁻¹")
print(f"  RMS  radius 1S     : {result.rms_radius(0):.4f} GeV⁻¹")
print(f"  Node count  1S     : {result.node_count(0)}")

multi   = base >> Solve("Matrix", "FGH", "Salpeter")
matrix  = multi["Matrix"]              # access by name
salpeter= multi["Salpeter"]
print(f"\n  Matrix  E1 = {matrix.bound_energies[0]:.5f} GeV")
print(f"  Salpeter E1 = {salpeter.bound_energies[0]:.5f} GeV")
delta   = (matrix.bound_energies[0] - salpeter.bound_energies[0]) * 1000
print(f"  Relativistic shift = {delta:.1f} MeV")

print()
print("╔══════════════════════════════════════════════════════╗")
print(f"║  All outputs written to: {OUT:<28}║")
print("╚══════════════════════════════════════════════════════╝")
print()
