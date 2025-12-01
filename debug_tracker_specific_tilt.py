"""
Debug Tracker-Specific Optimal Tilt
Verifies the new tracker-specific optimal tilt methods in SolarModel.
"""

from solar_model import SolarModel
import pandas as pd

def debug_tracker_tilts():
    print("Testing Tracker-Specific Optimal Tilt Calculations")
    print("=" * 80)
    
    # Test locations
    locations = [
        {'name': 'Mid-Latitude (Perth)', 'lat': -32.05, 'lon': 115.89}
    ]
    
    for loc in locations:
        print(f"\n{loc['name']} (Lat: {loc['lat']}°)")
        print("-" * 80)
        
        model = SolarModel(latitude=loc['lat'], longitude=loc['lon'])
        
        # 1. Generic Optimal Tilt (Fixed Panel)
        generic_tilt, generic_yield = model.calculate_optimal_tilt(optimize_electrical=True)
        print(f"Generic Fixed Panel Optimal Tilt: {generic_tilt}° ({generic_yield:.2f} kWh/m²)")
        
        # 2. 1-Axis Azimuth Optimal Tilt
        az_tilt, az_yield = model.calculate_optimal_tilt_1axis_azimuth(optimize_electrical=True)
        print(f"1-Axis Azimuth Optimal Tilt:      {az_tilt}° ({az_yield:.2f} kWh/m²)")
        
        # 3. 1-Axis Polar Optimal Tilt
        polar_tilt, polar_yield = model.calculate_optimal_tilt_1axis_polar(optimize_electrical=True)
        print(f"1-Axis Polar Optimal Axis Tilt:   {polar_tilt}° ({polar_yield:.2f} kWh/m²)")
        
        # Comparison
        print(f"\nDifferences vs Generic:")
        print(f"  Azimuth Tracker: {az_tilt - generic_tilt:+.0f}°")
        print(f"  Polar Tracker:   {polar_tilt - generic_tilt:+.0f}°")

if __name__ == "__main__":
    debug_tracker_tilts()
