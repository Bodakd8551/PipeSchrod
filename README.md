# PipeSchrod ⚛️

**Pipe Your Quantum Mechanics Naturally**

[![PyPI version](https://img.shields.io/badge/pypi-v1.1.4-blue?logo=pypi&logoColor=white)](https://pypi.org/project/pipeschrod/)
[![Python version](https://img.shields.io/badge/python-3.8+-blue?logo=python&logoColor=white)](https://pypi.org/project/pipeschrod/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow?logo=opensourceinitiative&logoColor=white)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-active-green?logo=github&logoColor=white)](https://github.com/Yasser03/pipeschrod)

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
- 🧮 **Advanced Precision Solvers** - Run Standard Matrix (𝒪(h²)), Matrix Numerov (𝒪(h⁴)), Fourier Grid Hamiltonian (𝒪(h⁶)), and Salpeter Relativistic numerical methods.
- 📊 **Rich Visualization** - Native, automated matplotlib plotting targets inside the pipeline (spectra, wavefunctions, and densities).
- 💾 **Data Interoperability** - Export natively calculated matrices into datasets via `.json` or `.csv`.
- ⚡ **Highly Cached Properties** - Rapid property-fetching after solve pipelines.

---

## 🚀 Quick Start

### Installation
```bash
# Recommended: Install directly from PyPI
pip install pipeschrod

# Or using uv for lightning fast setup
uv pip install pipeschrod
```

### Native CLI
Once installed, you can launch the **PipeSchrod Lab** dashboard from anywhere using the built-in command:
```bash
pipeschrod-lab
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

## 🪐 Potential Models

PipeSchrod comes with several built-in physical potentials, each implemented as an independent pipe step. Here is how to configure and use them:

### `Cornell`
Creates a Cornell potential, widely used in quarkonium models:

$$V(r) = - \frac{4\alpha}{3r} + br$$
```python
# Create a charmonium system using the Cornell potential with spin-orbit coupling
PipeSchrod(m1=1.44) >> Cornell(alpha=0.5317, b=0.1497, pot_type=3, S=1, J=1)
```
- **`alpha`** *(float)*: Strong coupling constant.
- **`b`** *(float)*: String tension parameter.
- **`pot_type`** *(int)*: Defines variants of the potential interactions:
  - `1`: Standard Coulomb + Linear (default).
  - `2`: Type 1 + Gaussian-smeared hyperfine interactions.
  - `3`: Type 2 + Spin-orbit coupling + Tensor force.
- **`sigma`** *(float)*: Gaussian smearing parameter for hyperfine terms (used in `pot_type >= 2`).
- **`S`, `J`** *(int)*: Total spin and total angular momentum quantum numbers (used in `pot_type >= 3`).

### `Harmonic`
Applies a generic Harmonic Oscillator potential:

$$V(r) = \frac{1}{2} m \omega^2 r^2$$
```python
PipeSchrod(m1=1.0) >> Harmonic(omega=1.0)
```
- **`omega`** *(float)*: Angular frequency of the oscillator.

### `Coulomb`
Applies a strictly Coulombic potential target (Hydrogen-like):

$$V(r) = - \frac{Z}{r}$$
```python
# Hydrogen-like system
PipeSchrod(m1=0.511) >> Coulomb(Z=1.0)
```
- **`Z`** *(float)*: Effective atomic number or generic charge coefficient.

### `WoodsSaxon`
A standard phenomenological model for nucleons:

$$V(r) = \frac{-V_0}{1 + \exp((r - R)/a)}$$
```python
PipeSchrod(m1=938.0) >> WoodsSaxon(V0=50.0, R=1.2, a=0.65)
```
- **`V0`** *(float)*: Well depth.
- **`R`** *(float)*: Nuclear radius.
- **`a`** *(float)*: Surface thickness modifier.

### `Morse`
An accurate model for diatomic molecular vibrations:

$$V(r) = D_e (1 - e^{-a(r-r_e)})^2$$
```python
PipeSchrod(m1=1.0) >> Morse(De=1.0, re=1.0, a=1.0)
```
- **`De`** *(float)*: Well depth (dissociation energy).
- **`re`** *(float)*: Equilibrium bond length.
- **`a`** *(float)*: Potential well width control.

---

## 🔥 Advanced Features

### Multi-Solver Parallelism
```python
# Solve the same grid across 4 different numerical methods simultaneously
system = (PipeSchrod(m1=1.4495)
    >> Cornell(0.5317, 0.1497)
    >> Grid(200, 20.0)
    >> Solve("Matrix", "Numerov", "FGH", "Salpeter")
    >> Compare() # Immediately view console matrix of diffs
)
```

### Automated Dashboards
```python
# Launch complex matplotlib graphs seamlessly inline
(system 
    >> Plot("wavefunctions") # individual plot
    >> Plot("spectrum")      # individual plot
    >> Plot("dashboard")     # 4-panel comprehensive view
)
```

### Result Persistence
```python
# Convert calculation matrices instantly to CSV
system >> Export("csv_compare", path="all_solvers.csv")
```

---

## 🎯 Real-World Examples

### Charmonium Mass Spectrum
```python
from pipeschrod import PipeSchrod
from pipeschrod.steps import Cornell, Grid, Solve, Plot

charmonium = (
    PipeSchrod(m1=1.4495, m2=1.4495)
    >> Cornell(alpha=0.5317, b=0.1497, pot_type=1)
    >> Grid(N=200, rmax=20.0)
    >> Solve("FGH", "Salpeter")
    >> Plot("spectrum", "compare_wf", save="./figures")
)
```

### Bottomonium Parameter Sweep
```python
base_environment = PipeSchrod(m1=4.67, m2=4.67) >> Grid(N=200, rmax=20.0)

# Quickly iterate alpha constants
result_1 = base_environment >> Cornell(alpha=0.450, b=0.192) >> Solve("FGH")
result_2 = base_environment >> Cornell(alpha=0.471, b=0.192) >> Solve("FGH")
```

---

## 📊 Performance

PipeSchrod adds minimal overhead to complex mathematical arrays while dramatically improving code readability:

**Benchmarks:**
- **Matrix Solver**: Fastest build execution, relies precisely on 𝒪(h²) step increments.
- **Numerov Solver**: Deep integration 𝒪(h⁴) bounds reducing standard node drifts.
- **Fourier Grid Hamiltonian (FGH)**: Superior convergence parameters using a 3-point or 5-point 𝒪(h⁶) spectral analysis matrix.
- **Spinless Salpeter**: Relativistic momentum computations calculated through discrete pseudo-spectral array layouts over heavy quark masses.

**Why the syntax overhead is worth it:**
- 🧠 Reduced cognitive load when comparing results
- 🐛 Fewer bugs from isolated variable scoping
- ⚡ Faster solver switching & prototyping
- 📚 Better script reusability

---

## 🎓 Learning Resources
- **[Tutorial Notebook](tutorial.ipynb)** - A complete, hands-on walkthrough exposing every verb.
- **[API Reference](API_REFERENCE.md)** - Detailed core documentation for all variables and potential models.
- **[Theoretical Details](pipeschrod_medium_article.md)** - Contains details on the theoretical part of the matrix methods.
- **[Examples](examples/)** - More advanced usage templates.

## ⚛️ Interactive Lab

The **PipeSchrod Interactive Lab** allows you to investigate quantum systems visually and see real-time spectroscopic results.

### 🌐 Cloud Access (No Setup Required)
For researchers and students who prefer not to install Python locally, the lab is hosted on the Streamlit Cloud:
👉 **[Launch PipeSchrod Lab Online](https://pipeschrod.streamlit.app/)**

### 💻 Local Execution
If you have the package installed, you can launch the lab from any terminal:
```bash
pipeschrod-lab
```
For more details, see the [Interactive Lab Instructions](pipeschrod/dashboard/How_to_Use_Streamlit_App_for_PipeSchrod.md).

---

## 🤝 Contributing
Contributions are extremely welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/advanced-potential`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/advanced-potential`)
5. Open a Pull Request

---

## 📜 License
MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📖 Related Projects

PipeSchrod is part of the **Pipe** ecosystem emphasizing readable, pipeline-centric processing:
- [PipeFrame](https://github.com/Yasser03/pipeframe) - DataFrame manipulation using python pipes.
- [PipePlotly](https://github.com/Yasser03/pipeplotly) - Grammar-of-graphics charting using python pipes.
- [PipeScrape](https://github.com/Yasser03/pipescraper) - Structural web scraping using python pipes.

---

## 📝 How to Cite

If you use PipeSchrod in your research or educational materials, please cite it as follows:

```bibtex
@software{pipeschrod,
  author = {Mustafa, Yasser},
  title = {PipeSchrod: Pipe Your Quantum Mechanics Naturally},
  url = {https://github.com/Yasser03/PipeSchrod},
  year = {2026}
}
```

---

## 🌟 Star History
If PipeSchrod helps your research or calculations, please consider giving it a star! ⭐

---

## 📈 Roadmap

### Current (v1.1.1)
- ✅ Dashboard Bugfix Release: Corrected CLI path resolution
- ✅ Integrated Dashboard into the core package structure
- ✅ Modern PyPI Package structure (`pyproject.toml`)
- ✅ Standard non-relativistic solvers (Matrix, Numerov, FGH)
- ✅ Spinless Salpeter
- ✅ Matplotlib auto-dashboard capabilities
- ✅ 5 native potential models

### Upcoming (v1.2.0)
- [ ] Direct Plotly integration for interactive charts.
- [ ] Distributed batch solving for massive variable sweeps.
- [ ] Expanded potential library (Hulthén, Yukaua).

---

## 👨‍💻 Author
**Dr. Yasser Mustafa**

*AI & Data Science Specialist | Theoretical Physics PhD*

- 🎓 PhD in Theoretical Nuclear Physics
- 💼 10+ years in production AI/ML systems
- 🔬 48+ research publications
- 🏢 Experience: Government (Abu Dhabi), Media (Track24), Recruitment (Reed), Energy (ADNOC)
- 📍 Based in Newcastle Upon Tyne, UK
- ✉️ yasser.mustafan@gmail.com
- 🔗 [LinkedIn](https://www.linkedin.com/in/yasser-mustafa-ai/) | [GitHub](https://github.com/Yasser03)

**PipeSchrod** was born from the need for a more intuitive, pipe-based approach to defining and solving quantum mechanical bound-state systems, combining the analytical rigor of numerical solvers with the elegance of modern functional programming interfaces.

---

## 💬 Community
- **Issues**: Report bugs or request features
- **Discussions**: Ask questions, share use cases

**Built with ❤️ for physicists and educators who value readability**

*Pipeline your quantum states naturally with PipeSchrod ⚛️*
