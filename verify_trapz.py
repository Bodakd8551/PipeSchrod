import numpy as np
from pipeschrod.result import SchrodResult

def verify_trapz():
    print("Testing SchrodResult.rms_radius with Scipy integration...")
    
    # Mock data
    r = np.linspace(0.1, 10.0, 100)
    energies = np.array([-1.0, -0.5, 0.1])
    psi = np.zeros((3, 100))
    # Gaussian-like wavefunction for ground state
    psi[0] = np.exp(-r**2)
    # Normalizing manually for the test
    norm = np.sqrt(np.trapz(psi[0]**2, r)) if hasattr(np, 'trapz') else np.sqrt(np.sum(psi[0]**2) * (r[1]-r[0]))
    psi[0] /= norm
    
    res = SchrodResult(
        method="Test",
        r=r,
        energies=energies,
        psi=psi,
        potential=np.zeros_like(r),
        V_eff=np.zeros_like(r)
    )
    
    try:
        rms = res.rms_radius(0)
        print(f"OK! rms_radius: {rms:.4f}")
        
        mean = res.mean_radius(0)
        print(f"OK! mean_radius: {mean:.4f}")
        
        summary = res.summary_dict()
        print("OK! summary_dict generated.")
        
    except Exception as e:
        print(f"FAILED: {e}")
        exit(1)

if __name__ == "__main__":
    verify_trapz()
