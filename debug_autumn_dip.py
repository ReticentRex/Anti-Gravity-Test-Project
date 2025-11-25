import numpy as np
import matplotlib.pyplot as plt
from solar_model import SolarModel

# Test at latitude -32 where the dip is observed
model = SolarModel(latitude=-32, longitude=115.89)

# Generate annual profile
profile = model.generate_annual_profile(efficiency=0.14)
df = profile['hourly_data']

# Aggregate to daily
daily = df.groupby('Day').agg({'P_2Axis': 'sum'}).reset_index()
daily['P_2Axis_kWh'] = daily['P_2Axis'] / 1000

# Check for discontinuities around Autumn (Day 60 = Mar 1)
autumn_range = range(50, 80)
spring_range = range(230, 260)

print("Checking for asymmetry between Spring and Autumn")
print("=" * 60)
print("\nAutumn (Days 50-80):")
for day in autumn_range:
    if day in daily['Day'].values:
        val = daily[daily['Day'] == day]['P_2Axis_kWh'].values[0]
        print(f"Day {day}: {val:.3f} kWh/m²/day")

print("\nSpring (Days 230-260) - Should be symmetric:")
for day in spring_range:
    if day in daily['Day'].values:
        val = daily[daily['Day'] == day]['P_2Axis_kWh'].values[0]
        # Compare to symmetric autumn day
        symmetric_day = 365 - day + 60  # Map spring back to autumn
        print(f"Day {day}: {val:.3f} kWh/m²/day")

# Plot the curves
plt.figure(figsize=(12, 6))
plt.plot(daily['Day'], daily['P_2Axis_kWh'], 'b-', linewidth=2)
plt.axvline(60, color='r', linestyle='--', alpha=0.5, label='Autumn (~Mar 1)')
plt.axvline(244, color='g', linestyle='--', alpha=0.5, label='Spring (~Sep 1)')
plt.xlabel('Day of Year')
plt.ylabel('Daily Generation (kWh/m²/day)')
plt.title('2-Axis Tracker Daily Generation at -32° Latitude')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('generation_asymmetry_debug.png', dpi=150, bbox_inches='tight')
print("\nPlot saved to generation_asymmetry_debug.png")

# Check equation of time and declination
print("\n" + "=" * 60)
print("Checking Solar Equation Calculations:")
print("=" * 60)
for day in [60, 81, 100, 244, 265]:
    geom = model.calculate_geometry(day, 12)  # Solar noon
    B_364 = 2 * np.pi / 364 * (day - 81)
    B_365 = 2 * np.pi / 365 * (day - 81)
    
    print(f"\nDay {day}:")
    print(f"  Declination angle: {geom['declination']:.3f}°")
    print(f"  B (using 364): {np.degrees(B_364):.3f}°")
    print(f"  B (using 365): {np.degrees(B_365):.3f}°")
    print(f"  Difference: {np.degrees(B_365 - B_364):.4f}°")
