from solar_model import SolarModel
import numpy as np

def test_location(lat, name):
    print(f"\n--- Testing {name} (Lat {lat}) ---")
    model = SolarModel(latitude=lat, longitude=0)
    
    # Test Summer Solstice (Dec 21, n=355) -> Sun at -23.45
    # Test Winter Solstice (Jun 21, n=172) -> Sun at +23.45
    
    days = [('Dec 21 (Sun South)', 355, -23.45), ('Jun 21 (Sun North)', 172, 23.45)]
    
    for desc, day, sun_lat in days:
        # Solar Noon (Hour = 12 approx, H=0)
        # We use H=0.001 to avoid division by zero or exact boundary edge cases if any
        # Actually solar_model calculates H from hour.
        # We can just look at the result.
        
        # To get Solar Noon exactly, we need to account for Eq of Time.
        # But calculate_geometry takes 'hour' (local time).
        # Let's just run for 12:00 local time and check the azimuth.
        # Ideally we want to check if it's "Generally North" (abs(az) < 90) or "Generally South" (abs(az) > 90).
        
        geom = model.calculate_geometry(day, 12)
        az = geom['azimuth']
        el = geom['elevation']
        dec = geom['declination']
        
        # Expected direction:
        # If Lat > Sun_Lat, Sun is to the South (Az ~ 180)
        # If Lat < Sun_Lat, Sun is to the North (Az ~ 0)
        
        if lat > sun_lat:
            expected = "South (180)"
        else:
            expected = "North (0)"
            
        # Model Output Interpretation (North=0)
        if abs(az) <= 90:
            model_dir = "North (0)"
        else:
            model_dir = "South (180)"
            
        print(f"  Date: {desc}")
        print(f"    Sun Declination: {dec:.2f}")
        print(f"    Elevation: {el:.2f}")
        print(f"    Azimuth: {az:.2f} -> {model_dir}")
        print(f"    Expected: {expected}")
        
        if model_dir != expected:
            print("    [FAIL] Model predicts wrong direction!")
        else:
            print("    [PASS]")

if __name__ == "__main__":
    # Test Southern Tropic (e.g. -10)
    test_location(-10, "Southern Tropic")
    
    # Test Northern Tropic (e.g. +10)
    test_location(10, "Northern Tropic")
