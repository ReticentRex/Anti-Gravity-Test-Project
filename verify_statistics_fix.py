from solar_model import SolarModel
import pandas as pd

def verify_statistics():
    print("Initializing SolarModel...")
    model = SolarModel(latitude=-32.05, longitude=115.89)
    
    # Run Hourly Simulation
    print("\nRunning Hourly Simulation (60 min steps)...")
    df_hourly, totals_hourly = model.generate_annual_profile(time_step_minutes=60)
    
    # Run 5-Minute Simulation
    print("\nRunning 5-Minute Simulation (5 min steps)...")
    df_5min, totals_5min = model.generate_annual_profile(time_step_minutes=5)
    
    # Compare Key Metrics
    metrics = [
        'Annual_Yield_Horizontal_kWh_m2',
        'Annual_Yield_1Axis_Azimuth_kWh_m2',
        'Annual_Yield_2Axis_kWh_m2',
        'Annual_Loss_Ang_Horiz_kWh_m2',
        'Annual_Loss_Therm_Horiz_kWh_m2'
    ]
    
    print("\n--- Comparison of Annual Totals ---")
    print(f"{'Metric':<40} | {'Hourly':<10} | {'5-Min':<10} | {'Diff %':<10}")
    print("-" * 80)
    
    for metric in metrics:
        val_hourly = totals_hourly.get(metric, 0)
        val_5min = totals_5min.get(metric, 0)
        
        if val_hourly > 0:
            diff_pct = ((val_5min - val_hourly) / val_hourly) * 100
        else:
            diff_pct = 0.0
            
        print(f"{metric:<40} | {val_hourly:<10.2f} | {val_5min:<10.2f} | {diff_pct:<10.2f}%")

    # Check Daylight Hours
    print("\n--- Daylight Hours ---")
    print(f"Hourly Count: {totals_hourly['Daylight_Hours']:.2f}")
    print(f"5-Min Count:  {totals_5min['Daylight_Hours']:.2f}")

if __name__ == "__main__":
    verify_statistics()
