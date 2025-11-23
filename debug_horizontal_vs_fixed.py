from solar_model import SolarModel
import pandas as pd

def test_horizontal_vs_fixed():
    print("Testing Horizontal vs Fixed Custom (Lat -32, Tilt 32)...")
    lat = -32
    tilt = 32
    azimuth = 0
    
    model = SolarModel(latitude=lat, longitude=115)
    
    # Run Simulation
    df, totals = model.generate_annual_profile(fixed_tilt=tilt, fixed_azimuth=azimuth)
    
    horiz_yield = totals['Annual_Yield_Horizontal_kWh_m2']
    fixed_yield = totals['Annual_Yield_Fixed_kWh_m2']
    
    print(f"Horizontal Yield: {horiz_yield:.2f} kWh/m2")
    print(f"Fixed Custom Yield: {fixed_yield:.2f} kWh/m2")
    
    diff = fixed_yield - horiz_yield
    percent_diff = (diff / horiz_yield) * 100
    
    print(f"Difference: {diff:.2f} kWh/m2")
    print(f"Percentage Gain: {percent_diff:.2f}%")
    
    # System Yield (5kW, 14% Eff)
    sys_cap = 5.0
    eff = 0.14
    area = sys_cap / eff
    
    sys_horiz = horiz_yield * area
    sys_fixed = fixed_yield * area
    sys_diff = sys_fixed - sys_horiz
    
    print(f"\nSystem Capacity: {sys_cap} kW (Area: {area:.1f} m2)")
    print(f"System Horizontal Yield: {sys_horiz:.0f} kWh")
    print(f"System Fixed Yield: {sys_fixed:.0f} kWh")
    print(f"System Difference: {sys_diff:.0f} kWh")

if __name__ == "__main__":
    test_horizontal_vs_fixed()
