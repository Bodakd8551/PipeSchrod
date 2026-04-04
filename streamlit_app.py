import streamlit as st

# Title
st.title("PipeSchrod Simulation App")

# Sidebar for user input
st.sidebar.header("Customize Simulation Parameters")

# Parameters for customization
def get_user_inputs():
    mass = st.sidebar.number_input("Mass (kg):", value=1.0, min_value=0.0)
    potential = st.sidebar.number_input("Potential (J):", value=0.0)
    solver_method = st.sidebar.selectbox(
        "Solver Method:",
        options=["Method 1", "Method 2", "Method 3"],
        index=0
    )
    return mass, potential, solver_method

# Run Simulation
if st.button("Run Simulation"):
    mass, potential, solver_method = get_user_inputs()
    
    # Placeholder for simulation results (replace with actual computation)
    results = {
        'Mass': mass,
        'Potential': potential,
        'Solver Method': solver_method,
        'Result': mass + potential  # Dummy calculation
    }

    st.write("## Results")
    st.write(results)
    
    # Visualize Results
    import pandas as pd
    results_df = pd.DataFrame([results])
    st.write("### Results Table:")
    st.write(results_df)
    
    if st.button("Export as CSV"):
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='results.csv',
            mime='text/csv'
        )

    if st.button("Export as JSON"):
        json = results_df.to_json(orient='records')
        st.download_button(
            label="Download JSON",
            data=json,
            file_name='results.json',
            mime='application/json'
        )

# Run the app 

# Add example dataset for visualizations (e.g. plot if necessary)