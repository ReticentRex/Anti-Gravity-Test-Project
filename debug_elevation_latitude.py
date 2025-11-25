import numpy as np
from solar_model import SolarModel

# Test at different latitudes
latitudes = [0, -10, -20, -32, -40]
print("1-Axis Elevation Tracker Performance vs Latitude\n")
print(f"{'Latitude':<12} {'kWh/m²':<12} {'Avg Hours/Day'}")
print("-" * 40)

for lat in latitudes:
    model = SolarModel(latitude=lat, longitude=115.89)
    profile = model.generate_annual_profile(efficiency=0.14)
    
    # Calculate annual yield for 1-Axis Elevation
    annual_yield = profile['Annual_Yield_1Axis_Elevation_kWh_m2']
    
    # Count average daylight hours (where elevation tracker is active)
    df = profile['hourly_data']
    avg_hours_per_day = len(df) / 365
    
    print(f"{lat:<12.0f} {annual_yield:<12.1f} {avg_hours_per_day:<.2f}")

print("\n\nDetailed Analysis for Equator (Lat=0) - Day 80 (Around Equinox)")
print("=" * 70)

model_eq = SolarModel(latitude=0, longitude=115.89)

day = 80  # Near equinox
print(f"\nDay {day}:")
for hour in range(24):
    geom = model_eq.calculate_geometry(day, hour)
    
    if geom['elevation'] <= 0:
        continue
    
    # Calculate panel orientation
    if abs(geom['azimuth']) <= 90:
        phi_c = 0  # Face North
        direction = "North"
    else:
        phi_c = 180  # Face South
        direction = "South"
    
    sigma = 90 - geom['elevation']  # Panel tilt
    
    print(f"  Hour {hour:02d}: Sun Az={geom['azimuth']:6.1f}°, El={geom['elevation']:5.1f}° | "
          f"Panel faces {direction:5s} (Az={phi_c:3.0f}°), Tilt={sigma:5.1f}°")
