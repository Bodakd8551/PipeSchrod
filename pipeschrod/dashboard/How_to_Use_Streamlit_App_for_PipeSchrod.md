# ⚛️ PipeSchrod Interactive Lab: User Guide

### 🌐 Cloud Access (No Setup Required)
If you just want to explore PipeSchrod without installing anything locally, launch the hosted lab here:
👉 **[Launch PipeSchrod Lab Online](https://pipeschrod.streamlit.app/)**

---

Welcome to the official documentation for the **PipeSchrod Streamlit App**. This interactive dashboard allows physicists, students, and researchers to visualize and solve quantum bound-state problems naturally using the PipeSchrod ecosystem.

---

## 🛠️ Prerequisites

Before running the lab, ensure you have the necessary dependencies installed:

```bash
# Recommended: Install the production package
pip install pipeschrod

# Or for development (from the repo root)
pip install -e .
```

---

## 🚀 Launching the App

There are two primary ways to start the Interactive Lab:

### 1. Native CLI (Recommended)
This is the standard and fastest method. Once installed via `pip` or `uv`, simply run:
```bash
pipeschrod-lab
```

### 2. Manual Terminal Launch
If you are running directly from source without installing, run the following from the root directory:
```bash
uv run python -m pipeschrod.cli
```
*Or using standard python:*
```bash
python -m pipeschrod.cli
```

> [!IMPORTANT]
> If you encounter a `ModuleNotFoundError: No module named 'streamlit.cli'`, always use the `python -m streamlit` prefix as shown above.

---

## 🎨 Features & Capabilities

### 1. **System Configuration**
Set the physical properties of your quantum system in the sidebar:
*   **Masses (m₁, m₂):** Define the constituent masses (e.g., 1.4495 GeV for Charm quarks).
*   **Quantum Numbers:** Adjust Orbital (L), Spin (S), and total angular momentum (J).

### 2. **Potential Model Selection**
Choose from five industry-standard physical models:
*   **Cornell**: Standard funnel potential for quarkonium simulations (V = -4α/3r + br).
*   **Harmonic Oscillator**: Exactly solvable benchmark model.
*   **Coulomb**: Hydrogen-like systems.
*   **Woods-Saxon**: Phenomenological nuclear well model.
*   **Morse**: Diatomic molecular vibration model.

### 3. **Numerical Solvers**
Select one or more advanced numerical methods to compute the spectrum:
*   **FGH (Fourier Grid Hamiltonian)**: High-precision spectral method (𝒪(h⁶)).
*   **Matrix**: Fast 𝒪(h²) matrix discretization.
*   **Numerov**: High-accuracy 𝒪(h⁴) integration method.
*   **Spinless Salpeter**: Relativistic treatment for heavy systems.

### 4. **Visualization Suite**
Explore your results through interactive tabs:
*   **📊 Summary**: Tabular view of bound-state energies and radii.
*   **📈 Dashboard**: 4-panel overview of the entire system.
*   **🌊 Wavefunctions**: High-fidelity plots of radial wavefunctions and probability densities.
*   **🛡️ Potential**: Visualization of the potential well with energy levels overlaid.
*   **⚖️ Comparison**: Side-by-side comparison of results if multiple solvers were selected.

### 5. **Data Export**
Download your simulation results for external use:
*   **CSV**: Individual solver data tables.
*   **JSON**: Comprehensive system-wide configuration and results snapshot.

---

## 💡 Pro Tips
*   **Grid Accuracy**: For deep potentials or highly excited states, increase the **Number of Points (N)** to 300-500.
*   **Convergence**: Use the **Comparison** tab to check if different solvers agree on the ground-state energy; if they differ significantly, try increasing N or Rₘₐₓ.

---

## 📑 Conclusion
The PipeSchrod Interactive Lab is designed to make quantum mechanics exploration intuitive and visual. 

**Happy Computing!** ⚛️

---

**Created by**: [Dr. Yasser Mustafa](https://www.linkedin.com/in/yasser-mustafa-ai/)