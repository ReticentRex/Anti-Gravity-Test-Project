
print("Starting debug script...")
import numpy as np
from solar_model import SolarModel

model = SolarModel(latitude=-32.05, longitude=115.89)

def check_day(day):
    print(f"\n--- Day {day} ---")
    included_hours = []
    temps = []
    
    for hour in range(24):
        geom = model.calculate_geometry(day, hour)
        geom_next = model.calculate_geometry(day, hour + 1)
        
        # New Logic
        if geom['elevation'] <= 0 and geom_next['elevation'] <= 0:
            continue
            
        T_amb = model.calculate_ambient_temperature(day, hour)
        included_hours.append(hour)
        temps.append(T_amb)
        print(f"Hour {hour}: Elev {geom['elevation']:.2f}, NextElev {geom_next['elevation']:.2f}, Temp {T_amb:.2f}")
        
    print(f"Included Hours: {len(included_hours)}")
    print(f"Average Temp: {np.mean(temps):.4f}")

check_day(45)
check_day(57)
