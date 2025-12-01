"""
Debug 1-Axis Horizontal Dip
Traces the internal variables of the 1-Axis Horizontal tracker
for Day 355 at Latitude -32 (Perth) to investigate noon dip.
"""

from solar_model import SolarModel
import numpy as np
import pandas as pd

def debug_horizontal_dip():
    print("Debugging 1-Axis Horizontal Noon Dip")
    print("Location: Perth (Lat -32.05)")
    print("Day: 355 (Summer Solstice)")
    print("=" * 100)
    
    model = SolarModel(latitude=-32.05, longitude=115.89)
    day = 355
    efficiency = 0.14
    
    print(f"{'Hour':<5} | {'H_deg':<7} | {'Sun_El':<7} | {'Sun_Az':<7} | {'Rho':<7} | {'N_z':<6} | {'P_Tilt':<7} | {'P_Az':<7} | {'Inc_Ang':<7} | {'Ic (W)':<7} | {'P_out':<7}")
    print("-" * 100)
    
    for hour in range(24):
        geom = model.calculate_geometry(day, hour)
        if geom['elevation'] <= 0: continue
        
        irrad = model.calculate_irradiance(day, geom['elevation'])
        T_amb = model.calculate_ambient_temperature(day, hour)
        
        # Extract variables
        beta = geom['elevation']
        phi_s = geom['azimuth']
        Ib = irrad['dni']
        C = irrad['diffuse_factor']
        omega = geom['hour_angle']
        
        # --- Replicate 1-Axis Horizontal Logic ---
        axis_tilt_horiz = 0
        axis_azimuth_horiz = 180 # South for S. Hem
        
        # Axis Vector k
        az_rad_h = np.radians(axis_azimuth_horiz)
        tilt_rad_h = np.radians(axis_tilt_horiz)
        k_x_h = np.cos(tilt_rad_h) * np.sin(az_rad_h)
        k_y_h = np.cos(tilt_rad_h) * np.cos(az_rad_h)
        k_z_h = np.sin(tilt_rad_h)
        
        # Noon Normal n0 (Flat)
        panel_azimuth_noon = 0 # North (doesn't matter if flat)
        n0_az_rad_h = np.radians(panel_azimuth_noon)
        n0_tilt_rad_h = np.pi/2 - tilt_rad_h # 90 deg (Vertical normal = Flat panel)
        
        n0_x_h = np.cos(n0_tilt_rad_h) * np.sin(n0_az_rad_h)
        n0_y_h = np.cos(n0_tilt_rad_h) * np.cos(n0_az_rad_h)
        n0_z_h = np.sin(n0_tilt_rad_h)
        
        # Rotation Rho (with mechanical stop limit)
        omega_rad = np.radians(omega)
        if k_y_h >= 0:
            rho_rad_h = np.clip(omega_rad, -np.pi/2, np.pi/2)
        else:
            rho_rad_h = np.clip(-omega_rad, -np.pi/2, np.pi/2)
            
        # Cross product
        v_cross_x_h = k_y_h * n0_z_h - k_z_h * n0_y_h
        
        # Rotated Normal
        n_rot_x_h = v_cross_x_h * np.sin(rho_rad_h)
        n_rot_y_h = n0_y_h * np.cos(rho_rad_h)
        n_rot_z_h = n0_z_h * np.cos(rho_rad_h)
        
        if n_rot_z_h < 0:
            sigma_horiz = 0
            phi_c = 0
            Ic = 0
            cos_theta = 0
        else:
            # Panel tilt from horizontal = 90° - elevation of normal
            sigma_horiz = 90.0 - np.degrees(np.arcsin(np.clip(n_rot_z_h, -1, 1)))
            phi_c = np.degrees(np.arctan2(n_rot_x_h, n_rot_y_h))
            
            Ic, cos_theta = model.calculate_incident_irradiance(beta, phi_s, sigma_horiz, phi_c, Ib, C)
            
        res = model.calculate_pv_performance(Ic, cos_theta, T_amb=T_amb, efficiency=efficiency)
        
        print(f"{hour:<5} | {omega:<7.1f} | {beta:<7.1f} | {phi_s:<7.1f} | {np.degrees(rho_rad_h):<7.1f} | {n_rot_z_h:<6.3f} | {sigma_horiz:<7.1f} | {phi_c:<7.1f} | {np.degrees(np.arccos(cos_theta)):<7.1f} | {Ic:<7.1f} | {res['P_out']:<7.1f}")

if __name__ == "__main__":
    debug_horizontal_dip()
