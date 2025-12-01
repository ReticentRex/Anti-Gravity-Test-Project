"""
Debug Extreme Latitude Irradiance
Investigates why irradiance is so high at latitude -80° in summer.
Outputs to CSV for analysis.
"""

from solar_model import SolarModel
import pandas as pd

def debug_extreme_latitude():
    print("Debugging Extreme Latitude Irradiance")
    print("=" * 100)
    
    # Test at -80° (Antarctica) on summer solstice (Day 355)
    model = SolarModel(latitude=-80.0, longitude=0.0)
    day = 355  # Summer solstice for Southern Hemisphere
    
    data = []
    
    for hour in range(24):
        geom = model.calculate_geometry(day, hour)
        irrad = model.calculate_irradiance(day, geom['elevation'])
        
        data.append({
            'Hour': hour,
            'Elevation_deg': geom['elevation'],
            'Azimuth_deg': geom['azimuth'],
            'Hour_Angle_deg': geom['hour_angle'],
            'Declination_deg': geom['declination'],
            'DNI_W_m2': irrad['dni'],
            'GHI_W_m2': irrad['global_horizontal'],
            'Diffuse_Factor': irrad['diffuse_factor']
        })
    
    df = pd.DataFrame(data)
    
    # Calculate daily totals
    dni_daily_kwh = df['DNI_W_m2'].sum() / 1000.0
    ghi_daily_kwh = df['GHI_W_m2'].sum() / 1000.0
    
    print(f"\nLocation: Latitude -80°, Day 355 (Summer Solstice)")
    print(f"Daily DNI Total: {dni_daily_kwh:.2f} kWh/m²")
    print(f"Daily GHI Total: {ghi_daily_kwh:.2f} kWh/m²")
    print(f"\nSun elevation range: {df['Elevation_deg'].min():.1f}° to {df['Elevation_deg'].max():.1f}°")
    print(f"Hours with sun above horizon: {(df['Elevation_deg'] > 0).sum()}")
    
    # Save to CSV
    df.to_csv('extreme_latitude_irradiance.csv', index=False)
    print(f"\nData saved to extreme_latitude_irradiance.csv")
    
    # Compare with mid-latitude (Perth, -32°)
    print("\n" + "=" * 100)
    print("COMPARISON: Mid-Latitude (Perth, -32°)")
    print("=" * 100)
    
    model_mid = SolarModel(latitude=-32.0, longitude=115.89)
    data_mid = []
    
    for hour in range(24):
        geom = model_mid.calculate_geometry(day, hour)
        irrad = model_mid.calculate_irradiance(day, geom['elevation'])
        
        data_mid.append({
            'Hour': hour,
            'Elevation_deg': geom['elevation'],
            'DNI_W_m2': irrad['dni'],
            'GHI_W_m2': irrad['global_horizontal']
        })
    
    df_mid = pd.DataFrame(data_mid)
    dni_daily_kwh_mid = df_mid['DNI_W_m2'].sum() / 1000.0
    ghi_daily_kwh_mid = df_mid['GHI_W_m2'].sum() / 1000.0
    
    print(f"\nDaily DNI Total: {dni_daily_kwh_mid:.2f} kWh/m²")
    print(f"Daily GHI Total: {ghi_daily_kwh_mid:.2f} kWh/m²")
    print(f"Sun elevation range: {df_mid['Elevation_deg'].min():.1f}° to {df_mid['Elevation_deg'].max():.1f}°")
    print(f"Hours with sun above horizon: {(df_mid['Elevation_deg'] > 0).sum()}")
    
    print("\n" + "=" * 100)
    print("ANALYSIS:")
    print("=" * 100)
    print(f"Extreme latitude daily total is {dni_daily_kwh / dni_daily_kwh_mid:.2f}x higher than mid-latitude")
    print(f"This is expected if sun is above horizon 24 hours (midnight sun)")
    print(f"But check if DNI values at low sun angles are realistic!")

if __name__ == "__main__":
    debug_extreme_latitude()
