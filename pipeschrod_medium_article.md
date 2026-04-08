# Solving the Schrödinger Equation with Matrix Methods

A deep dive into four powerful numerical approaches — Standard Matrix, Numerov, FGH, and the relativistic Salpeter equation — implemented in the pipe-chained **PipeSchrod** package with real charmonium spectroscopy results.

**Dr. Yasser Mustafa** · Theoretical Nuclear & Particle Physics · ⏱ 13 min read

## Contents

1.  [Introduction](#intro)
2.  [The Radial Schrödinger Equation](#physics)
3.  [Introducing PipeSchrod](#pipeschrod)
4.  [Method 1 — Standard Matrix](#matrix)
5.  [Method 2 — Matrix Numerov](#numerov)
6.  [Method 3 — Fourier Grid Hamiltonian](#fgh)
7.  [Method 4 — Spinless Salpeter](#salpeter)
8.  [Numerical Results & Comparison](#results)
9.  [The PipeSchrod API in Full](#api)
10. [Conclusion](#conclusion)

<h2 id="intro">01 Introduction</h2>

> The Schrödinger equation, written in 1926, encodes every observable property of a quantum system. Yet for most physically interesting potentials — the Cornell funnel that confines quarks, the Woods-Saxon well that shapes atomic nuclei — it yields no analytic solution. Numerical matrix methods are indispensable.

This article presents four progressively powerful matrix methods for the radial Schrödinger equation, each implemented in **PipeSchrod** — a Python package built around the `>>` pipe operator. Every calculation in the article was produced by a single chain of `>>` steps:

```python
from pipeschrod import PipeSchrod
from pipeschrod.steps import Cornell, Grid, Solve, Compare, Plot, Export

(PipeSchrod(m1=1.4495, m2=1.4495)
 >> Cornell(alpha=0.5317, b=0.1497)
 >> Grid(N=200, rmax=20.0)
 >> Solve("all")
 >> Compare()
 >> Plot("dashboard")
 >> Export("csv", path="charmonium.csv"))
```

The benchmark system throughout is **charmonium** — the cc̄ meson family. The J/ψ was discovered in 1974 (the "November Revolution" of particle physics), its spectrum is precisely known from experiment, and its canonical Cornell potential parameters give a compact, well-defined numerical problem. Parameters used: α = 0.5317, b = 0.1497 GeV², m₁ = m₂ = 1.4495 GeV.

<h2 id="physics">02 The Radial Schrödinger Equation</h2>

For two particles in a spherically symmetric potential V(r), writing ψ = [u(r)/r]·Yₗᵐ separates the angular parts exactly, leaving a one-dimensional eigenvalue problem for u(r):

$$-\frac{\hbar^2}{2\mu} \frac{d^2u}{dr^2} + \left[ \frac{\hbar^2 L(L+1)}{2\mu r^2} + V(r) \right] u(r) = E \cdot u(r)$$

*Eq.(1) — Radial Schrödinger equation. μ = m₁m₂/(m₁+m₂) is the reduced mass.*

Boundary conditions u(0)=0 and u(∞)=0 quantise the energy into a discrete spectrum E₁ < E₂ < E₃… The term L(L+1)/r² is the centrifugal barrier: L=0 gives S-states, L=1 gives P-states, and so on. All four PipeSchrod methods solve exactly this equation, differing only in how they represent the kinetic energy operator d²/dr² as a matrix.

### The Cornell Potential

The Cornell potential combines the one-gluon-exchange Coulomb interaction (perturbative QCD at short range) with a linearly rising confinement term (the colour flux tube at long range):

$$V(r) = -\frac{4\alpha}{3r} + br$$

*Eq.(2) — Cornell potential. The 4/3 is the SU(3) colour factor for a quark–antiquark singlet.*

*Figure 1. The Cornell potential V(r) with α=0.5317, b=0.1497 GeV², and the first four S-state energy levels shown as dashed lines. The competing Coulomb (short range) and linear confinement (long range) terms create the characteristic funnel shape.*

### Discretisation

All four methods replace the continuous r with a uniform grid of N=200 points from r₀=0.1 to rₘₐₓ=20.0 GeV⁻¹ (step h=0.1 GeV⁻¹). The wave function u(r) becomes a column vector, and H·u=E·u becomes a standard matrix eigenvalue problem solved by `scipy.linalg.eigh`. Every eigenvalue is a total meson mass in GeV; the binding energy is B.E. = E − (m₁+m₂).

<h2 id="pipeschrod">03 Introducing PipeSchrod</h2>

**Part of the Pipe* family**
### PipeFrame · PipePlotly · PipeScrape · PipeSchrod
PipeSchrod extends the Pipe* ecosystem to quantum physics. Every step of a calculation — defining the system, choosing a potential, setting the grid, running solvers, plotting, exporting — is a `>>` step on a `PipeSchrod` object.

The `>>` operator is **immutable**: each step returns a new object, leaving the original unchanged. This means you can define a base pipe once and branch it into multiple solver chains without recomputing the potential or grid:

```python
# Define once, branch freely
base = (PipeSchrod(m1=1.4495, m2=1.4495)
        >> Cornell(alpha=0.5317, b=0.1497)
        >> Grid(N=200, rmax=20.0))

fgh_pipe  = base >> Solve("FGH")       # base unchanged
sal_pipe  = base >> Solve("Salpeter")   # independent branch
all_pipe  = base >> Solve("all")        # all four solvers
```

*Figure 2. PipeSchrod architecture. Immutability ensures safe branching for complex workflows.*

<h2 id="matrix">04 Method 1 — Standard Matrix</h2>

The most direct approach. The second derivative is approximated using the classic three-point finite difference stencil:

$$\frac{d^2u}{dr^2} \approx \frac{u(r+h) - 2u(r) + u(r-h)}{h^2} + O(h²)$$

This transforms the kinetic energy operator into a sparse tridiagonal matrix. The potential V(r) and centrifugal barrier are simply diagonal matrices added on top.

### Implementation in PipeSchrod
```python
pipe = base >> Solve("Matrix")
```

### The Matrix Structure
For a grid of N points, the Hamiltonian H is an N×N matrix. Let T₀ = ℏ² / (2μh²):
- **Diagonal:** Hᵢ,ᵢ = 2T₀ + V(rᵢ) + [L(L+1)] / [2μrᵢ²]
- **Off-diagonal:** Hᵢ,ᵢ±₁ = -T₀

**Pros:** Trivially simple to implement; highly sparse matrix allows very fast exact diagonalisation for massive grids using `scipy.sparse.linalg.eigsh`.
**Cons:** Error scales slowly as O(h²). To get high accuracy, you need a very fine grid (large N), which increases computation time despite sparsity.

<h2 id="numerov">05 Method 2 — Matrix Numerov</h2>

The Numerov algorithm was originally developed for solving second-order ODEs step-by-step (shooting method). In the 1990s, it was recast into a direct matrix eigenvalue approach. It achieves O(h⁴) accuracy using the same three-point stencil, but applying a clever tridiagonal smoothing operator B to the entire equation.

We rewrite the Schrödinger equation as `d²u/dr² = Q(r)u(r)`, where `Q(r) = (2μ/ℏ²)[V(r) + L(L+1)/2μr² - E]`. The Numerov approximation is:

$$\frac{u(r+h) - 2u(r) + u(r-h)}{h^2} = \frac{h^2}{12} \left[ Q(r+h)u(r+h) + 10Q(r)u(r) + Q(r-h)u(r-h) \right] + O(h⁶)$$

### Implementation in PipeSchrod
```python
pipe = base >> Solve("Numerov")
```

### The Matrix Structure
Instead of H·u = E·u, Matrix Numerov yields a generalised eigenvalue problem:
`A·u = E(B·u)`
where A and B are both tridiagonal N×N matrices:
- **Matrix A (Kinetic + Smoothed Potential):**
  `A[i,i] = 2/h² + (5/6)Wᵢ`
  `A[i,i±1] = -1/h² + (1/12)Wᵢ±₁`
  *(where Wᵢ = (2μ/ℏ²)[V(rᵢ) + L(L+1)/2μrᵢ²] )*
- **Matrix B (Smoothing Operator):**
  `B[i,i] = 5/6`
  `B[i,i±1] = 1/12`

**Pros:** Exceptional O(h⁴) accuracy. Reaches high precision with far fewer grid points than the standard method. Still tridiagonal (banded).
**Cons:** Requires solving a generalised eigenvalue problem, which is slightly slower per N than standard diagonalisation.

<h2 id="fgh">06 Method 3 — Fourier Grid Hamiltonian (FGH)</h2>

A radical departure from finite differences. Originally formulated by Marston and Balint-Kurti (1989), FGH uses a discrete Fourier transform to evaluate the kinetic energy exactly in momentum space, then transforms back to coordinate space.

Because momentum p = -iℏ(d/dr), the kinetic energy in momentum space is simply the scalar T = p²/2μ. FGH constructs a matrix that implicitly performs the forward and inverse Fourier transforms algebraically.

### Implementation in PipeSchrod
```python
pipe = base >> Solve("FGH")
```

### The Matrix Structure
Unlike previous methods, FGH generates a **dense** matrix. The potential is diagonal `H[i,i] = V(rᵢ)`, but the kinetic energy T connects every grid point to every other point:

$$T_{i,j} = \frac{\hbar^2}{2\mu h^2} \cdot \frac{(-1)^{i-j}}{\sin^2(\pi(i-j)/N)}$$
*(For i=j, the diagonal is ħ²π² / 6μh²)*

**Pros:** Tremendously accurate — essentially exact for functions that can be represented by the discrete Fourier basis. Often requires the smallest grid N of any method.
**Cons:** The matrix is completely dense (N×N non-zero elements). Memory scales as 𝒪(N²), diagonalisation time scales as 𝒪(N³). Impractical for N > 5000 on standard machines.

<h2 id="salpeter">07 Method 4 — Spinless Salpeter</h2>

The Schrödinger equation is non-relativistic: kinetic energy is p²/2μ. For light quarks, or fast-moving heavy quarks like charm, relativistic effects matter. The Spinless Salpeter equation replaces the non-relativistic kinetic energy with the fully relativistic expression:

$$H = \sqrt{p^2 + m_1^2} + \sqrt{p^2 + m_2^2} + V(r)$$

In coordinate space, the square root of a differential operator √( -∇² + m² ) is non-local and highly non-trivial to evaluate. Lucha and Schöberl (1999) solved this by taking the FGH method and altering only the momentum-space kinetic energy scalar before transforming back to coordinate space.

### Implementation in PipeSchrod
```python
pipe = base >> Solve("Salpeter")
```

### The Matrix Structure
PipeSchrod implements the Lucha–Schöberl algorithm. We generate the momentum grid pₖ = k·Δp, construct the diagonal matrix T[k,k] = √(pₖ² + m₁²) + √(pₖ² + m₂²), and apply the transformation S·T·Sᵀ where S is the sine-transform matrix connecting r-space to p-space. This generates a dense, purely relativistic kinetic energy matrix in coordinate space, to which we add the diagonal V(r).

**Pros:** Computes full relativistic kinematics naturally. The only practical numerical method for the Salpeter equation.
**Cons:** Dense matrix scaling issues (same as FGH). Slightly more overhead to build the transformation matrices.

<h2 id="results">08 Numerical Results & Comparison</h2>

We ran all four methods on the `(m₁=1.4495, m₂=1.4495) + Cornell` charmonium system using a crude grid (N=200, max r=20) to expose convergence differences in extreme conditions.

```python
results = (PipeSchrod(m1=1.4495, m2=1.4495)
           >> Cornell()
           >> Grid(N=200, rmax=20.0)
           >> Solve("all")).data["levels"]
```

| N=   | State | PDG Exp (GeV) | Matrix  | Numerov | FGH     | Salpeter |
| :--- | :---: | :---:         | :---:   | :---:   | :---:   | :---:    |
| 1S   | J/ψ   | 3.096         | 3.1024  | 3.0975  | 3.0974  | 3.0821   |
| 2S   | ψ(2S) | 3.686         | 3.6968  | 3.6896  | 3.6895  | 3.6659   |
| 3S   | ψ(3S) | 4.039         | 4.0621  | 4.0538  | 4.0537  | 4.0315   |

**1. Precision vs Grid:** At a sparse N=200, the Standard Matrix method overshoots the 1S mass by ~5 MeV relative to the true numerical limit of the analytical model. Numerov and FGH nail it near perfectly (3.0974). FGH matches Numerov completely but achieves it through momentum-space Fourier series rather than numerical smoothing.

**2. Relativistic Shift:** The Salpeter method drops the 1S mass by ~15 MeV compared to non-relativistic FGH. This is a pure physical effect! Relativistic kinetic energy √(p²+m²) grows slower than p²/2m at high momenta, yielding tighter binding (lower masses) in the deep funnel of the potential.

**3. Accuracy to Experiment:** Despite taking standard literature parameters, it is striking to see simple Python matrix diagonalisation reproduce the 1974 Nobel prize-winning J/ψ mass to sub-percent precision in milliseconds.

<h2 id="api">09 The PipeSchrod API in Full</h2>

The PipeSchrod pipeline consists of five primary step categories.

### 1. Initialization
`PipeSchrod(m1, m2=None, L=0)`
Initialises the system state. `m1` and `m2` are particle masses in GeV. `L` is orbital angular momentum.

### 2. Potentials
`>> Cornell(alpha=0.5317, b=0.1497, pot_type=1)`
`>> WoodsSaxon(V0=-50, R=1.25, a=0.65)`
`>> HarmonicOscillator(omega=1.0)`
Adds a potential energy term to the state. Custom parameter values can be passed.

### 3. Grid
`>> Grid(N=1000, rmin=0.001, rmax=20.0)`
Discretises the radial coordinate space. Controls computational precision and scaling.

### 4. Solvers
`>> Solve(method="Matrix")`  (Options: `"Matrix"`, `"Numerov"`, `"FGH"`, `"Salpeter"`, `"all"`)
Executes diagonalisation. Solvers can be chained consecutively or branched. Results are attached to the output object's `.data` dictionary.

### 5. Outputs
`>> Print()` — Pretty-prints tabulated energy levels to console.
`>> Compare()` — Displays table contrasting multiple solvers if `"all"` was run.
`>> Plot(style="dashboard")` — Renders Plotly visualisations. Options: `"Wavefunctions"`, `"Potential"`, `"dashboard"`.
`>> Export(fmt="csv", path="out.csv")` — Saves levels and wavefunctions.

<h2 id="conclusion">10 Conclusion</h2>

Numerical solution of the Schrödinger equation is no longer the domain of Fortran 77 monoliths. By recasting the differential equation into sparse, smoothed, or Fourier-transformed matrices, we can construct the charmonium spectrum instantly.

**PipeSchrod** unifies these techniques behind an immutable, fluent Python API. Whether you are teaching undergraduate quantum mechanics or scanning parameters for heavy quarkonia phenomenology, the `>>` pipeline handles the matrix algebra, letting you focus entirely on the physics.

<hr class="rule">

**PipeSchrod Repository:** [github.com/Yasser03/pipeschrod](https://github.com/Yasser03/pipeschrod)
**Author:** Dr. Yasser Mustafa
