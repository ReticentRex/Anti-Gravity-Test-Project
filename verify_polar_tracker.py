"""
Verify 1-Axis Polar Tracker Implementation
Step-by-step calculation with detailed output
"""

import numpy as np

def verify_polar_tracker():
    print("="*80)
    print("POLAR TRACKER VERIFICATION")
    print("="*80)
    
    # Perth location
    latitude = -32.05
    longitude = 115.89
    
    # Test case: Summer solstice (day 355), 9am local time
    day = 355
    hour = 9.0
    
    print(f"\nLocation: Perth ({latitude}°, {longitude}°)")
    print(f"Date: Day {day} (Summer Solstice)")
    print(f"Time: {hour}:00 local")
    
    # Calculate solar geometry (simplified - using typical values)
    # In reality would call calculate_geometry(), but let's use example values
    delta_deg = 23.45  # Declination at summer solstice
    
    # Equation of time (simplified)
    B_deg = (360.0 / 364.0) * (day - 81)
    B_rad = np.radians(B_deg)
    E_min = 9.87 * np.sin(2*B_rad) - 7.53 * np.cos(B_rad) - 1.5 * np.sin(B_rad)
    
    # Solar time
    utc_offset = 8  # UTC+8
    local_time_meridian = utc_offset * 15  # 120°E
    time_correction_min = 4 * (longitude - local_time_meridian) + E_min
    solar_time_hours = hour + time_correction_min / 60
    
    # Hour angle
    H_deg = 15 * (12 - solar_time_hours)
    
    # Solar elevation (simplified)
    lat_rad = np.radians(latitude)
    delta_rad = np.radians(delta_deg)
    H_rad = np.radians(H_deg)
    
    sin_beta = np.cos(lat_rad) * np.cos(delta_rad) * np.cos(H_rad) + \
               np.sin(lat_rad) * np.sin(delta_rad)
    beta_deg = np.degrees(np.arcsin(np.clip(sin_beta, -1, 1)))
    
    # Solar azimuth (simplified)
    sin_phi = (np.cos(delta_rad) * np.sin(H_rad)) / np.cos(np.radians(beta_deg))
    phi_s_deg = np.degrees(np.arcsin(np.clip(sin_phi, -1, 1)))
    
    # Quadrant check (simplified for this example)
    # At 9am on summer solstice in Perth, sun should be in NE
    # Let's assume phi_s_deg is positive (East)
    
    print(f"\n" + "="*80)
    print("SOLAR POSITION")
    print("="*80)
    print(f"Solar Time: {solar_time_hours:.2f} hours")
    print(f"Hour Angle (H): {H_deg:.2f}°")
    print(f"Declination (δ): {delta_deg:.2f}°")
    print(f"Elevation (β): {beta_deg:.2f}°")
    print(f"Azimuth (φs): {phi_s_deg:.2f}° (positive = East)")
    
    # Now calculate polar tracker orientation
    print(f"\n" + "="*80)
    print("POLAR TRACKER CALCULATION")
    print("="*80)
    
    # Step 1: Define axis
    axis_tilt_polar = abs(latitude)  # 32.05°
    axis_azimuth_polar = 180  # Points South (toward Antarctic pole)
    
    print(f"\n1. Rotation Axis:")
    print(f"   Tilt: {axis_tilt_polar:.2f}°")
    print(f"   Azimuth: {axis_azimuth_polar:.2f}° (South)")
    
    az_rad = np.radians(axis_azimuth_polar)
    tilt_rad = np.radians(axis_tilt_polar)
    
    k_x = np.cos(tilt_rad) * np.sin(az_rad)
    k_y = np.cos(tilt_rad) * np.cos(az_rad)
    k_z = np.sin(tilt_rad)
    
    print(f"   Axis vector k:")
    print(f"   k_x (East): {k_x:7.4f}")
    print(f"   k_y (North): {k_y:7.4f}")
    print(f"   k_z (Up): {k_z:7.4f}")
    
    # Step 2: Initial panel normal (at noon)
    panel_azimuth_noon = 0  # Faces North in S. Hemisphere
    
    print(f"\n2. Initial Panel Normal (at solar noon):")
    print(f"   Panel azimuth at noon: {panel_azimuth_noon}° (North)")
    
    n0_az_rad = np.radians(panel_azimuth_noon)
    n0_tilt_rad = np.pi/2 - tilt_rad  # Perpendicular to axis
    
    n0_x = np.cos(n0_tilt_rad) * np.sin(n0_az_rad)
    n0_y = np.cos(n0_tilt_rad) * np.cos(n0_az_rad)
    n0_z = np.sin(n0_tilt_rad)
    
    print(f"   n0_tilt from horiz: {np.degrees(n0_tilt_rad):.2f}°")
    print(f"   Normal vector n₀:")
    print(f"   n0_x (East): {n0_x:7.4f}")
    print(f"   n0_y (North): {n0_y:7.4f}")
    print(f"   n0_z (Up): {n0_z:7.4f}")
    
    # Check perpendicularity
    dot_product = k_x*n0_x + k_y*n0_y + k_z*n0_z
    print(f"   k·n₀ = {dot_product:.6f} (should be ~0 if perpendicular)")
    
    # Step 3: Rotate by hour angle
    print(f"\n3. Rotation by Hour Angle:")
    print(f"   Hour angle H: {H_deg:.2f}°")
    
    omega_rad = np.radians(H_deg)
    rho_rad = omega_rad if k_y >= 0 else -omega_rad
    
    print(f"   Rotation angle ρ: {np.degrees(rho_rad):.2f}°")
    print(f"   (Note: k_y = {k_y:.4f}, so {'ρ = H' if k_y >= 0 else 'ρ = -H'})")
    
    # Calculate rotated normal
    v_cross_x = k_y * n0_z - k_z * n0_y
    n_rot_x = v_cross_x * np.sin(rho_rad)
    n_rot_y = n0_y * np.cos(rho_rad)
    n_rot_z = n0_z * np.cos(rho_rad)
    
    print(f"\n   Cross product component v_cross_x: {v_cross_x:.4f}")
    print(f"   Rotated normal vector n_rot:")
    print(f"   n_rot_x (East): {n_rot_x:7.4f}")
    print(f"   n_rot_y (North): {n_rot_y:7.4f}")
    print(f"   n_rot_z (Up): {n_rot_z:7.4f}")
    
    # Step 4: Extract panel orientation
    print(f"\n4. Panel Orientation from Rotated Normal:")
    
    if n_rot_z < 0:
        print("   ERROR: Panel facing downward (n_rot_z < 0)")
        sigma_polar = 0
        phi_c_polar = 0
    else:
        n_rot_z_clipped = np.clip(n_rot_z, -1.0, 1.0)
        sigma_polar = np.degrees(np.arccos(n_rot_z_clipped))
        phi_c_polar = np.degrees(np.arctan2(n_rot_x, n_rot_y))
        
        print(f"   Panel Tilt (σ): {sigma_polar:.2f}° (from horizontal)")
        print(f"   Panel Azimuth (φc): {phi_c_polar:.2f}°")
        
        # Interpret azimuth
        if phi_c_polar > 0:
            direction = f"East of North"
        elif phi_c_polar < 0:
            direction = f"West of North"
        else:
            direction = "North"
        print(f"   → Normal points: {direction}")
        print(f"   → Panel FACE points: opposite direction")
    
    # Step 5: Check if makes sense
    print(f"\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    print(f"\nSun is at:")
    print(f"  Elevation: {beta_deg:.1f}° (above horizon)")
    print(f"  Azimuth: {phi_s_deg:.1f}° (from North)")
    
    print(f"\nPanel normal points at:")
    print(f"  Tilt: {sigma_polar:.1f}° (from horizontal)")
    print(f"  Azimuth: {phi_c_polar:.1f}° (from North)")
    
    # For perfect tracking, panel normal should point toward sun
    # Sun vector (pointing FROM ground TO sun)
    sun_x = np.cos(np.radians(beta_deg)) * np.sin(np.radians(phi_s_deg))
    sun_y = np.cos(np.radians(beta_deg)) * np.cos(np.radians(phi_s_deg))
    sun_z = np.sin(np.radians(beta_deg))
    
    print(f"\nSun direction vector:")
    print(f"  sun_x (East): {sun_x:7.4f}")
    print(f"  sun_y (North): {sun_y:7.4f}")
    print(f"  sun_z (Up): {sun_z:7.4f}")
    
    # Normalize rotated normal
    n_mag = np.sqrt(n_rot_x**2 + n_rot_y**2 + n_rot_z**2)
    n_rot_x_norm = n_rot_x / n_mag
    n_rot_y_norm = n_rot_y / n_mag
    n_rot_z_norm = n_rot_z / n_mag
    
    # Dot product (cosine of angle between vectors)
    alignment = sun_x*n_rot_x_norm + sun_y*n_rot_y_norm + sun_z*n_rot_z_norm
    angle_between = np.degrees(np.arccos(np.clip(alignment, -1, 1)))
    
    print(f"\nAlignment check:")
    print(f"  Panel normal · Sun vector = {alignment:.4f}")
    print(f"  Angle between = {angle_between:.1f}°")
    print(f"  → Angle of Incidence (θ) = {angle_between:.1f}°")
    
    if angle_between < 5:
        print(f"  ✓ Excellent tracking!")
    elif angle_between < 15:
        print(f"  ✓ Good tracking")
    elif angle_between < 30:
        print(f"  ⚠ Moderate tracking")
    else:
        print(f"  ✗ Poor tracking - something may be wrong!")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    verify_polar_tracker()
