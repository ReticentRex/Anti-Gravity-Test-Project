"""
Debug Fixed North-South Tracker (Bifacial)
Compares performance at Mid-Latitude vs Equator to show the "active side flip" effect.
"""

import numpy as np
import pandas as pd

def debug_ns_tracker():
    print("Generating N-S tracker debug data...")
    
    # Locations to compare
    locations = [
        {'name': 'Perth (Mid-Lat)', 'lat': -32.05},
        {'name': 'Pontianak (Equator)', 'lat': 0.0},
        {'name': 'Darwin (Tropical)', 'lat': -12.46}
    ]
    
    # Dates: Solstices and Equinox
    dates = [
        {'name': 'Summer Solstice', 'day': 355, 'decl': -23.45},
        {'name': 'Equinox', 'day': 80, 'decl': 0.0},
        {'name': 'Winter Solstice', 'day': 172, 'decl': 23.45}
    ]
    
    results = []
    
    for loc in locations:
        for date in dates:
            # Solar Geometry at Solar Noon (simplified)
            # At solar noon, Hour Angle H = 0
            
            lat_rad = np.radians(loc['lat'])
            delta_rad = np.radians(date['decl'])
            H_rad = 0
            
            # Elevation (beta)
            sin_beta = np.cos(lat_rad) * np.cos(delta_rad) * np.cos(H_rad) + \
                       np.sin(lat_rad) * np.sin(delta_rad)
            beta_deg = np.degrees(np.arcsin(np.clip(sin_beta, -1, 1)))
            beta_rad = np.radians(beta_deg)
            
            # Azimuth (phi_s) at Noon
            # If Lat > Decl, Sun is North (Az=0 in S.Hem convention? Wait, let's check code)
            # In solar_model.py: 
            # North Hem: Noon Az = 180 (South)
            # South Hem: Noon Az = 0 (North)
            # But wait, if we are in tropics, it flips.
            
            # Let's use the formula:
            # sin(phi) = ... (0 at noon)
            # cos(phi) depends on (sin(alpha)*sin(lat) - sin(delta)) / ...
            
            # Simple geometric check for Noon Azimuth:
            if loc['lat'] > date['decl']:
                # Location is North of Sun -> Sun is South
                # In standard convention (N=0, E=90): South is 180
                # In our code convention?
                # Let's assume standard: N=0, E=90, S=180, W=270
                phi_s_deg = 180.0
            else:
                # Location is South of Sun -> Sun is North
                phi_s_deg = 0.0
                
            # --- Panel Orientations (Fixed 10° Tilt) ---
            # North Panel: Tilt 10, Azimuth 0 (North)
            # South Panel: Tilt 10, Azimuth 180 (South)
            
            # 1. North Panel
            sigma_N = np.radians(10)
            phi_c_N = np.radians(0)
            
            cos_theta_N = np.cos(beta_rad) * np.cos(np.radians(phi_s_deg) - phi_c_N) * np.sin(sigma_N) + \
                          np.sin(beta_rad) * np.cos(sigma_N)
            cos_theta_N = max(0, cos_theta_N)
            
            # 2. South Panel
            sigma_S = np.radians(10)
            phi_c_S = np.radians(180)
            
            cos_theta_S = np.cos(beta_rad) * np.cos(np.radians(phi_s_deg) - phi_c_S) * np.sin(sigma_S) + \
                          np.sin(beta_rad) * np.cos(sigma_S)
            cos_theta_S = max(0, cos_theta_S)
            
            # Combined (Average)
            cos_theta_avg = (cos_theta_N + cos_theta_S) / 2
            
            results.append({
                'Location': loc['name'],
                'Latitude': loc['lat'],
                'Season': date['name'],
                'Declination': date['decl'],
                'Sun_Elev_Noon': round(beta_deg, 2),
                'Sun_Az_Noon': phi_s_deg,
                'North_Panel_Eff': round(cos_theta_N, 4),
                'South_Panel_Eff': round(cos_theta_S, 4),
                'Combined_Eff': round(cos_theta_avg, 4),
                'Winner': 'North' if cos_theta_N > cos_theta_S else 'South'
            })
            
    df = pd.DataFrame(results)
    output_file = 'ns_tracker_debug.csv'
    df.to_csv(output_file, index=False)
    print(f"Debug data saved to {output_file}")
    print(df.to_string())

if __name__ == "__main__":
    debug_ns_tracker()
