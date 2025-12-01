"""
Debug script to test sub-hourly time step generation
"""
import sys
sys.path.insert(0, r'c:\Users\Ryan\Desktop\Random BS\Anti Gravity Test Project')

from solar_model import SolarModel
import pandas as pd

# Create model
model = SolarModel(latitude=-32.05, longitude=115.89)

print("Testing different time steps...")
print("=" * 60)

for time_step in [60, 30, 5]:
    print(f"\nTime step: {time_step} minutes")
    print("-" * 60)
    
    df, totals = model.generate_annual_profile(
        efficiency=0.14,
        time_step_minutes=time_step
    )
    
    # Show first day's data
    day_1 = df[df['Day'] == 1].copy()
    
    print(f"Total rows in dataframe: {len(df)}")
    print(f"Rows for Day 1: {len(day_1)}")
    print(f"\nFirst 10 rows for Day 1:")
    print(day_1[['Day', 'Hour', 'Minute', 'Time_Step_Hours', 'Elevation_deg']].head(10).to_string(index=False))
    
    # Check for duplicates
    duplicates = day_1.duplicated(subset=['Day', 'Hour', 'Minute'], keep=False)
    if duplicates.sum() > 0:
        print(f"\n⚠️ WARNING: Found {duplicates.sum()} duplicate rows!")
        print(day_1[duplicates][['Day', 'Hour', 'Minute']].to_string(index=False))
    else:
        print("\n✓ No duplicates found")
    
    # Check minute values
    unique_minutes = sorted(day_1['Minute'].unique())
    print(f"Unique minute values: {unique_minutes}")
    
    # Check expected vs actual row count for Day 1
    expected_rows_per_day = 1440 // time_step  # Total minutes in day / time step
    # But we only count daylight hours, so let's just check total
    print(f"\nExpected rows per day (if all 24h): {expected_rows_per_day}")
    print(f"Actual rows for Day 1: {len(day_1)} (daylight only)")
