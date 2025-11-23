from solar_model import SolarModel

# Test Perth location
latitude = -32.0525
longitude = 115.89

print(f"Testing optimal tilt for Perth (Lat: {latitude}°)")
print("=" * 60)

# Test range of tilts from 20° to 35°
for tilt in range(20, 36, 1):
    model = SolarModel(latitude, longitude)
    df, totals = model.generate_annual_profile(
        fixed_tilt=float(tilt),
        fixed_azimuth=0,  # North for Southern Hemisphere
        efficiency=0.14
    )
    
    yield_kwh_m2 = totals['Annual_Yield_Fixed_kWh_m2']
    print(f"Tilt {tilt:2d}°: {yield_kwh_m2:.2f} kWh/m²")

print("\n" + "=" * 60)
print("The optimal tilt should be around 25-28° for Perth.")
print("'Tilt = Latitude' (32°) is close but not always perfectly optimal.")
