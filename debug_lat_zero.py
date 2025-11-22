from solar_model import SolarModel
import pandas as pd
import numpy as np

def test_lat_zero():
    print("--- Testing Solar Model at Lat=0, Long=0 ---")
    model = SolarModel(latitude=0, longitude=0)
    
    # Calculate for a specific time (e.g., Day 81, Solar Noon)
    # Day 81 is Equinox. Declination should be ~0.
    day = 81
    hour = 12 # Solar noon approx
    
    print(f"\nDay: {day}, Hour: {hour}")
    
    # 1. Geometry
    geom = model.calculate_geometry(day, hour)
    print("\nGeometry:")
    for k, v in geom.items():
        print(f"  {k}: {v:.4f}")
        
    # 2. Irradiance
    irrad = model.calculate_irradiance(day, geom['elevation'])
    Ib = irrad['dni']
    C = irrad['diffuse_factor']
    print(f"\nDNI (Ib): {Ib:.2f} W/m2")
    
    # 3. Tracking Modes
    beta = geom['elevation']
    phi_s = geom['azimuth']
    
    print("\nTracking Mode Analysis:")
    
    # Mode 1: Horizontal
    sigma_horiz = 0
    phi_c_horiz = 0
    Ic_horiz, cos_theta_horiz = model.calculate_incident_irradiance(beta, phi_s, sigma_horiz, phi_c_horiz, Ib, C)
    print(f"  Horizontal:")
    print(f"    Tilt (Sigma): {sigma_horiz}")
    print(f"    Panel Azimuth (Phi_c): {phi_c_horiz}")
    print(f"    Cos(Theta): {cos_theta_horiz:.4f}")
    print(f"    Incident Irradiance: {Ic_horiz:.2f} W/m2")
    
    # Mode 2: 1-Axis Azimuth
    # Logic from solar_model.py:
    sigma_az_track = abs(model.latitude)
    phi_c_az_track = phi_s
    Ic_az, cos_theta_az = model.calculate_incident_irradiance(beta, phi_s, sigma_az_track, phi_c_az_track, Ib, C)
    print(f"  1-Axis Azimuth:")
    print(f"    Tilt (Sigma): {sigma_az_track} (Should be abs(lat))")
    print(f"    Panel Azimuth (Phi_c): {phi_c_az_track:.4f} (Tracks Sun Azimuth)")
    print(f"    Cos(Theta): {cos_theta_az:.4f}")
    print(f"    Incident Irradiance: {Ic_az:.2f} W/m2")
    
    if abs(Ic_horiz - Ic_az) < 0.01:
        print("\n  [RESULT] Horizontal and 1-Axis Azimuth are IDENTICAL.")
        print("  Reason: Tilt is 0. A flat plate rotating in azimuth sees the same sun angles as a stationary flat plate.")
    else:
        print("\n  [RESULT] Different.")

if __name__ == "__main__":
    test_lat_zero()
