"""
Debug 1-Axis Horizontal Early Morning Rotation
Investigates why the tracker produces no power at sunrise (hour 6).
"""

from solar_model import SolarModel
import numpy as np

def debug_morning_rotation():
    print("=" * 100)
    print("Debugging 1-Axis Horizontal Early Morning (Hour 6)")
    print("Location: Perth (Lat -32.05), Day 355")
    print("=" * 100)
    
    model = SolarModel(latitude=-32.05, longitude=115.89)
    day = 355
    hour = 6
    
    geom = model.calculate_geometry(day, hour)
    print(f"\nSun Position:")
    print(f"  Elevation: {geom['elevation']:.1f}°")
    print(f"  Azimuth: {geom['azimuth']:.1f}°")
    print(f"  Hour Angle: {geom['hour_angle']:.1f}°")
    
    # Horizontal tracker setup
    axis_tilt = 0  # Horizontal
    axis_azimuth = 180  # South for S. Hem
    
    print(f"\nTracker Setup:")
    print(f"  Axis Tilt: {axis_tilt}°")
    print(f"  Axis Azimuth: {axis_azimuth}° (South)")
    
    # Calculate axis vector k
    az_rad = np.radians(axis_azimuth)
    tilt_rad = np.radians(axis_tilt)
    
    k_x = np.cos(tilt_rad) * np.sin(az_rad)
    k_y = np.cos(tilt_rad) * np.cos(az_rad)
    k_z = np.sin(tilt_rad)
    
    print(f"\nAxis Vector k: ({k_x:.3f}, {k_y:.3f}, {k_z:.3f})")
    
    # Initial panel normal (noon position)
    panel_azimuth_noon = 0  # Doesn't matter for flat panel
    n0_az_rad = np.radians(panel_azimuth_noon)
    n0_tilt_rad = np.pi/2 - tilt_rad  # 90° (vertical = flat panel)
    
    n0_x = np.cos(n0_tilt_rad) * np.sin(n0_az_rad)
    n0_y = np.cos(n0_tilt_rad) * np.cos(n0_az_rad)
    n0_z = np.sin(n0_tilt_rad)
    
    print(f"Initial Normal n0 (noon): ({n0_x:.3f}, {n0_y:.3f}, {n0_z:.3f})")
    print(f"  → Panel is FLAT (normal pointing UP)")
    
    # Rotation angle
    omega_rad = np.radians(geom['hour_angle'])
    
    if k_y >= 0:
        rho_rad = omega_rad
    else:
        rho_rad = -omega_rad
    
    print(f"\nRotation:")
    print(f"  Hour Angle (omega): {geom['hour_angle']:.1f}°")
    print(f"  Rotation (rho): {np.degrees(rho_rad):.1f}°")
    print(f"  (Note: k_y = {k_y:.1f}, so rho = -omega)")
    
    # Rotated normal
    v_cross_x = k_y * n0_z - k_z * n0_y
    
    n_rot_x = v_cross_x * np.sin(rho_rad)
    n_rot_y = n0_y * np.cos(rho_rad)
    n_rot_z = n0_z * np.cos(rho_rad)
    
    print(f"\nRotated Normal n_rot: ({n_rot_x:.3f}, {n_rot_y:.3f}, {n_rot_z:.3f})")
    print(f"  n_rot_z = {n_rot_z:.3f}")
    
    if n_rot_z < 0:
        print(f"  ❌ PROBLEM: n_rot_z < 0 means panel is UPSIDE DOWN!")
        print(f"     The panel has rotated {np.degrees(rho_rad):.1f}° and flipped over.")
        print(f"     Panel normal is pointing DOWNWARD.")
    else:
        print(f"  ✓ Panel normal is pointing upward")
    
    print("\n" + "=" * 100)
    print("ANALYSIS:")
    print("=" * 100)
    print("\nA 1-axis horizontal tracker rotates a flat panel around a horizontal N-S axis.")
    print("The rotation angle equals the hour angle: rho = H")
    print()
    print("At hour 6 (6am), H = 93.9° (6.26 hours before noon × 15°/hour)")
    print("Rotating by 93.9° from vertical flips the panel past horizontal!")
    print()
    print("cos(93.9°) = -0.067 (negative!)")
    print("This means the panel normal has rotated more than 90° from vertical,")
    print("so it's pointing downward. The panel is facing the ground.")
    print()
    print("SOLUTION:")
    print("Real horizontal trackers have mechanical limits (typically ±90° from vertical).")
    print("When H > 90°, the panel should stay at its maximum tilt (horizontal, edge-on).")
    print("We need to clamp the rotation: rho = clamp(H, -90°, +90°)")

if __name__ == "__main__":
    debug_morning_rotation()
