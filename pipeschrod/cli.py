import os
import subprocess
import sys
import pkg_resources

def run_dashboard():
    """
    Entry point for the 'pipeschrod-lab' command.
    Launches the Streamlit app from within the package or local directory.
    """
    try:
        # Try to find the dashboard file relative to this script
        # This handles both local 'pip install -e .' and PyPI installation
        pkg_base = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(pkg_base, "dashboard", "streamlit_app.py")
        
        if not os.path.exists(app_path):
            print(f"Error: Dashboard file not found at {app_path}")
            sys.exit(1)
            
        print(f"⚛️  Launching PipeSchrod Interactive Lab...")
        
        # Invoke streamlit as a module
        cmd = [sys.executable, "-m", "streamlit", "run", app_path]
        
        # Execute the process
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n⚛️  Lab closed.")
    except Exception as e:
        print(f"Error launching lab: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_dashboard()
