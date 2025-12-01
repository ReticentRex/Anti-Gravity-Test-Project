
import pandas as pd
import numpy as np
from solar_model import SolarModel

# Setup model for Perth (Lat -32)
model = SolarModel(latitude=-32.0, longitude=115.0)

# Run simulation for a summer day (Day 1)
print("Running simulation for Day 1 (Summer)...")
# Use 60 min time step for clarity
df, totals = model.generate_annual_profile(efficiency=0.14, time_step_minutes=60)

# Filter for Day 1 and morning hours
day_df = df[(df['Day'] == 1) & (df['Hour'] >= 5) & (df['Hour'] <= 10)].copy()

# Columns to inspect
cols = [
    'Hour', 
    'Elevation_deg', 'Azimuth_deg',  # Sun
    'P_1Axis_Horiz'
]

print("\n--- Morning Performance for Day 1 (1-Axis Horizontal) ---")
print(day_df[cols].to_string(index=False))

print("\n--- Detailed Angle Check ---")
# Manually calculate geometry for these hours to see internal states
for hour in range(5, 11):
    geom = model.calculate_geometry(1, hour)
    beta = geom['elevation']
    phi_s = geom['azimuth']
    
    if beta <= 0:
        print(f"Hour {hour}: Sun below horizon (Beta={beta:.2f})")
        continue

    # Re-implement Mode 9 logic to inspect intermediate values
    omega = geom['hour_angle']
    omega_rad = np.radians(omega)
    
    # Mode 9: 1-Axis Horizontal
    # Axis along N-S (y-axis), rotates around y
    # Vector math from solar_model.py
    
    rho_rad_h = omega_rad
    
    # Current implementation
    n_rot_x_h = -1 * np.sin(rho_rad_h)
    n_rot_y_h = 0
    n_rot_z_h = 1 * np.cos(rho_rad_h)
    
    if n_rot_z_h < 0:
        print(f"Hour {hour}: n_rot_z_h < 0 ({n_rot_z_h:.4f}) -> Panel facing down?")
        continue
        
    n_rot_z_h = np.clip(n_rot_z_h, -1.0, 1.0)
    sigma_horiz = np.degrees(np.arccos(n_rot_z_h))
    phi_c_horiz = np.degrees(np.arctan2(n_rot_x_h, n_rot_y_h))
    
    # Calculate Irradiance
    irr = model.calculate_irradiance(1, beta)
    Ib = irr['dni']
    C = irr['diffuse_factor']
    
    Ic, cos_theta = model.calculate_incident_irradiance(beta, phi_s, sigma_horiz, phi_c_horiz, Ib, C)
    
    print(f"Hour {hour}: Beta={beta:.2f}, Phi_s={phi_s:.2f} | Sigma={sigma_horiz:.2f}, Phi_c={phi_c_horiz:.2f} | Cos_Theta={cos_theta:.4f} | Ic={Ic:.2f}")
