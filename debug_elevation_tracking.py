from solar_model import SolarModel
import numpy as np

def test_elevation_tracking():
    print("\n--- Testing 1-Axis Elevation Tracking at Equator (Lat 0) ---")
    model = SolarModel(latitude=0, longitude=0)
    
    # Test Case: Dec 21 (Sun is South at -23.45 deg)
    # Solar Noon (Hour 12)
    day = 355
    hour = 12
    
    geom = model.calculate_geometry(day, hour)
    beta = geom['elevation']
    phi_s = geom['azimuth']
    
    print(f"Date: Dec 21 (Sun South)")
    print(f"Sun Elevation: {beta:.2f}")
    print(f"Sun Azimuth: {phi_s:.2f} (Should be ~180 South)")
    
    # Calculate Irradiance
    irrad = model.calculate_irradiance(day, beta)
    Ib = irrad['dni']
    C = irrad['diffuse_factor']
    
    # Mode 3: 1-Axis Elevation Tracking (Current Implementation)
    # phi_c = 0 (North)
    # sigma = 90 - beta
    
    phi_c_current = 0
    sigma_current = 90 - beta
    
    Ic_current, cos_theta_current = model.calculate_incident_irradiance(beta, phi_s, sigma_current, phi_c_current, Ib, C)
    
    print(f"\nCurrent Implementation (Phi_c=0):")
    print(f"  Panel Azimuth: {phi_c_current}")
    print(f"  Panel Tilt: {sigma_current:.2f}")
    print(f"  Cos(Theta): {cos_theta_current:.4f}")
    print(f"  Incident Irradiance: {Ic_current:.2f}")
    
    # Proposed Fix: Panel should face the sun's azimuth (0 or 180)
    # If Sun Azimuth is ~180, Panel Azimuth should be 180.
    
    phi_c_fix = 180
    Ic_fix, cos_theta_fix = model.calculate_incident_irradiance(beta, phi_s, sigma_current, phi_c_fix, Ib, C)
    
    print(f"\nProposed Fix (Phi_c=180):")
    print(f"  Panel Azimuth: {phi_c_fix}")
    print(f"  Panel Tilt: {sigma_current:.2f}")
    print(f"  Cos(Theta): {cos_theta_fix:.4f}")
    print(f"  Incident Irradiance: {Ic_fix:.2f}")
    
    if Ic_fix > Ic_current * 1.1:
        print("\n[CONCLUSION] Current implementation severely underperforms when Sun is South.")
    else:
        print("\n[CONCLUSION] Performance is similar.")

if __name__ == "__main__":
    test_elevation_tracking()
