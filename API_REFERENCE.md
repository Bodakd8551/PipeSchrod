# API Reference 📚

Welcome to the comprehensive API Reference for `PipeSchrod`, the pipeline-based Python library for solving 1D Schrödinger and Salpeter equations.

> [!TIP]
> **No installation required?** Explore the **PipeSchrod Lab** directly in your browser: [Launch Online](https://pipeschrod.streamlit.app/)

## Core Module: Base Initialization

### `PipeSchrod`
Initializes the physical system and establishes the pipeline context.
```python
PipeSchrod(m1, m2=None, L=0, n=0, name="System")
```
- **`m1`** *(float)*: Mass of particle 1 (or the reduced mass if `m2` is Omitted) [GeV].
- **`m2`** *(float, optional)*: Mass of particle 2 [GeV]. If provided, the effective mass μ = (m₁m₂)/(m₁+m₂) is calculated.
- **`L`** *(int, default=0)*: Orbital angular momentum quantum number (centrifugal term).
- **`n`** *(int, default=0)*: Principal quantum number (used for labeling).
- **`name`** *(str, optional)*: A custom name for the system.

---

## Grid Configuration

### `Grid`
Defines the spatial discretization of the coordinate r.
```python
Grid(N=200, rmax=20.0, r0=1e-5)
```
- **`N`** *(int)*: Number of grid points.
- **`rmax`** *(float)*: Maximum coordinate extent [GeV⁻¹].
- **`r0`** *(float)*: Origin cutoff to avoid potential singularities at r = 0.

---

## Potential Models

These verbs inject a specific V(r) into the pipeline logic.

### `Cornell`
Creates a Cornell potential, widely used in quarkonium models:

$$V(r) = - \frac{4\alpha}{3r} + br$$
```python
Cornell(alpha=0.5317, b=0.1497, pot_type=1)
```
- **`alpha`** *(float)*: Strong coupling constant.
- **`b`** *(float)*: String tension parameter.
- **`pot_type`** *(int)*: Defines variants of the Coulomb and linear term combinations.

### `Harmonic`
Applies a generic Harmonic Oscillator potential:

$$V(r) = \frac{1}{2} m \omega^2 r^2$$
```python
Harmonic(omega=1.0)
```
- **`omega`** *(float)*: Angular frequency of the oscillator.

### `Coulomb`
Applies a strictly Coulombic potential target (Hydrogen-like):

$$V(r) = - \frac{Z}{r}$$
```python
Coulomb(Z=1.0)
```
- **`Z`** *(float)*: Effective atomic number or generic charge coefficient.

### `WoodsSaxon`
A standard phenomenological model for nucleons:

$$V(r) = \frac{-V_0}{1 + \exp((r - R)/a)}$$
```python
WoodsSaxon(V0=50.0, R=1.2, a=0.65)
```
- **`V0`** *(float)*: Well depth.
- **`R`** *(float)*: Nuclear radius.
- **`a`** *(float)*: Surface thickness modifier.

### `Morse`
An accurate model for diatomic molecular vibrations:

$$V(r) = D_e (1 - e^{-a(r-r_e)})^2$$
```python
Morse(De=1.0, re=1.0, a=1.0)
```
- **`De`** *(float)*: Well depth (dissociation energy).
- **`re`** *(float)*: Equilibrium bond length.
- **`a`** *(float)*: Potential well width control.

---

## Numerical Solvers

### `Solve`
Constructs and evaluates the Hamiltonian across the grid.
```python
Solve(*methods)
```
- **`*methods`** *(str)*: A sequence of solver names. Available options:
  - `"Matrix"` (Standard Matrix method, 𝒪(h²))
  - `"Numerov"` (Matrix Numerov, 𝒪(h⁴))
  - `"FGH"` (Fourier Grid Hamiltonian, 𝒪(h⁶), highly convergent)
  - `"Salpeter"` (Spinless Salpeter solving √(m² + p²))
  - `"all"` (Solves using all available methods in parallel)

---

## Output and Diagnostics

### `Compare`
Outputs a direct console-based comparison of eigenvalue results from multiple solvers.
```python
Compare(n_states=5)
```
- **`n_states`** *(int)*: Limits how many bound states to print per solver.

### `Summary`
Prints localized eigenvalue logic and details for the first active dataset within the pipe's result payload.
```python
Summary(n_states=5)
```

---

## Visualizations

### `Plot`
Triggers integrated `matplotlib` visualizations directly inline with your code.
```python
Plot(*targets, save=None)
```
- **`*targets`** *(str)*: Which plot components to generate:
  - `"dashboard"`: A primary 4-panel breakdown.
  - `"wavefunctions"`: Core 1st/2nd/3rd bound wavefunctions.
  - `"densities"`: Plot of probability volume |u(r)|².
  - `"potential"`: View V(r) and mapped Eigenstates.
  - `"spectrum"`: Bar charts showing mass distributions.
  - `"compare_wf"`: Overlaps `1S` wavefunction shapes across all tested solvers.
  - `"compare_E"`: Group bar charts of resulting energy thresholds.
  - `"all"`: Fires every single available plot type sequentially.
- **`save`** *(str, optional)*: If provided, dictates the output folder to save the generated PNGs.

---

## Data Operations

### `Export`
Bridges your calculated pipeline back into raw, usable data formats.
```python
Export(fmt, path=None)
```
- **`fmt`** *(str)*: Output structure format. Available options:
  - `"csv"` (General array output)
  - `"json"` (Export results property map as JSON)
  - `"csv_compare"` (Merge multi-solver results directly to CSV matrix)
- **`path`** *(str)*: Target path filename (e.g. `"results.csv"`).

---

**Created by**: [Dr. Yasser Mustafa](https://www.linkedin.com/in/yasser-mustafa-ai/)
