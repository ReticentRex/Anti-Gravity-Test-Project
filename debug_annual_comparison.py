import numpy as np
import pandas as pd
from solar_model import SolarModel

# Create model for latitude -32°S
model = SolarModel(latitude=-32.0, longitude=115.0)

print("Running annual simulation...")
df, totals = model.generate_annual_profile(efficiency=0.14, time_step_minutes=60)

# Calculate average energy densities (kWh/m²)
avg_1axis_horiz = totals['Annual_Yield_1Axis_Horizontal_kWh_m2']
avg_2axis = totals['Annual_Yield_2Axis_kWh_m2']

print(f"\n=== ANNUAL RESULTS ===")
print(f"1-Axis Horizontal: {avg_1axis_horiz:.1f} kWh/m²")
print(f"2-Axis Tracker:    {avg_2axis:.1f} kWh/m²")
print(f"Ratio: {avg_1axis_horiz/avg_2axis:.1%}")

# Look at winter vs summer performance
winter_days = range(152, 244)  # June-Aug for Southern Hemisphere
summer_days = list(range(1, 60)) + list(range(335, 366))  # Dec-Feb

df_winter = df[df['Day'].isin(winter_days)]
df_summer = df[df['Day'].isin(summer_days)]

winter_1h = (df_winter['P_1Axis_Horiz'] * df_winter['Time_Step_Hours']).sum() / 1000
winter_2a = (df_winter['P_2Axis'] * df_winter['Time_Step_Hours']).sum() / 1000
summer_1h = (df_summer['P_1Axis_Horiz'] * df_summer['Time_Step_Hours']).sum() / 1000
summer_2a = (df_summer['P_2Axis'] * df_summer['Time_Step_Hours']).sum() / 1000

print(f"\n=== SEASONAL BREAKDOWN ===")
print(f"WINTER (Jun-Aug):")
print(f"  1-Axis Horizontal: {winter_1h:.1f} kWh/m²")
print(f"  2-Axis Tracker:    {winter_2a:.1f} kWh/m²")
print(f"  Ratio: {winter_1h/winter_2a:.1%}")

print(f"\nSUMMER (Dec-Feb):")
print(f"  1-Axis Horizontal: {summer_1h:.1f} kWh/m²")
print(f"  2-Axis Tracker:    {summer_2a:.1f} kWh/m²")
print(f"  Ratio: {summer_1h/summer_2a:.1%}")

# Check a specific winter day at noon
day_172 = df[(df['Day'] == 172) & (df['Hour'] >= 11.5) & (df['Hour'] <= 12.5)]
if len(day_172) > 0:
    row = day_172.iloc[0]
    print(f"\n=== WINTER SOLSTICE NOON (Day 172) ===")
    print(f"Sun Elevation: {row['Elevation_deg']:.2f}°")
    print(f"Sun Azimuth: {row['Azimuth_deg']:.2f}°")
    print(f"DNI: {row['DNI_W_m2']:.1f} W/m²")
    print(f"1-Axis Horizontal Power: {row['P_1Axis_Horiz']:.1f} W/m²")
    print(f"2-Axis Power: {row['P_2Axis']:.1f} W/m²")
    print(f"Ratio: {row['P_1Axis_Horiz']/row['P_2Axis']:.1%}")

# Check a summer day at noon
day_355 = df[(df['Day'] == 355) & (df['Hour'] >= 11.5) & (df['Hour'] <= 12.5)]
if len(day_355) > 0:
    row = day_355.iloc[0]
    print(f"\n=== SUMMER SOLSTICE NOON (Day 355) ===")
    print(f"Sun Elevation: {row['Elevation_deg']:.2f}°")
    print(f"1-Axis Horizontal Power: {row['P_1Axis_Horiz']:.1f} W/m²")
    print(f"2-Axis Power: {row['P_2Axis']:.1f} W/m²")
    print(f"Ratio: {row['P_1Axis_Horiz']/row['P_2Axis']:.1%}")
