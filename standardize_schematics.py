from PIL import Image
import os

base_path = r"c:\Users\Ryan\Desktop\Random BS\Anti Gravity Test Project\Collector Images"

# Target dimensions (width x height) - standard size for all schematics
TARGET_WIDTH = 1024
TARGET_HEIGHT = 600

def resize_and_pad(image_path):
    """Resize image to fit within target dimensions and center it on a white canvas"""
    img = Image.open(image_path)
    print(f"\n{os.path.basename(image_path)}")
    print(f"  Original size: {img.size}")
    
    # Calculate scaling to fit within target dimensions while maintaining aspect ratio
    width_ratio = TARGET_WIDTH / img.width
    height_ratio = TARGET_HEIGHT / img.height
    scale = min(width_ratio, height_ratio)
    
    # Resize
    new_width = int(img.width * scale)
    new_height = int(img.height * scale)
    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    print(f"  Resized to: {resized.size}")
    
    # Create white canvas
    canvas = Image.new('RGB', (TARGET_WIDTH, TARGET_HEIGHT), 'white')
    
    # Calculate position to center the image
    x_offset = (TARGET_WIDTH - new_width) // 2
    y_offset = (TARGET_HEIGHT - new_height) // 2
    
    # Paste resized image onto canvas
    canvas.paste(resized, (x_offset, y_offset))
    print(f"  Final size: {canvas.size} (centered)")
    
    # Save
    canvas.save(image_path)
    return canvas.size

# List of images to process
images = [
    "horizontal_panel_schematic_1763815355294.png",
    "fixed_custom_schematic_1763815554067.png",
    "one_axis_azimuth_schematic_1763815278060.png",
    "one_axis_elevation_schematic_1763815294214.png",
    "two_axis_tracking_schematic_1763815319309.png",
    "Polar axis tracking collector orientation.png",
    "East-West Collector Configuration Schematic.png",
    "North-South Collector Configuration Schematic.png"
]

print(f"Processing images to standard size: {TARGET_WIDTH}x{TARGET_HEIGHT}")
print("=" * 60)

for img_name in images:
    img_path = os.path.join(base_path, img_name)
    if os.path.exists(img_path):
        resize_and_pad(img_path)
    else:
        print(f"\n⚠️ Not found: {img_name}")

print("\n✅ All images processed!")
