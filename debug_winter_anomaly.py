
import pandas as pd
import numpy as np
from solar_model import SolarModel

# Setup model for Perth (Lat -32)
model = SolarModel(latitude=-32.0, longitude=115.0)

# Run simulation for a winter day (Day 172 ~ June 21)
print("Running simulation for Day 172 (Winter)...")
df, totals = model.generate_annual_profile(efficiency=0.14, time_step_minutes=60)

# Filter for Day 172 and noon
day_df = df[(df['Day'] == 172) & (df['Hour'] >= 11) & (df['Hour'] <= 13)].copy()

# Columns to inspect
cols = [
    'Hour', 
    'Elevation_deg', 'Azimuth_deg',  # Sun
    'P_1Axis_Horiz', 'P_1Axis_Horiz_25C',
    'P_2Axis', 'P_2Axis_25C',
    'T_amb', 'T_cell_1Axis_Horiz', 'T_cell_2Axis'
]

print("\n--- Winter Noon Performance (Day 172) ---")
print(day_df[cols].to_string(index=False))

# Analyze Cooling Benefit
print("\n--- Cooling Benefit Analysis ---")
for idx, row in day_df.iterrows():
    p_act = row['P_1Axis_Horiz']
    p_cool = row['P_1Axis_Horiz_25C']
    benefit = p_cool - p_act
    ratio = benefit / p_act if p_act > 0 else 0
    t_cell = row['T_cell_1Axis_Horiz']
    t_amb = row['T_amb']
    
    print(f"Hour {row['Hour']}: P_act={p_act:.1f}, P_cool={p_cool:.1f}, Benefit={benefit:.1f} ({ratio*100:.1f}%)")
    print(f"  T_amb={t_amb:.1f}, T_cell={t_cell:.1f}, DeltaT={t_cell-25:.1f}")
    
    # Check 2-Axis comparison
    p_2axis = row['P_2Axis']
    eff_ratio = p_act / p_2axis if p_2axis > 0 else 0
    print(f"  vs 2-Axis: {p_act:.1f} / {p_2axis:.1f} = {eff_ratio*100:.1f}%")

# Check if 1-Axis Horiz is getting extra light
print("\n--- Geometry Check ---")
hour = 12
geom = model.calculate_geometry(172, hour)
beta = geom['elevation']
phi_s = geom['azimuth']
print(f"Noon Geometry: Beta={beta:.2f}, Phi_s={phi_s:.2f}")

# 1-Axis Horiz Logic
omega = geom['hour_angle']
rho_rad_h = np.clip(np.radians(omega), -np.pi/2, np.pi/2)
n_rot_x_h = 1 * np.sin(rho_rad_h)
n_rot_y_h = 0
n_rot_z_h = 1 * np.cos(rho_rad_h)
sigma_horiz = np.degrees(np.arccos(n_rot_z_h))
phi_c_horiz = np.degrees(np.arctan2(n_rot_x_h, n_rot_y_h))

print(f"1-Axis Horiz: Sigma={sigma_horiz:.2f}, Phi_c={phi_c_horiz:.2f}")

# Irradiance
irr = model.calculate_irradiance(172, beta)
Ib = irr['dni']
C = irr['diffuse_factor']
Ic, cos_theta = model.calculate_incident_irradiance(beta, phi_s, sigma_horiz, phi_c_horiz, Ib, C)
print(f"1-Axis Horiz: Ic={Ic:.1f}, CosTheta={cos_theta:.4f}")

# 2-Axis Logic
sigma_2axis = 90 - beta
phi_c_2axis = phi_s
Ic_2, cos_theta_2 = model.calculate_incident_irradiance(beta, phi_s, sigma_2axis, phi_c_2axis, Ib, C)
print(f"2-Axis: Ic={Ic_2:.1f}, CosTheta={cos_theta_2:.4f}")
