# ⚛️ PipeSchrod Interactive Lab: User Guide

Welcome to the official documentation for the **PipeSchrod Streamlit App**. This interactive dashboard allows physicists, students, and researchers to visualize and solve quantum bound-state problems naturally using the PipeSchrod ecosystem.

---

## 🛠️ Prerequisites

Before running the lab, ensure you have the necessary dependencies installed:

```bash
# Install the core library and dashboard requirements
pip install -r requirements.txt

# Or manually install the essentials
pip install streamlit pandas matplotlib pipeschrod
```

---

## 🚀 Launching the App

There are two primary ways to start the Interactive Lab:

### 1. The Quick Start (Recommended for Windows)
Double-click the **`run_lab.bat`** file in the root directory. This script automatically handles environment paths and bypasses common Streamlit CLI versioning errors.

### 2. Manual Terminal Launch
Run the following command in your terminal from the repository root:
```bash
python -m streamlit run dashboard/streamlit_app.py
```

### 3. Native CLI (Recommended after installation)
If you have installed the package via `pip install -e .` or simply `pip install pipeschrod`, you can launch the lab from anywhere using:
```bash
pipeschrod-lab
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