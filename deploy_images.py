import shutil
import os

source_dir = r"C:\Users\Ryan\.gemini\antigravity\brain\855624a4-2414-475b-99c8-2ec59a5dcf49"
dest_dir = r"c:\Users\Ryan\Desktop\Random BS\Anti Gravity Test Project"

files = [
    "horizontal_panel_schematic_1763815355294.png",
    "one_axis_azimuth_schematic_1763815278060.png",
    "one_axis_elevation_schematic_1763815294214.png",
    "two_axis_tracking_schematic_1763815319309.png",
    "fixed_custom_schematic_1763815554067.png"
]

target_names = [
    "horizontal_panel_schematic.png",
    "one_axis_azimuth_schematic.png",
    "one_axis_elevation_schematic.png",
    "two_axis_tracking_schematic.png",
    "fixed_custom_schematic.png"
]

print(f"Copying from {source_dir} to {dest_dir}")

for src_name, target_name in zip(files, target_names):
    src_path = os.path.join(source_dir, src_name)
    dest_path = os.path.join(dest_dir, target_name)
    
    try:
        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            print(f"✅ Copied {target_name}")
        else:
            print(f"❌ Source not found: {src_name}")
    except Exception as e:
        print(f"❌ Error copying {target_name}: {e}")
