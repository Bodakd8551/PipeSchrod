# PipeSchrod ⚛️

**Pipe Your Quantum Mechanics Naturally**

[![PyPI version](https://img.shields.io/pypi/v/pipeschrod.svg)](https://pypi.org/project/pipeschrod/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intuitive, readable, and modern Python library for defining, solving, and visualizing 1D Schrödinger and Salpeter equations. Designed for nuclear physicists, particle physicists, and quantum mechanics students, PipeSchrod implements a clear pipeline syntax (`>>`) inspired by standard data workflows but applied to rigorous physical systems.

```python
from pipeschrod import PipeSchrod
from pipeschrod.steps import Cornell, Grid, Solve, Plot, Export

# Your quantum pipeline reads like a recipe
result = (PipeSchrod(m1=1.4495, m2=1.4495)
    >> Cornell(alpha=0.5317, b=0.1497)
    >> Grid(N=200, rmax=20.0)
    >> Solve("FGH")
    >> Plot("dashboard")
    >> Export("csv", path="charmonium.csv")
)
```

> **💡 How to read `>>`:** Read the `>>` operator as **"pipe to"** or **"then"**. For example, the code above reads as: *"Initialize the PipeSchrod system, **then** apply a Cornell Potential, **then** attach a Grid, **then** Solve it utilizing FGH..."*

---

## 🌟 Why PipeSchrod?

### **Readability First**
```python
# ❌ Traditional Logic: Nested definitions across dozens of lines
import numpy as np
# ... build matrices ...
# ... implement custom potential ...
# ... build boundary conditions ...
# ... retrieve eigensystems ...

# ✅ PipeSchrod: Clear, reproducible, and intuitive execution
PipeSchrod(m1=4.67, m2=4.67) >> Cornell(0.471, 0.192) >> Grid(N=200, rmax=20) >> Solve('Salpeter')
```

### **Key Features**
- 🔗 **Pipe Operator `>>`** - Streamline quantum definitions and model solvers intuitively.
- 🌌 **Broad Potential Support** - Ready-to-go `Cornell`, `Harmonic`, `Coulomb`, `WoodsSaxon`, and `Morse` limits.
- 🧮 **Advanced Precision Solvers** - Run Standard Matrix ($O(h^2)$), Matrix Numerov ($O(h^4)$), Fourier Grid Hamiltonian ($O(h^6)$), and Salpeter Relativistic numerical methods.
- 📊 **Rich Visualization** - Native, automated matplotlib plotting targets inside the pipeline (spectra, wavefunctions, and densities).
- 💾 **Data Interoperability** - Export natively calculated matrices into datasets via `.json` or `.csv`.
- ⚡ **Highly Cached Properties** - Rapid property-fetching after solve pipelines.

---

## 🚀 Quick Start

### Installation
```bash
# Basic installation via PyPI
pip install pipeschrod

# Install from source
git clone https://github.com/Yasser03/PipeSchrod.git
cd PipeSchrod
pip install -e .
```

### Hello Quantum World!
```python
from pipeschrod import PipeSchrod
from pipeschrod.steps import Harmonic, Grid, Solve, Plot

# A simple Harmonic Oscillator pipeline
oscillator = (
    PipeSchrod(m1=1.0)
    >> Harmonic(omega=1.0)
    >> Grid(N=200, rmax=10.0)
    >> Solve("Matrix", "Numerov") # Run two solvers sequentially
    >> Plot("wavefunctions")      # Graph the resulting states
)

print(oscillator.result.bound_energies[:3])
# [0.5, 1.5, 2.5]
```

---

## 📚 Core Concepts

### The Pipe Operator `>>`
The Pipe allows you to define configurations on the fly without modifying base templates, generating unique executions quickly and repeatedly:

```python
# Define baseline environment
environment = PipeSchrod(m1=1.4495) >> Grid(N=200, rmax=20.0)

# Branch multiple specific scenarios without rewriting initial components
result_harmonic = environment >> Harmonic(1.0) >> Solve("FGH")
result_coulomb  = environment >> Coulomb(1.0) >> Solve("FGH")
```

### Core Verbs

| Verb | Purpose | Example |
|------|---------|---------|
| `PipeSchrod()` | Origin Initialization | `PipeSchrod(m1=1.44, m2=1.44)` |
| `Cornell()` | Set Potential | `>> Cornell(alpha=0.5, b=0.1)` |
| `Grid()` | Configure Grid Map | `>> Grid(N=200, rmax=20.0)` |
| `Solve()` | Apply Solvers | `>> Solve("FGH", "Salpeter")` |
| `Summary()` | Print Output | `>> Summary(n_states=5)` |
| `Plot()` | Visual Dashboard | `>> Plot("dashboard", "spectrum")` |
| `Compare()` | Solver Differences | `>> Compare()` |
| `Export()` | Save results | `>> Export("json", path="data.json")` |

> *For a full overview of verb arguments and potential functions, see the [API Reference](API_REFERENCE.md)*

---

## 📖 Related Projects

PipeSchrod is part of the **Pipe** ecosystem emphasizing readable, pipeline-centric processing:
- [PipeFrame](https://github.com/Yasser03/pipeframe) - DataFrame manipulation using python pipes.
- [PipePlotly](https://github.com/Yasser03/pipeplotly) - Grammar-of-graphics charting using python pipes.
- [PipeScrape](https://github.com/Yasser03/pipescraper) - Structural web scraping using python pipes.

---

## 📈 Roadmap

### Current (v0.1.0)
- ✅ Standard non-relativistic solvers (Matrix, Numerov, FGH)
- ✅ Spinless Salpeter
- ✅ Matplotlib auto-dashboard capabilities
- ✅ 5 native potential models

### Upcoming (v0.2.0)
- [ ] Direct Plotly integration for interactive charts.
- [ ] Real-time UI controls and widgets directly natively attached to output models.
- [ ] Distributed batch solving for massive variable sweeps.
