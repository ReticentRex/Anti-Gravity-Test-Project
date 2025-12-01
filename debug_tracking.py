"""
Debug script to analyze 1-axis horizontal vs 2-axis tracker behavior.
Examines angle of incidence, irradiance calculations, and tracking geometry.
"""

import numpy as np
from solar_model import SolarModel

def main():
    # Perth location -32.05°S
    model = SolarModel(latitude=-32.05, longitude=115.89)
    
    print("=" * 80)
    print("TRACKING ALGORITHM DEBUG - Perth (-32.05°S, 115.89°E)")
    print("=" * 80)
    
    # Test key days of the year
    test_days = [
        (172, "Winter Solstice (Jun 21)", 12.0),  # Midday
        (355, "Summer Solstice (Dec 21)", 12.0),  # Midday
        (80, "Spring Equinox (Mar 21)", 12.0),    # Midday
        (172, "Winter Solstice Morning", 9.0),    # Morning
        (172, "Winter Solstice Afternoon", 15.0), # Afternoon
    ]
    
    for day, label, hour in test_days:
        print(f"\n{'=' * 80}")
        print(f"{label} - Day {day}, Hour {hour}")
        print(f"{'=' * 80}")
        
        # Get solar geometry
        geom = model.calculate_geometry(day, hour)
        beta = geom['elevation']
        phi_s = geom['azimuth']
        H_deg = geom['hour_angle']
        delta = geom['declination']
        
        if beta <= 0:
            print("Sun below horizon - skipping")
            continue
            
        # Get irradiance
        irr = model.calculate_irradiance(day, beta)
        Ib = irr['dni']
        C = irr['diffuse_factor']
        
        print(f"\nSolar Geometry:")
        print(f"  Elevation (β):     {beta:7.2f}°")
        print(f"  Azimuth (φs):      {phi_s:7.2f}°")
        print(f"  Hour Angle (H):    {H_deg:7.2f}°")
        print(f"  Declination (δ):   {delta:7.2f}°")
        print(f"  DNI (Ib):          {Ib:7.1f} W/m²")
        
        # ===== 2-AXIS TRACKER =====
        print(f"\n--- 2-Axis Tracker (Ideal) ---")
        # From line 614-619: directly faces the sun
        Ibc_2axis = Ib  # cos(theta) = 1.0
        sin_beta = np.sin(np.radians(beta))
        Idc_2axis = C * Ib * (1 + sin_beta) / 2
        Irc_2axis = 0.2 * Ib * (sin_beta + C) * (1 - sin_beta) / 2
        Ic_2axis = Ibc_2axis + Idc_2axis + Irc_2axis
        cos_theta_2axis = 1.0
        
        print(f"  Panel: Tracks sun directly")
        print(f"  cos(θ):            {cos_theta_2axis:.4f}")
        print(f"  θ (AOI):           {np.degrees(np.arccos(cos_theta_2axis)):7.2f}°")
        print(f"  Beam (Ibc):        {Ibc_2axis:7.1f} W/m²")
        print(f"  Diffuse (Idc):     {Idc_2axis:7.1f} W/m²")
        print(f"  Reflected (Irc):   {Irc_2axis:7.1f} W/m²")
        print(f"  Total Ic:          {Ic_2axis:7.1f} W/m²")
        
        # ===== 1-AXIS HORIZONTAL TRACKER =====
        print(f"\n--- 1-Axis Horizontal Tracker ---")
        # From lines 662-694
        # Axis: North-South (azimuth=0), horizontal (tilt=0)
        # Rotates about this axis by hour angle
        
        # Rotation angle (clamped to ±90°)
        omega_rad = np.radians(H_deg)
        rho_rad_h = np.clip(omega_rad, -np.pi/2, np.pi/2)
        
        # Panel normal vector after rotation
        n_rot_x_h = np.sin(rho_rad_h)
        n_rot_y_h = 0
        n_rot_z_h = np.cos(rho_rad_h)
        
        if n_rot_z_h < 0:
            print("  Panel facing down - skipping")
            continue
            
        # Panel tilt and azimuth
        n_rot_z_h = np.clip(n_rot_z_h, -1.0, 1.0)
        sigma_horiz = np.degrees(np.arccos(n_rot_z_h))
        phi_c_horiz = np.degrees(np.arctan2(n_rot_x_h, n_rot_y_h))
        
        # Calculate incident irradiance
        Ic_1axis_horiz, cos_theta_1axis_horiz = model.calculate_incident_irradiance(
            beta, phi_s, sigma_horiz, phi_c_horiz, Ib, C
        )
        
        print(f"  Rotation angle:    {np.degrees(rho_rad_h):7.2f}° (clamped hour angle)")
        print(f"  Panel Tilt (σ):    {sigma_horiz:7.2f}°")
        print(f"  Panel Azimuth (φc):{phi_c_horiz:7.2f}°")
        print(f"  cos(θ):            {cos_theta_1axis_horiz:.4f}")
        print(f"  θ (AOI):           {np.degrees(np.arccos(max(0, cos_theta_1axis_horiz))):7.2f}°")
        print(f"  Total Ic:          {Ic_1axis_horiz:7.1f} W/m²")
        
        # === MANUAL AOI CALCULATION ===
        # Verify the AOI calculation is correct
        # From Eq 8: cos(θ) = cos(β)·cos(φs - φc)·sin(σ) + sin(β)·cos(σ)
        beta_rad = np.radians(beta)
        phi_s_rad = np.radians(phi_s)
        sigma_rad = np.radians(sigma_horiz)
        phi_c_rad = np.radians(phi_c_horiz)
        
        cos_theta_manual = (np.cos(beta_rad) * np.cos(phi_s_rad - phi_c_rad) * np.sin(sigma_rad) +
                           np.sin(beta_rad) * np.cos(sigma_rad))
        
        print(f"  cos(θ) [manual]:   {cos_theta_manual:.4f}")
        
        # === COMPARISON ===
        print(f"\n--- Performance Comparison ---")
        ratio_irr = (Ic_1axis_horiz / Ic_2axis * 100) if Ic_2axis > 0 else 0
        ratio_cos = (cos_theta_1axis_horiz / cos_theta_2axis * 100) if cos_theta_2axis > 0 else 0
        
        print(f"  1-Axis Horiz Ic:   {ratio_irr:5.1f}% of 2-Axis")
        print(f"  1-Axis Horiz cos:  {ratio_cos:5.1f}% of 2-Axis")
        
        aoi_diff = np.degrees(np.arccos(max(0, cos_theta_1axis_horiz))) - np.degrees(np.arccos(cos_theta_2axis))
        print(f"  AOI difference:    {aoi_diff:7.2f}° (1-Axis - 2-Axis)")
        
    # ===== ANNUAL COMPARISON =====
    print(f"\n{'=' * 80}")
    print("ANNUAL ENERGY ANALYSIS")
    print(f"{'=' * 80}")
    
    df, totals = model.generate_annual_profile(efficiency=0.2)
    
    print(f"\nAnnual Incident Energy (kWh/m²):")
    print(f"  1-Axis Horizontal: {totals['Annual_I_1Axis_Horizontal_kWh_m2']:.1f}")
    print(f"  2-Axis:            {totals['Annual_I_2Axis_kWh_m2']:.1f}")
    
    ratio_annual = totals['Annual_I_1Axis_Horizontal_kWh_m2'] / totals['Annual_I_2Axis_kWh_m2'] * 100
    print(f"  Ratio:             {ratio_annual:.1f}%")
    
    print(f"\nAnnual Electrical Yield (kWh/m²):")
    print(f"  1-Axis Horizontal: {totals['Annual_Yield_1Axis_Horizontal_kWh_m2']:.1f}")
    print(f"  2-Axis:            {totals['Annual_Yield_2Axis_kWh_m2']:.1f}")
    
    ratio_elec = totals['Annual_Yield_1Axis_Horizontal_kWh_m2'] / totals['Annual_Yield_2Axis_kWh_m2'] * 100
    print(f"  Ratio:             {ratio_elec:.1f}%")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
