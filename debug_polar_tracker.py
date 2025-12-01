"""
Debug Polar Tracker Implementation
Generates a CSV file with step-by-step vector calculations for a full day.
"""

import numpy as np
import pandas as pd

def debug_polar_tracker():
    print("Generating polar tracker debug data...")
    
    # Perth location
    latitude = -32.05
    longitude = 115.89
    
    # Test case: Summer solstice (day 355)
    day = 355
    
    results = []
    
    # Iterate through daylight hours
    for hour in np.arange(6, 19, 1):
        # --- 1. Solar Geometry ---
        # (Simplified calculations for verification)
        delta_deg = 23.45
        
        # Equation of time
        B_deg = (360.0 / 364.0) * (day - 81)
        B_rad = np.radians(B_deg)
        E_min = 9.87 * np.sin(2*B_rad) - 7.53 * np.cos(B_rad) - 1.5 * np.sin(B_rad)
        
        # Solar time
        utc_offset = 8
        local_time_meridian = utc_offset * 15
        time_correction_min = 4 * (longitude - local_time_meridian) + E_min
        solar_time_hours = hour + time_correction_min / 60
        
        # Hour angle
        H_deg = 15 * (12 - solar_time_hours)
        
        # Solar elevation
        lat_rad = np.radians(latitude)
        delta_rad = np.radians(delta_deg)
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
            # If cos(H) >= tan(delta)/tan(lat), then |phi_s| <= 90
            check_val = np.tan(delta_rad) / np.tan(lat_rad)
            if not (np.cos(H_rad) >= check_val):
                # Sun is in the South (far side)
                if phi_s_deg > 0:
                    phi_s_deg = 180 - phi_s_deg
                else:
                    phi_s_deg = -180 - phi_s_deg

        # --- 2. Polar Tracker Vectors ---
        
        # Axis definition
        axis_tilt_polar = abs(latitude)
        axis_azimuth_polar = 180 # South
        
        az_rad = np.radians(axis_azimuth_polar)
        tilt_rad = np.radians(axis_tilt_polar)
        
        k_x = np.cos(tilt_rad) * np.sin(az_rad)
        k_y = np.cos(tilt_rad) * np.cos(az_rad)
        k_z = np.sin(tilt_rad)
        
        # Initial panel normal (at noon)
        panel_azimuth_noon = 0 # North
        n0_az_rad = np.radians(panel_azimuth_noon)
        n0_tilt_rad = np.pi/2 - tilt_rad
        
        n0_x = np.cos(n0_tilt_rad) * np.sin(n0_az_rad)
        n0_y = np.cos(n0_tilt_rad) * np.cos(n0_az_rad)
        n0_z = np.sin(n0_tilt_rad)
        
        # Rotation
        omega_rad = np.radians(H_deg)
        rho_rad = omega_rad if k_y >= 0 else -omega_rad
        
        v_cross_x = k_y * n0_z - k_z * n0_y
        n_rot_x = v_cross_x * np.sin(rho_rad)
        n_rot_y = n0_y * np.cos(rho_rad)
        n_rot_z = n0_z * np.cos(rho_rad)
        
        # --- 3. Extract Orientation ---
        if n_rot_z < 0:
            sigma_polar = 0
            phi_c_polar = 0
        else:
            n_rot_z_clipped = np.clip(n_rot_z, -1.0, 1.0)
            sigma_polar = np.degrees(np.arccos(n_rot_z_clipped))
            phi_c_polar = np.degrees(np.arctan2(n_rot_x, n_rot_y))
            
        # --- 4. Alignment Check ---
        # Sun vector (pointing to sun)
        sun_x = np.cos(np.radians(beta_deg)) * np.sin(np.radians(phi_s_deg))
        sun_y = np.cos(np.radians(beta_deg)) * np.cos(np.radians(phi_s_deg))
        sun_z = np.sin(np.radians(beta_deg))
        
        # Dot product
        alignment = sun_x*n_rot_x + sun_y*n_rot_y + sun_z*n_rot_z
        aoi_check = np.degrees(np.arccos(np.clip(alignment, -1, 1)))
        
        results.append({
            'Hour': hour,
            'Solar_Time': solar_time_hours,
            'Sun_Elev': beta_deg,
            'Sun_Azimuth': phi_s_deg,
            'Panel_Tilt': sigma_polar,
            'Panel_Azimuth': phi_c_polar,
            'AOI_Check': aoi_check,
            'n_rot_x': n_rot_x,
            'n_rot_y': n_rot_y,
            'n_rot_z': n_rot_z,
            'sun_x': sun_x,
            'sun_y': sun_y,
            'sun_z': sun_z
        })
    
    df = pd.DataFrame(results)
    output_file = 'polar_tracker_debug.csv'
    df.to_csv(output_file, index=False)
    print(f"Debug data saved to {output_file}")

if __name__ == "__main__":
    debug_polar_tracker()
