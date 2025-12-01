"""
Verify Kasten-Young Implementation
Checks the impact of the new air mass formula on DNI at extreme latitudes
"""

import numpy as np
from solar_model import SolarModel

# Day 355, Elevation 13.4°
day = 355
elevation_deg = 13.44987746562805

model = SolarModel(latitude=-80.0, longitude=0.0)
irrad = model.calculate_irradiance(day, elevation_deg)

print("=" * 80)
print("Kasten-Young Formula Verification")
print("Latitude -80°, Day 355, Elevation 13.4°")
print("=" * 80)

print(f"\nCalculated values:")
print(f"  A (Extraterrestrial): {irrad['extraterrestrial']:.2f} W/m²")
print(f"  k (Optical Depth): {irrad['optical_depth']:.4f}")
print(f"  m (Air Mass): {irrad['air_mass']:.2f}")
print(f"  DNI: {irrad['dni']:.2f} W/m²")

# Compare with simple formula
beta_rad = np.radians(elevation_deg)
m_simple = 1 / np.sin(beta_rad)
A = irrad['extraterrestrial']
k = irrad['optical_depth']
DNI_simple = A * np.exp(-k * m_simple)

print(f"\nComparison with simple formula (m = 1/sin(β)):")
print(f"  m (Simple): {m_simple:.2f}")
print(f"  m (Kasten-Young): {irrad['air_mass']:.2f}")
print(f"  Difference: {irrad['air_mass'] - m_simple:+.2f} ({(irrad['air_mass']/m_simple - 1)*100:+.1f}%)")

print(f"\n  DNI (Simple): {DNI_simple:.2f} W/m²")
print(f"  DNI (Kasten-Young): {irrad['dni']:.2f} W/m²")
print(f"  Difference: {irrad['dni'] - DNI_simple:+.2f} W/m² ({(irrad['dni']/DNI_simple - 1)*100:+.1f}%)")

# Run full day simulation
print("\n" + "=" * 80)
print("Full Day Analysis")
print("=" * 80)

total_dni_kwh = 0
for hour in range(24):
    geom = model.calculate_geometry(day, hour)
    if geom['elevation'] > 0:
        irrad_hour = model.calculate_irradiance(day, geom['elevation'])
        total_dni_kwh += irrad_hour['dni'] / 1000.0

print(f"\nDaily DNI Total (Kasten-Young): {total_dni_kwh:.2f} kWh/m²")
print(f"Previous (Simple formula): 20.12 kWh/m²")
print(f"Change: {total_dni_kwh - 20.12:+.2f} kWh/m² ({(total_dni_kwh/20.12 - 1)*100:+.1f}%)")
