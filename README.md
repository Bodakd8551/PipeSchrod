# PipeSchrod

**Pipe-chained quantum bound-state solver** for the Schrödinger & Salpeter equations.

*Dr. Yasser Mustafa — Theoretical Nuclear & Particle Physics*

Part of the **Pipe*** family: PipeFrame · PipePlotly · PipeScrape · **PipeSchrod**

---

## The >> Operator

PipeSchrod uses the `>>` operator to chain every step of a quantum calculation
into a single readable expression:

```python
from pipeschrod import PipeSchrod
from pipeschrod.steps import Cornell, Grid, Solve, Compare, Plot, Export

result = (
    PipeSchrod(m1=1.4495, m2=1.4495)   # system: charm quark masses
    >> Cornell(alpha=0.5317, b=0.1497)  # potential: Cornell funnel
    >> Grid(N=200, rmax=20.0)           # grid: 200 points, 0–20 GeV⁻¹
    >> Solve("FGH")                     # solver: Fourier Grid Hamiltonian
    >> Plot("dashboard")                # figure: all-in-one 4-panel
    >> Export("csv", path="result.csv") # output: eigenvalue table
)
```

---

## Installation

```bash
pip install numpy scipy matplotlib rich
pip install -e .   # from source directory
```

---

## Methods

| Method | Class | Order | Notes |
|--------|-------|-------|-------|
| Standard Matrix | `MatrixSolver` | O(h²) | Tridiagonal, fastest build |
| Matrix Numerov  | `NumerovSolver`| O(h⁴) | Full B⁻¹A, 4th-order |
| FGH             | `FGHSolver`    | O(h⁶) | 5-point stencil, fastest convergence |
| Salpeter        | `SalpeterSolver`| spectral | Relativistic √(m²+p²) |

---

## Pipe Steps

| Step | Description |
|------|-------------|
| `Cornell(alpha, b, pot_type)` | Coulomb+Linear potential (type 1/2/3) |
| `Harmonic(omega)`             | Harmonic oscillator |
| `Coulomb(Z)`                  | Hydrogen-like Coulomb |
| `WoodsSaxon(V0, R, a)`        | Nuclear shell model |
| `Morse(De, re, a)`            | Molecular vibrations |
| `Grid(N, rmax, r0)`           | Set radial grid |
| `Solve("FGH")`                | Run solver(s) — any of Matrix/Numerov/FGH/Salpeter/"all" |
| `Compare(n_states)`           | Print side-by-side energy comparison |
| `Summary(n_states)`           | Print eigenvalue table for active result |
| `Plot("dashboard")`           | Generate figure(s) |
| `Export("csv", path=...)`     | Save results to CSV or JSON |

---

## Plot Types

```python
Plot("dashboard")      # 4-panel overview
Plot("wavefunctions")  # u(r) grid
Plot("densities")      # |u(r)|² grid
Plot("potential")      # V(r) + energy levels
Plot("spectrum")       # mass spectrum bar chart
Plot("compare_wf")     # 1S wave function from all methods overlaid
Plot("compare_E")      # grouped energy bar chart
Plot("convergence")    # E₁ vs N
Plot("sensitivity")    # E₁ vs α or b
Plot("all")            # every figure above
```

---

## Recipes

### All four solvers in one chain

```python
(
    PipeSchrod(m1=1.4495, m2=1.4495)
    >> Cornell(alpha=0.5317, b=0.1497)
    >> Grid(N=200, rmax=20.0)
    >> Solve("all")
    >> Compare()
    >> Plot("compare_E", "compare_wf", save="./figures")
    >> Export("csv_compare", path="comparison.csv")
)
```

### Reuse a base pipe

```python
base = (
    PipeSchrod(m1=1.4495, m2=1.4495)
    >> Cornell(alpha=0.5317, b=0.1497)
    >> Grid(N=200, rmax=20.0)
)

fgh_result  = base >> Solve("FGH")
sal_result  = base >> Solve("Salpeter")
# base is unchanged — >> creates a new object every time
```

### Bottomonium

```python
(
    PipeSchrod(m1=4.67, m2=4.67)
    >> Cornell(alpha=0.471, b=0.192)
    >> Grid(N=200, rmax=20.0)
    >> Solve("FGH", "Salpeter")
    >> Compare()
)
```

### Access results

```python
pipe   = base >> Solve("FGH")
result = pipe.result                    # primary SchrodResult
print(result.bound_energies)           # array of eigenvalues [GeV]
print(result.binding_energies_mev)     # B.E. = (E - 2m) * 1000 [MeV]
print(result.mean_radius(0))           # <r> for 1S [GeV⁻¹]

multi = base >> Solve("Matrix", "FGH")
print(multi["Matrix"].bound_energies[0])   # 3.04248 GeV
print(multi["FGH"].bound_energies[0])      # 3.04911 GeV
```

---

## SchrodResult Properties

```python
res.bound_energies          # [GeV]   — eigenvalues below threshold
res.binding_energies_mev    # [MeV]   — (E - 2m) * 1000
res.bound_psi               # array   — normalised wave functions
res.bound_prob              # array   — |u(r)|²
res.n_bound                 # int     — number of bound states
res.node_count(n)           # int     — nodes in nth state
res.mean_radius(n)          # float   — ⟨r⟩ [GeV⁻¹]
res.rms_radius(n)           # float   — √⟨r²⟩ [GeV⁻¹]
res.state_label(n)          # str     — e.g. "1S", "2P"
res.summary_dict()          # dict    — all data as plain dict
```

---

## Presets

```python
# Charmonium:   m=1.4495, α=0.5317, b=0.1497
# Bottomonium:  m=4.67,   α=0.471,  b=0.192
# P-wave:       PipeSchrod(m1=1.4495, m2=1.4495, L=1) >> Cornell(pot_type=2)
```
