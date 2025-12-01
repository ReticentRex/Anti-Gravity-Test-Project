"""
Debug Irradiance Formula
Checks if Eq 9-12 are correctly calculating DNI at low angles
"""

import numpy as np

# Day 355, Elevation 13.4°
day = 355
elevation_deg = 13.44987746562805

beta_rad = np.radians(elevation_deg)

# Eq 9: Extraterrestrial Flux
A = 1160 + 75 * np.sin(2 * np.pi / 365 * (day - 275))
print(f"Eq 9: A = {A:.2f} W/m²")

# Eq 10: Optical Depth
k = 0.174 + 0.035 * np.sin(2 * np.pi / 365 * (day - 100))
print(f"Eq 10: k = {k:.4f}")

# Eq 11: Air Mass
sin_beta = np.sin(beta_rad)
if sin_beta < 0.01:
    m = 1 / 0.01
else:
    m = 1 / sin_beta
print(f"Eq 11: m = {m:.2f} (sin(β) = {sin_beta:.4f})")

# Eq 12: DNI
Ib_calculated = A * np.exp(-k * m)
print(f"Eq 12: DNI = {Ib_calculated:.2f} W/m²")

# From CSV
Ib_csv = 673.382694938204
print(f"\nFrom CSV: DNI = {Ib_csv:.2f} W/m²")
print(f"Difference: {Ib_csv - Ib_calculated:.2f} W/m²")

# Check intermediate values
attenuation = np.exp(-k * m)
print(f"\nAttenuation factor: e^(-k·m) = {attenuation:.4f}")
print(f"This means {attenuation*100:.1f}% of extraterrestrial flux reaches ground")

# What value of k would give us the CSV DNI?
# Ib_csv = A * e^(-k_needed * m)
# e^(-k_needed * m) = Ib_csv / A
# -k_needed * m = ln(Ib_csv / A)
# k_needed = -ln(Ib_csv / A) / m
k_needed = -np.log(Ib_csv / A) / m
print(f"\nTo get CSV value, k would need to be: {k_needed:.4f}")
print(f"Current k: {k:.4f}")
print(f"Ratio: {k/k_needed:.2f}x too high attenuation")
