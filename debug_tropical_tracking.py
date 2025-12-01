"""
Debug Tropical Tracking Algorithms
Verifies solar geometry and tracker behavior in the tropics (Darwin -12.46 S).
Tests 3 scenarios: Sun North, Sun South, and Sun Overhead (Zenith).
"""

import numpy as np
import pandas as pd

def debug_tropical_tracking():
    print("Generating tropical tracking debug data...")
    
    # Location: Darwin
    latitude = -12.46
    longitude = 130.84
    
    # Scenarios
    # 1. Winter Solstice (Day 172): Decl = +23.45 (Sun North of Darwin)
    # 2. Summer Solstice (Day 355): Decl = -23.45 (Sun South of Darwin)
    # 3. Zenith Day (approx Oct 25 or Feb 17): Decl ≈ -12.46 (Sun Overhead)
    # Let's calculate the day when Decl ≈ -12.46
    # delta ≈ 23.45 * sin(...)
    # -12.46/23.45 = -0.531
    # arcsin(-0.531) ≈ -32 degrees
    # This happens twice. Let's pick Day 300 (late Oct) roughly.
    
    scenarios = [
        {'name': 'Winter (Sun North)', 'day': 172},
        {'name': 'Summer (Sun South)', 'day': 355},
        {'name': 'Zenith Pass', 'day': 298} # Approx Oct 25
    ]
    
    # Test Hours: 9am, 12pm, 3pm
    hours = [9, 12, 15]
    
    results = []
    
    for scen in scenarios:
        day = scen['day']
        
        # Calculate Declination for this day
        delta_rad = np.radians(23.45) * np.sin(2 * np.pi / 365 * (day - 81))
        delta_deg = np.degrees(delta_rad)
        
        for hour in hours:
            # --- 1. Solar Geometry ---
            # Equation of time
            B_deg = (360.0 / 364.0) * (day - 81)
            B_rad = np.radians(B_deg)
            E_min = 9.87 * np.sin(2*B_rad) - 7.53 * np.cos(B_rad) - 1.5 * np.sin(B_rad)
            
            # Solar time
            utc_offset = 9.5 # Darwin is UTC+9.5
            local_time_meridian = utc_offset * 15
            time_correction_min = 4 * (longitude - local_time_meridian) + E_min
            solar_time_hours = hour + time_correction_min / 60
            
            # Hour angle
            H_deg = 15 * (12 - solar_time_hours)
            
            # Solar elevation
            lat_rad = np.radians(latitude)
            H_rad = np.radians(H_deg)
            
            sin_beta = np.cos(lat_rad) * np.cos(delta_rad) * np.cos(H_rad) + \
                       np.sin(lat_rad) * np.sin(delta_rad)
            beta_deg = np.degrees(np.arcsin(np.clip(sin_beta, -1, 1)))
            
            # Solar azimuth
            cos_beta = np.cos(np.radians(beta_deg))
            if cos_beta == 0:
                phi_s_deg = 0
            else:
                sin_phi = (np.cos(delta_rad) * np.sin(H_rad)) / cos_beta
                phi_s_deg = np.degrees(np.arcsin(np.clip(sin_phi, -1, 1)))
                
                # Quadrant check (Southern Hemisphere logic)
                check_val = np.tan(delta_rad) / np.tan(lat_rad)
                if not (np.cos(H_rad) >= check_val):
                    if phi_s_deg > 0:
                        phi_s_deg = 180 - phi_s_deg
                    else:
                        phi_s_deg = -180 - phi_s_deg

            # --- 2. Trackers ---
            
            # A. 1-Axis Azimuth
            # Tilt = Fixed (Latitude) -> Wait, usually optimal tilt. Let's assume Latitude tilt for simplicity.
            # Actually code uses 'tilt_1axis_az'. Let's assume it's set to abs(latitude) = 12.46
            sigma_az = 12.46
            phi_c_az = phi_s_deg # Follows sun azimuth
            
            # B. 2-Axis
            sigma_2ax = 90 - beta_deg
            phi_c_2ax = phi_s_deg
            
            # C. 1-Axis Elevation
            # Logic from solar_model.py
            if abs(latitude) < 0.1:
                phi_c_el = 0
            else:
                if latitude < 0:
                    # Darwin is South (-12)
                    if delta_deg > 0 and abs(delta_deg) > abs(latitude):
                        phi_c_el = 0 # Sun is North (Winter) -> Face North
                    else:
                        phi_c_el = 180 # Sun is South (Summer) -> Face South
            
            sigma_el = 90 - beta_deg
            
            results.append({
                'Scenario': scen['name'],
                'Declination': round(delta_deg, 2),
                'Hour': hour,
                'Sun_Elev': round(beta_deg, 2),
                'Sun_Azimuth': round(phi_s_deg, 2),
                '1Ax_Az_Phi': round(phi_c_az, 2),
                '2Ax_Phi': round(phi_c_2ax, 2),
                '1Ax_El_Phi': round(phi_c_el, 2),
                '1Ax_El_Tilt': round(sigma_el, 2)
            })
            
    df = pd.DataFrame(results)
    output_file = 'tropical_tracking_debug.csv'
    df.to_csv(output_file, index=False)
    print(f"Debug data saved to {output_file}")
    print(df.to_string())

if __name__ == "__main__":
    debug_tropical_tracking()
