import numpy as np

# Test winter noon at latitude -32°S
# In winter (June), sun is in the north at low elevation

# Winter conditions
lat = -32.0
day = 172  # Winter solstice (June 21)
hour = 12  # Noon

# Calculate declination
n = day
delta_deg = 23.45 * np.sin(2 * np.pi / 365 * (n - 81))
print(f"Declination: {delta_deg:.2f}°")

# Calculate noon elevation at winter solstice
lat_rad = np.radians(lat)
delta_rad = np.radians(delta_deg)
# At solar noon, hour angle H = 0
sin_beta = np.cos(lat_rad) * np.cos(delta_rad) + np.sin(lat_rad) * np.sin(delta_rad)
beta_deg = np.degrees(np.arcsin(sin_beta))
print(f"Noon Elevation: {beta_deg:.2f}°")

# Sun azimuth at noon (should be North = 0° for Southern Hemisphere)
phi_s_deg = 0.0
print(f"Sun Azimuth: {phi_s_deg:.2f}°")

print("\n--- 1-Axis Horizontal Tracker ---")
# At noon, hour angle omega = 0
omega_deg = 0
omega_rad = np.radians(omega_deg)

# Panel normal vector
n_rot_x = 1 * np.sin(omega_rad)  # 0
n_rot_y = 0
n_rot_z = 1 * np.cos(omega_rad)  # 1

# Panel tilt (sigma)
sigma_deg = np.degrees(np.arccos(n_rot_z))
print(f"Panel Tilt (sigma): {sigma_deg:.2f}°")

# Panel azimuth (phi_c)
phi_c_deg = np.degrees(np.arctan2(n_rot_x, n_rot_y))
print(f"Panel Azimuth (phi_c): {phi_c_deg:.2f}° [arctan2(0, 0)]")

# Calculate angle of incidence
beta_rad = np.radians(beta_deg)
phi_s_rad = np.radians(phi_s_deg)
sigma_rad = np.radians(sigma_deg)
phi_c_rad = np.radians(phi_c_deg)

cos_theta = np.cos(beta_rad) * np.cos(phi_s_rad - phi_c_rad) * np.sin(sigma_rad) + \
            np.sin(beta_rad) * np.cos(sigma_rad)
print(f"cos(theta) = cos({beta_deg:.1f}°)*cos({phi_s_deg:.1f}° - {phi_c_deg:.1f}°)*sin({sigma_deg:.1f}°) + sin({beta_deg:.1f}°)*cos({sigma_deg:.1f}°)")
print(f"cos(theta) = {np.cos(beta_rad):.4f} * {np.cos(phi_s_rad - phi_c_rad):.4f} * {np.sin(sigma_rad):.4f} + {np.sin(beta_rad):.4f} * {np.cos(sigma_rad):.4f}")
print(f"cos(theta) = {cos_theta:.4f}")
print(f"Angle of incidence: {np.degrees(np.arccos(np.clip(cos_theta, -1, 1))):.2f}°")

# For flat panel (sigma=0), this should simplify to sin(beta)
print(f"\nFor flat panel: cos(theta) should equal sin(beta) = {np.sin(beta_rad):.4f}")
print(f"Actual cos(theta) = {cos_theta:.4f}")

print("\n--- 2-Axis Tracker ---")
print(f"cos(theta) = 1.0 (perfect tracking)")
print(f"Angle of incidence: 0.0°")

print(f"\n--- Ratio of Irradiance (1-Axis/2-Axis) ---")
print(f"Direct beam ratio: {cos_theta:.4f} / 1.0 = {cos_theta:.2%}")
print(f"Expected annual yield ratio should be much lower in winter!")
