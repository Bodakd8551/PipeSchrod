import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Ensure local pipeschrod can be imported from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeschrod import PipeSchrod
from pipeschrod.steps import (Cornell, Harmonic, Coulomb, WoodsSaxon, Morse, 
                               Grid, Solve, Summary)
from pipeschrod.plotter import SchrodPlotter

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="PipeSchrod ⚛️ Interactive Lab",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main {
        background-color: #0d1117;
        color: #e6edf3;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #238636;
        color: white;
    }
    .stExpander {
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: SYSTEM PARAMETERS ---
st.sidebar.header("⚛️ System Configuration")
with st.sidebar.expander("Physical Constants", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        m1 = st.number_input("Mass 1 (m1) [GeV]", value=1.4495, format="%.4f")
        L = st.number_input("Orbital (L)", value=0, min_value=0)
    with col2:
        m2 = st.number_input("Mass 2 (m2) [GeV]", value=1.4495, format="%.4f")
        S = st.number_input("Spin (S)", value=1, min_value=0)
    J = st.sidebar.number_input("Total J", value=1, min_value=0)

# --- SIDEBAR: POTENTIAL SELECTION ---
st.sidebar.header("🌌 Potential Model")
pot_type_choice = st.sidebar.selectbox(
    "Select Model",
    options=["Cornell", "Harmonic", "Coulomb", "Woods-Saxon", "Morse"]
)

pot_step = None
if pot_type_choice == "Cornell":
    with st.sidebar.expander("Cornell Parameters", expanded=True):
        alpha = st.number_input("Alpha (α)", value=0.5317, format="%.4f")
        b = st.number_input("String Tension (b)", value=0.1497, format="%.4f")
        v_type = st.number_input("Pot Type (1-3)", value=1, min_value=1, max_value=3)
        pot_step = Cornell(alpha=alpha, b=b, pot_type=v_type)
        st.caption("V(r) = -4α/3r + br")

elif pot_type_choice == "Harmonic":
    with st.sidebar.expander("Harmonic Parameters", expanded=True):
        omega = st.number_input("Omega (ω)", value=1.0, format="%.2f")
        pot_step = Harmonic(omega=omega, mass=(m1*m2)/(m1+m2) if m1+m2 > 0 else 1.0)
        st.caption("V(r) = ½μω²r²")

elif pot_type_choice == "Coulomb":
    with st.sidebar.expander("Coulomb Parameters", expanded=True):
        Z = st.number_input("Target Charge (Z)", value=1.0, format="%.2f")
        pot_step = Coulomb(Z=Z)
        st.caption("V(r) = -Zα/r")

elif pot_type_choice == "Woods-Saxon":
    with st.sidebar.expander("Woods-Saxon Parameters", expanded=True):
        V0 = st.number_input("Well Depth (V0)", value=0.05, format="%.3f")
        R = st.number_input("Radius (R)", value=5.0, format="%.2f")
        a = st.number_input("Thickness (a)", value=0.6, format="%.2f")
        pot_step = WoodsSaxon(V0=V0, R=R, a=a)
        st.caption("V(r) = -V0 / (1 + exp((r-R)/a))")

elif pot_type_choice == "Morse":
    with st.sidebar.expander("Morse Parameters", expanded=True):
        De = st.number_input("Well Depth (De)", value=0.3, format="%.3f")
        re = st.number_input("Equil. Path (re)", value=2.0, format="%.2f")
        a_morse = st.number_input("Width (a)", value=0.5, format="%.2f")
        pot_step = Morse(De=De, re=re, a=a_morse)
        st.caption("V(r) = De(1 - exp(-a(r-re)))²")

# --- SIDEBAR: GRID & SOLVERS ---
st.sidebar.header("🧮 Numerical Settings")
with st.sidebar.expander("Grid Configuration"):
    N_points = st.slider("Number of Points (N)", 50, 500, 200)
    rmax = st.number_input("R Max [GeV⁻¹]", value=20.0, format="%.1f")

st.sidebar.header("🚀 Solvers")
available_solvers = ["FGH", "Matrix", "Numerov", "Salpeter"]
selected_solvers = st.sidebar.multiselect("Select Methods", available_solvers, default=["FGH"])

# --- MAIN PAGE CONTENT ---
st.title("PipeSchrod ⚛️ Simulation Dashboard")
st.markdown("""
Welcome to the **PipeSchrod Lab**. This dashboard allows you to investigate quantum bound states 
for various physical potentials using the pipeline syntax.
""")

if not selected_solvers:
    st.warning("⚠️ Please select at least one solver in the sidebar.")
    st.stop()

if st.sidebar.button("Run Simulation"):
    with st.status("Solving Schrödinger Equation...", expanded=True) as status:
        st.write("Initializing Pipeline...")
        pipe = PipeSchrod(m1=m1, m2=m2, L=L, S=S, J=J)
        
        st.write(f"Applying {pot_type_choice} Potential...")
        pipe = pipe >> pot_step
        
        st.write("Configuring Grid...")
        pipe = pipe >> Grid(N=N_points, rmax=rmax)
        
        st.write(f"Running Solvers: {', '.join(selected_solvers)}...")
        pipe = pipe >> Solve(*selected_solvers)
        
        status.update(label="Simulation Complete!", state="complete", expanded=False)

    res_dict = pipe.results
    active_method = pipe.result.method if pipe.result else None
    
    tabs = st.tabs(["📊 Summary", "📈 Dashboard", "🌊 Wavefunctions", "🛡️ Potential", "⚖️ Comparison", "💾 Export"])
    
    with tabs[0]:
        st.subheader(f"Summary Table ({active_method})")
        res = res_dict[active_method]
        
        # Build DataFrame for display
        df = pd.DataFrame({
            "State": [res.state_label(i) for i in range(res.n_bound)],
            "Energy (GeV)": [res.bound_energies[i] for i in range(res.n_bound)],
            "Binding E (MeV)": [res.binding_energies_mev[i] for i in range(res.n_bound)],
            "RMS Radius (GeV⁻¹)": [res.rms_radius(i) for i in range(res.n_bound)],
            "Nodes": [res.node_count(i) for i in range(res.n_bound)]
        })
        st.dataframe(df.style.format({"Energy (GeV)": "{:.6f}", "Binding E (MeV)": "{:.2f}", "RMS Radius (GeV⁻¹)": "{:.4f}"}), use_container_width=True)
        
        col_m1, col_m2, col_mu = st.columns(3)
        col_m1.metric("m1", f"{m1} GeV")
        col_m2.metric("m2", f"{m2} GeV")
        col_mu.metric("Reduced Mass (μ)", f"{(m1*m2)/(m1+m2):.4f} GeV" if m1+m2 > 0 else "N/A")

    with tabs[1]:
        st.subheader("All-in-one Dashboard")
        plotter = SchrodPlotter(res)
        fig, _ = plotter.dashboard()
        if fig:
            st.pyplot(fig)

    with tabs[2]:
        st.subheader("Radial Wavefunctions")
        plotter = SchrodPlotter(res)
        fig, _ = plotter.wave_functions(n_states=6)
        if fig:
            st.pyplot(fig)
            
        st.subheader("Probability Densities")
        fig2, _ = plotter.probability_densities(n_states=6)
        if fig2:
            st.pyplot(fig2)

    with tabs[3]:
        st.subheader("Potential and Bound Levels")
        plotter = SchrodPlotter(res)
        fig, _ = plotter.potential_and_levels(n_levels=6)
        if fig:
            st.pyplot(fig)

    with tabs[4]:
        st.subheader("Method Comparison")
        if len(selected_solvers) > 1:
            plotter_multi = SchrodPlotter(res_dict)
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                fig_e, _ = plotter_multi.compare_energies()
                st.pyplot(fig_e)
            with col_c2:
                fig_wf, _ = plotter_multi.compare_wave_functions(n=0)
                st.pyplot(fig_wf)
                
            # Comparison Table
            comp_data = []
            for i in range(min(4, res.n_bound)):
                row = {"State": res.state_label(i)}
                for m in selected_solvers:
                    row[m] = res_dict[m].bound_energies[i]
                comp_data.append(row)
            st.table(pd.DataFrame(comp_data))
        else:
            st.info("Select multiple solvers in the sidebar to view comparison.")

    with tabs[5]:
        st.subheader("Export Results")
        
        # CSV Export
        for m in selected_solvers:
            res_m = res_dict[m]
            df_m = pd.DataFrame({
                "n": range(1, res_m.n_bound + 1),
                "Energy_GeV": res_m.bound_energies
            })
            csv = df_m.to_csv(index=False)
            st.download_button(
                label=f"Download {m} Results (CSV)",
                data=csv,
                file_name=f"pipeschrod_{m}_results.csv",
                mime='text/csv'
            )
            
        # JSON Export
        import json
        all_data = {
            "system": {"m1": m1, "m2": m2, "L": L, "S": S, "J": J},
            "potential": {"name": pot_type_choice},
            "results": {m: {"energies": res_dict[m].bound_energies.tolist()} for m in selected_solvers}
        }
        st.download_button(
            label="Download All Results (JSON)",
            data=json.dumps(all_data, indent=4),
            file_name="pipeschrod_full_results.json",
            mime='application/json'
        )

else:
    st.info("💡 Adjust parameters in the sidebar and click **Run Simulation** to begin.")
    
    # Show a preview image or description
    # st.image("https://img.shields.io/badge/Status-Ready-brightgreen") # Removing potentially broken link
    st.markdown("""
    ### Quick Guide:
    1. **System Config**: Set the masses of the particles (e.g., 1.45 GeV for Charm quarks).
    2. **Potential**: Choose a physical model. **Cornell** is standard for quarkonium.
    3. **Numerical Settings**: FGH is usually the most accurate solver.
    4. **Tabs**: Once solved, flip through the tabs to see different physical properties.
    """)