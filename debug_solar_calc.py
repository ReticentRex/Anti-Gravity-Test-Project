"""
Diagnostic script to check solar calculations for anomalies
"""
import numpy as np
from solar_model import SolarModel

# Initialize model
model = SolarModel(latitude=-32, longitude=115.86)

print("Day | Declination | Amb_Temp | DNI_noon | Cell_Temp_2Axis")
print("-" * 70)

# Check days 40-60 where user sees anomaly
for day in range(40, 61):
    # Get declination
    geom_noon = model.calculate_geometry(day, 12)
    declination = geom_noon['declination']
    elevation_noon = geom_noon['elevation']
    
    # Get ambient temp at noon
    T_amb_noon = model.calculate_ambient_temperature(day, 12)
    
    # Get irradiance at noon
    if elevation_noon > 0:
        irrad = model.calculate_irradiance(day, elevation_noon)
        DNI = irrad['dni']
        
        # Calculate 2-axis tracking (perpendicular to sun)
        # For 2-axis, Ic = DNI (always perpendicular)
        Ic_2axis = DNI
        cos_theta_2axis = 1.0
        
        # Calculate cell temp for 2-axis
        res = model.calculate_pv_performance(Ic_2axis, cos_theta_2axis, T_amb=T_amb_noon, efficiency=0.14)
        T_cell_2axis = res['T_cell']
    else:
        DNI = 0
        T_cell_2axis = T_amb_noon
    
    print(f"{day:3d} | {declination:7.2f}° | {T_amb_noon:6.2f}°C | {DNI:7.1f} W/m² | {T_cell_2axis:6.2f}°C")

print("\n" + "="*70)
print("Checking ambient temperature model smoothness")
print("="*70)
print("Day | T_amb @ 6am | T_amb @ 12pm | T_amb @ 6pm")
print("-" * 50)

for day in [44, 45, 46, 50, 55, 56, 57]:
    T_6am = model.calculate_ambient_temperature(day, 6)
    T_noon = model.calculate_ambient_temperature(day, 12)
    T_6pm = model.calculate_ambient_temperature(day, 18)
    print(f"{day:3d} | {T_6am:10.2f}°C | {T_noon:11.2f}°C | {T_6pm:10.2f}°C")

print("\n" + "="*70)
print("Checking irradiance model components")
print("="*70)
print("Day | A (Extra) | k (Optical) | C (Diffuse) | DNI @ noon")
print("-" * 70)

for day in range(40, 61, 5):
    geom = model.calculate_geometry(day, 12)
    elevation = geom['elevation']
    
    if elevation > 0:
        # Manually calculate to see intermediate values
        n = day
        A = 1160 + 75 * np.sin(2 * np.pi / 365 * (n - 275))
        k = 0.174 + 0.035 * np.sin(2 * np.pi / 365 * (n - 100))
        C = 0.095 + 0.04 * np.sin(2 * np.pi / 365 * (n - 100))
        
        beta_rad = np.radians(elevation)
        sin_beta = np.sin(beta_rad)
        m = 1 / sin_beta if sin_beta > 0.01 else 1 / 0.01
        DNI = A * np.exp(-k * m)
        
        print(f"{day:3d} | {A:8.1f} | {k:10.4f} | {C:10.4f} | {DNI:10.1f}")
