
import sys
import pandas as pd
import numpy as np
from solar_model import SolarModel

# Setup model for Perth (Lat -32)
model = SolarModel(latitude=-32.0, longitude=115.0)

# Run simulation for a summer day (Day 1)
print("Running simulation for Day 1 (Summer)...")
df, totals = model.generate_annual_profile(efficiency=0.14, time_step_minutes=60)

# Filter for Day 1
day_df = df[df['Day'] == 1].copy()

# Columns to inspect for 1-Axis Horizontal
cols = [
    'Hour', 
    'Elevation_deg', 'Azimuth_deg',  # Sun
    'P_1Axis_Horiz', 'P_1Axis_Horiz_25C', # Power
    'T_amb'
]

print("\n--- Hourly Performance for Day 1 (1-Axis Horizontal) ---")
print(day_df[cols].to_string(index=False))

# Check for negative cooling benefit
day_df['Cooling_Benefit'] = day_df['P_1Axis_Horiz_25C'] - day_df['P_1Axis_Horiz']
print("\n--- Negative Cooling Benefit Check ---")
neg_benefit = day_df[day_df['Cooling_Benefit'] < -0.01]
if not neg_benefit.empty:
    print("WARNING: Found negative cooling benefit!")
    print(neg_benefit[['Hour', 'P_1Axis_Horiz', 'P_1Axis_Horiz_25C', 'Cooling_Benefit']].to_string(index=False))
else:
    print("No negative cooling benefit found.")

# Check for zero generation at mid-day
print("\n--- Mid-day Generation Check ---")
mid_day = day_df[(day_df['Hour'] >= 11) & (day_df['Hour'] <= 13)]
print(mid_day[cols].to_string(index=False))

# Let's also look at the tracking angles if we can access them
# Since they aren't in the DF, we might need to instrument the model or manually calc them here
print("\n--- Manual Tracking Angle Check ---")
for hour in range(10, 15):
    geom = model.calculate_geometry(1, hour)
    omega = geom['hour_angle']
    omega_rad = np.radians(omega)
    
    # Mode 9 Logic
    n_rot_x_h = 1 * np.sin(omega_rad)
    n_rot_y_h = 0
    n_rot_z_h = 1 * np.cos(omega_rad)
    
    beta_c = np.degrees(np.arcsin(n_rot_z_h))
    phi_c = np.degrees(np.arctan2(n_rot_x_h, n_rot_y_h))
    
    print(f"Hour: {hour}, Omega: {omega:.1f}, Beta_c: {beta_c:.1f}, Phi_c: {phi_c:.1f}")
