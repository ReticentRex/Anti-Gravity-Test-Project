from solar_model import SolarModel
import pandas as pd
import numpy as np

def test_polar_azimuth_range():
    print("Testing 1-Axis Polar Azimuth Range (90 to 180)...")
    lat = -32
    tilt = 32
    
    azimuths = [180, 150, 120, 91, 90, 89, 0]
    
    for az in azimuths:
        model = SolarModel(latitude=lat, longitude=0)
        df, totals = model.generate_annual_profile(fixed_tilt=tilt, fixed_azimuth=az)
        yield_val = totals['Annual_Yield_1Axis_Polar_kWh_m2']
        print(f"Panel Azimuth {az}: {yield_val:.2f} kWh/m2")

if __name__ == "__main__":
    test_polar_azimuth_range()
