"""
Debug Optimal Tilt Calculation at Various Latitudes
Tests the optimal tilt algorithm at Equator, Tropical, and Mid-Latitude locations
to verify it handles all cases correctly.
"""

from solar_model import SolarModel
import pandas as pd

def debug_optimal_tilt():
    print("Testing Optimal Tilt Calculation Across Latitudes")
    print("=" * 80)
    
    # Test locations
    locations = [
        {'name': 'Equator (Pontianak)', 'lat': 0.0, 'lon': 109.33},
        {'name': 'Tropical (Darwin)', 'lat': -12.46, 'lon': 130.84},
        {'name': 'Subtropical (Brisbane)', 'lat': -27.47, 'lon': 153.03},
        {'name': 'Mid-Latitude (Perth)', 'lat': -32.05, 'lon': 115.89},
        {'name': 'High Mid-Lat (Melbourne)', 'lat': -37.81, 'lon': 144.96}
    ]
    
    results = []
    
    for loc in locations:
        print(f"\n{loc['name']} (Lat: {loc['lat']}°)")
        print("-" * 80)
        
        model = SolarModel(latitude=loc['lat'], longitude=loc['lon'])
        
        # Test both optimization modes
        for optimize_electrical in [False, True]:
            mode = "Electrical" if optimize_electrical else "Irradiance"
            
            print(f"  Calculating optimal tilt for {mode} optimization...")
            optimal_tilt, optimal_yield = model.calculate_optimal_tilt(
                efficiency=0.14,
                optimize_electrical=optimize_electrical
            )
            
            # Also calculate what "latitude tilt" would yield
            lat_tilt = abs(loc['lat'])
            
            # Manually simulate latitude tilt for comparison
            if optimize_electrical:
                # Simulate with latitude tilt
                daylight_data = []
                for day in range(1, 366):
                    for hour in range(24):
                        geom = model.calculate_geometry(day, hour)
                        if geom['elevation'] <= 0: continue
                        
                        irrad = model.calculate_irradiance(day, geom['elevation'])
                        T_amb = model.calculate_ambient_temperature(day, hour)
                        
                        daylight_data.append({
                            'beta': geom['elevation'],
                            'phi_s': geom['azimuth'],
                            'Ib': irrad['dni'],
                            'C': irrad['diffuse_factor'],
                            'T_amb': T_amb
                        })
                
                lat_yield = 0
                panel_azimuth = 0 if loc['lat'] < 0 else 180
                
                for data in daylight_data:
                    Ic, cos_theta = model.calculate_incident_irradiance(
                        data['beta'], data['phi_s'],
                        lat_tilt, panel_azimuth,
                        data['Ib'], data['C']
                    )
                    pv_result = model.calculate_pv_performance(Ic, cos_theta, T_amb=data['T_amb'], efficiency=0.14)
                    lat_yield += (pv_result['P_out'] / 1000.0)
            else:
                lat_yield = 0  # Skip for irradiance mode
            
            improvement = ((optimal_yield - lat_yield) / lat_yield * 100) if lat_yield > 0 else 0
            
            results.append({
                'Location': loc['name'],
                'Latitude': loc['lat'],
                'Mode': mode,
                'Optimal_Tilt': optimal_tilt,
                'Latitude_Tilt': round(lat_tilt, 1),
                'Difference': round(optimal_tilt - lat_tilt, 1),
                'Optimal_Yield_kWh': round(optimal_yield, 2),
                'Lat_Yield_kWh': round(lat_yield, 2) if lat_yield > 0 else 'N/A',
                'Improvement_%': round(improvement, 2) if lat_yield > 0 else 'N/A'
            })
            
            print(f"    Optimal Tilt: {optimal_tilt}°")
            print(f"    Latitude Tilt: {lat_tilt:.1f}°")
            print(f"    Difference: {optimal_tilt - lat_tilt:+.1f}°")
            print(f"    Annual Yield: {optimal_yield:.2f} kWh/m²")
            if lat_yield > 0:
                print(f"    Improvement over Lat Tilt: {improvement:.2f}%")
    
    # Save to CSV
    df = pd.DataFrame(results)
    output_file = 'optimal_tilt_debug.csv'
    df.to_csv(output_file, index=False)
    print(f"\n{'=' * 80}")
    print(f"Results saved to {output_file}")
    print(f"{'=' * 80}")
    print("\nSummary:")
    print(df.to_string(index=False))
    
    # Analysis
    print(f"\n{'=' * 80}")
    print("ANALYSIS:")
    print("=" * 80)
    
    equator_elec = df[(df['Latitude'] == 0.0) & (df['Mode'] == 'Electrical')]
    if not equator_elec.empty:
        eq_tilt = equator_elec['Optimal_Tilt'].values[0]
        print(f"✓ Equator Optimal Tilt: {eq_tilt}°")
        if 0 <= eq_tilt <= 15:
            print("  ✓ PASS: Low tilt makes sense for equator (sun passes overhead)")
        else:
            print(f"  ✗ WARNING: {eq_tilt}° seems high for equator")
    
    # Check if optimization works at all latitudes
    for mode in ['Irradiance', 'Electrical']:
        mode_data = df[df['Mode'] == mode]
        print(f"\n{mode} Optimization:")
        for idx, row in mode_data.iterrows():
            diff = row['Difference']
            if abs(diff) > 10:
                print(f"  ⚠ {row['Location']}: Large deviation ({diff:+.1f}°) from latitude rule")
            else:
                print(f"  ✓ {row['Location']}: {row['Optimal_Tilt']}° (lat {row['Latitude_Tilt']}°, diff {diff:+.1f}°)")

if __name__ == "__main__":
    debug_optimal_tilt()
