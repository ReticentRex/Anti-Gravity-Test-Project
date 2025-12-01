import numpy as np

# Manual calculation for winter noon
print("=== WINTER NOON TEST (Day 172, Lat -32°S) ===\n")

# Winter solstice parameters
beta_deg = 35.0  # Sun elevation at winter noon
phi_s_deg = 0.0  # Sun azimuth (north)
sigma_deg = 0.0  # Panel tilt (flat for 1-Axis Horizontal at noon)
phi_c_deg = 0.0  # Panel azimuth (arctan2(0,0) returns 0 in numpy)

print(f"Sun: Elevation={beta_deg}°, Azimuth={phi_s_deg}°")
print(f"Panel: Tilt={sigma_deg}°, Azimuth={phi_c_deg}°")

# Convert to radians
beta = np.radians(beta_deg)
phi_s = np.radians(phi_s_deg)
sigma = np.radians(sigma_deg)
phi_c = np.radians(phi_c_deg)

#  Angle of Incidence formula from solar_model.py
cos_theta = np.cos(beta) * np.cos(phi_s - phi_c) * np.sin(sigma) + \
            np.sin(beta) * np.cos(sigma)

print(f"\ncos(theta) = cos({beta_deg}°)*cos({phi_s_deg}° - {phi_c_deg}°)*sin({sigma_deg}°) + sin({beta_deg}°)*cos({sigma_deg}°)")
print(f"cos(theta) = {np.cos(beta):.4f} * {np.cos(phi_s - phi_c):.4f} * {np.sin(sigma):.4f} + {np.sin(beta):.4f} * {np.cos(sigma):.4f}")
print(f"cos(theta) = 0 + {np.sin(beta):.4f} = {cos_theta:.4f}")

# For flat panel (sigma=0), the formula simplifies:
# cos(theta) = sin(beta)
expected = np.sin(beta)
print(f"\nExpected for flat panel: cos(theta) = sin({beta_deg}°) = {expected:.4f}")
print(f"Match: {abs(cos_theta - expected) < 0.001}")

# Irradiance comparison (assuming DNI = 900 W/m², C = 0.1)
DNI = 900
C = 0.1

# 1-Axis Horizontal (flat)
Ibc_1h = DNI * cos_theta
Idc_1h = C * DNI * (1 + np.cos(sigma)) / 2  # (1 + 1)/2 = 1
Irc_1h = 0.2 * DNI * (np.sin(beta) + C) * (1 - np.cos(sigma)) / 2  # (1-1)/2 = 0
Ic_1h = Ibc_1h + Idc_1h + Irc_1h

print(f"\n1-AXIS HORIZONTAL IRRADIANCE:")
print(f"  Beam:      {Ibc_1h:.1f} W/m² (DNI * {cos_theta:.3f})")
print(f"  Diffuse:   {Idc_1h:.1f} W/m² (C * DNI)")
print(f"  Reflected: {Irc_1h:.1f} W/m²")
print(f"  Total:     {Ic_1h:.1f} W/m²")

# 2-Axis (pointing at sun)
sigma_2axis = 90 - beta_deg
Ibc_2axis = DNI * 1.0  # Perfect tracking
Idc_2axis = C * DNI * (1 + np.sin(beta)) / 2
Irc_2axis = 0.2 * DNI * (np.sin(beta) + C) * (1 - np.sin(beta)) / 2
Ic_2axis = Ibc_2axis + Idc_2axis + Irc_2axis

print(f"\n2-AXIS TRACKER IRRADIANCE:")
print(f"  Beam:      {Ibc_2axis:.1f} W/m² (DNI * 1.0)")
print(f"  Diffuse:   {Idc_2axis:.1f} W/m²")
print(f"  Reflected: {Irc_2axis:.1f} W/m²")
print(f"  Total:     {Ic_2axis:.1f} W/m²")

print(f"\nRATIO (1-Axis/2-Axis): {Ic_1h/Ic_2axis:.1%}")
print(f"Expected ratio should be ~65-70% due to beam losses")
print(f"If the user sees 90%, there's a bug somewhere!")
