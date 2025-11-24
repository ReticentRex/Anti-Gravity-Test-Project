from PIL import Image
import os

# Resize the North-South image to match the aspect ratio of others
base_path = r"c:\Users\Ryan\Desktop\Random BS\Anti Gravity Test Project\Collector Images"
ns_path = os.path.join(base_path, "North-South Collector Configuration Schematic.png")

# Open the image
img = Image.open(ns_path)
print(f"Original size: {img.size}")

# Get reference size from another image
ref_path = os.path.join(base_path, "horizontal_panel_schematic_1763815355294.png")
ref_img = Image.open(ref_path)
print(f"Reference size: {ref_img.size}")

# Resize to match reference height while maintaining aspect ratio
target_height = ref_img.height
aspect_ratio = img.width / img.height
target_width = int(target_height * aspect_ratio)

# Resize
resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
print(f"New size: {resized.size}")

# Save (overwrite)
resized.save(ns_path)
print(f"✅ Resized and saved {ns_path}")
