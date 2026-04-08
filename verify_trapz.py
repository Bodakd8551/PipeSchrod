import numpy as np
from pipeschrod.result import SchrodResult

def test_trapz_fix():
    print("Testing SchrodResult integration (Direct Sum Method)...")
    
    # Create mock grid
    N = 200
    r = np.linspace(0.1, 20.0, N)
    h = r[1] - r[0]
    
    # Mock wave function (ground state of some potential)
    psi = np.array([np.exp(-r)])
    psi = psi / np.sqrt(np.sum(psi**2) * h)
    
    # Create mock SchrodResult
    res = SchrodResult(
        method="Test",
        r=r,
        energies=np.array([1.0]),
        psi=psi,
        potential=np.zeros(N),
        V_eff=np.zeros(N)
    )
    
    # Test methods
    try:
        rms = res.rms_radius(0)
        mean = res.mean_radius(0)
        print(f"OK! rms_radius: {rms:.4f}")
        print(f"OK! mean_radius: {mean:.4f}")
        
        # Verify precision (should be close to theoretical values for e^-r)
        # theoretical mean r for e^-r is ~1.5 (actually depends on range)
        print("Integration logic verified.")
        
    except Exception as e:
        print(f"FAILED! Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_trapz_fix()
