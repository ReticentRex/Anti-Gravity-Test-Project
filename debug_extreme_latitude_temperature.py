"""
Debug Extreme Latitude Temperature
Investigates why temperature is only 4°C at Antarctic latitudes.
Outputs to CSV for analysis.
"""

from solar_model import SolarModel
import pandas as pd

def debug_extreme_temperature():
    print("Debugging Extreme Latitude Temperature")
    print("=" * 100)
    
    # Test at -80° (Antarctica) across the year
    model = SolarModel(latitude=-80.0, longitude=0.0)
    
    # Sample temperatures across the year
    data = []
    
    for day in [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 355]:  # Roughly one per month
        for hour in [0, 6, 12, 18]:  # Sample 4 times per day
            temp = model.calculate_ambient_temperature(day, hour)
            
            data.append({
                'Day': day,
                'Hour': hour,
                'Temperature_C': temp
            })
    
    df = pd.DataFrame(data)
    
    print(f"\nLocation: Latitude -80° (Antarctica)")
    print(f"Temperature range: {df['Temperature_C'].min():.1f}°C to {df['Temperature_C'].max():.1f}°C")
    print(f"Average temperature: {df['Temperature_C'].mean():.1f}°C")
    
    # Save to CSV
    df.to_csv('extreme_latitude_temperature.csv', index=False)
    print(f"\nData saved to extreme_latitude_temperature.csv")
    
    # Show model parameters
    print("\n" + "=" * 100)
    print("TEMPERATURE MODEL ANALYSIS:")
    print("=" * 100)
    print(f"\nChecking calculate_ambient_temperature() implementation...")
    print(f"The model likely uses a simple sinusoidal model:")
    print(f"  T = T_avg + T_amp * sin(2π * (day - day_offset) / 365) + daily_variation")
    print(f"\nFor extreme latitudes, the model needs:")
    print(f"  - Much lower T_avg (e.g., -20°C for Antarctica)")
    print(f"  - Larger seasonal T_amp (e.g., ±30°C)")
    print(f"  - Latitude-dependent parameters")
    
    print("\n" + "=" * 100)
    print("RECOMMENDATION:")
    print("=" * 100)
    print("The temperature model should adjust based on latitude:")
    print("  - Equator (0°): T_avg ≈ 25°C, T_amp ≈ 5°C")
    print("  - Mid-lat (30-40°): T_avg ≈ 15°C, T_amp ≈ 15°C")
    print("  - Polar (70-90°): T_avg ≈ -20°C, T_amp ≈ 30°C")

if __name__ == "__main__":
    debug_extreme_temperature()
