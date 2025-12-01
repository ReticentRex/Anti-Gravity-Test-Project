"""
Verify Improved Temperature Model
Shows temperatures at various latitudes including South Pole
"""

from solar_model import SolarModel

print("=" * 80)
print("Temperature Model Verification - Latitude Dependency")
print("=" * 80)

latitudes = [
    (0, "Equator"),
    (-23.45, "Tropic of Capricorn"),
    (-32, "Perth"),
    (-50, "Southern Ocean"),
    (-66.5, "Antarctic Circle"),
    (-80, "Antarctica"),
    (-90, "South Pole")
]

for lat, name in latitudes:
    model = SolarModel(latitude=lat, longitude=0.0)
    
    # Summer (Day 365) and Winter (Day 182)
    summer_temps = []
    winter_temps = []
    
    for hour in range(24):
        summer_temps.append(model.calculate_ambient_temperature(365, hour))
        winter_temps.append(model.calculate_ambient_temperature(182, hour))
    
    print(f"\n{name} ({lat}°):")
    print(f"  Summer (Day 365): {min(summer_temps):+.1f}°C to {max(summer_temps):+.1f}°C")
    print(f"  Winter (Day 182): {min(winter_temps):+.1f}°C to {max(winter_temps):+.1f}°C")

print("\n" + "=" * 80)
print("South Pole Detail (Day 365)")
print("=" * 80)

model_pole = SolarModel(latitude=-90.0, longitude=0.0)
print("\nHourly temperatures:")
for hour in [0, 6, 12, 18]:
    temp = model_pole.calculate_ambient_temperature(365, hour)
    print(f"  Hour {hour:2d}: {temp:+.1f}°C")
