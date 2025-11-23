from solar_model import SolarModel
import pandas as pd

def test_dual_panel():
    print("Testing Dual Panel Modes...")
    lat = -32
    model = SolarModel(latitude=lat, longitude=115)
    
    # Run Simulation
    df, totals = model.generate_annual_profile(fixed_tilt=32, fixed_azimuth=0)
    
    print("\n--- Results (kWh/m2) ---")
    print(f"Horizontal: {totals['Annual_Yield_Horizontal_kWh_m2']:.2f}")
    print(f"Fixed Custom (32, 0): {totals['Annual_Yield_Fixed_kWh_m2']:.2f}")
    print(f"Fixed East-West: {totals['Annual_Yield_Fixed_EW_kWh_m2']:.2f}")
    print(f"Fixed North-South: {totals['Annual_Yield_Fixed_NS_kWh_m2']:.2f}")
    
    # Sanity Check
    # Fixed NS (0/180) should be average of Fixed(45, 0) and Fixed(45, 180).
    # Let's calculate those manually to compare.
    
    print("\n--- Manual Check for Fixed NS ---")
    # Panel North (0)
    df_n, tot_n = model.generate_annual_profile(fixed_tilt=45, fixed_azimuth=0)
    yield_n = tot_n['Annual_Yield_Fixed_kWh_m2']
    print(f"Fixed (45, 0): {yield_n:.2f}")
    
    # Panel South (180)
    df_s, tot_s = model.generate_annual_profile(fixed_tilt=45, fixed_azimuth=180)
    yield_s = tot_s['Annual_Yield_Fixed_kWh_m2']
    print(f"Fixed (45, 180): {yield_s:.2f}")
    
    avg_ns = (yield_n + yield_s) / 2
    print(f"Average: {avg_ns:.2f}")
    print(f"Model Fixed NS: {totals['Annual_Yield_Fixed_NS_kWh_m2']:.2f}")
    
    if abs(avg_ns - totals['Annual_Yield_Fixed_NS_kWh_m2']) < 0.1:
        print("PASS: Fixed NS matches average.")
    else:
        print("FAIL: Fixed NS mismatch.")

if __name__ == "__main__":
    test_dual_panel()
