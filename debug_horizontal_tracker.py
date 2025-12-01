"""
Debug 1-Axis Horizontal Tracker Implementation
Generates a CSV file with step-by-step calculations for Summer and Winter Solstices.
"""

import numpy as np
import pandas as pd

def debug_horizontal_tracker():
    print("Generating horizontal tracker debug data...")
    
    # Perth location
    latitude = -32.05
    longitude = 115.89
    
    # Test cases: Summer Solstice (Day 355) and Winter Solstice (Day 172)
    test_days = {
        'Summer': 355,
        'Winter': 172
    }
    
    # Test hours
    test_hours = [9, 12, 15]
    
    results = []
    
    for season, day in test_days.items():
        for hour in test_hours:
            # --- 1. Solar Geometry ---
            # Calculate Declination
            delta_rad = np.radians(23.45) * np.sin(2 * np.pi / 365 * (day - 81))
            delta_deg = np.degrees(delta_rad)
            
            # Equation of time
            B_deg = (360.0 / 364.0) * (day - 81)
            B_rad = np.radians(B_deg)
            E_min = 9.87 * np.sin(2*B_rad) - 7.53 * np.cos(B_rad) - 1.5 * np.sin(B_rad)
            
            # Solar time
            utc_offset = 8
            local_time_meridian = utc_offset * 15
            time_correction_min = 4 * (longitude - local_time_meridian) + E_min
            solar_time_hours = hour + time_correction_min / 60
            
            # Hour angle (Thesis convention: Positive in Morning)
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

            # --- 2. Horizontal Tracker Logic ---
            # Tilt = absolute value of hour angle (clamped at 90°)
            sigma_horiz = min(abs(H_deg), 90.0)
            
            # Azimuth of panel normal
            # Morning (H > 0): Normal points East (90)
            # Afternoon (H < 0): Normal points West (-90)
            if H_deg > 0:
                phi_c_horiz = 90.0
            else:
                phi_c_horiz = -90.0
                
            # --- 3. Angle of Incidence Calculation ---
            beta_rad = np.radians(beta_deg)
            phi_s_rad = np.radians(phi_s_deg)
            sigma_rad = np.radians(sigma_horiz)
            phi_c_rad = np.radians(phi_c_horiz)
            
            cos_theta = np.cos(beta_rad) * np.cos(phi_s_rad - phi_c_rad) * np.sin(sigma_rad) + \
                        np.sin(beta_rad) * np.cos(sigma_rad)
            
            cos_theta = max(0, cos_theta)
            theta_deg = np.degrees(np.arccos(cos_theta))
            
            results.append({
                'Season': season,
                'Hour': hour,
                'Solar_Time': round(solar_time_hours, 2),
                'H_deg': round(H_deg, 2),
                'Sun_Elev': round(beta_deg, 2),
                'Sun_Azimuth': round(phi_s_deg, 2),
                'Panel_Tilt': round(sigma_horiz, 2),
                'Panel_Azimuth': round(phi_c_horiz, 2),
                'AOI_deg': round(theta_deg, 2),
                'Cos_Theta': round(cos_theta, 4)
            })
    
    df = pd.DataFrame(results)
    output_file = 'horizontal_tracker_debug.csv'
    df.to_csv(output_file, index=False)
    print(f"Debug data saved to {output_file}")
    print(df.to_string())

if __name__ == "__main__":
    debug_horizontal_tracker()
