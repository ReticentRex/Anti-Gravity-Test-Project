import sys

# Redirect output to log file
log_file = open("image_log.txt", "w")
sys.stdout = log_file
sys.stderr = log_file

print("Starting image processing...")

try:
    from PIL import Image
    import os

    base_path = r"c:\Users\Ryan\Desktop\Random BS\Anti Gravity Test Project\Collector Images"
    print(f"Base path: {base_path}")

    # 1. Rotate North-South Image
    ns_path = os.path.join(base_path, "North-South Collector Configuration Schematic.png")
    if os.path.exists(ns_path):
        try:
            img_ns = Image.open(ns_path)
            # Rotate 90 degrees clockwise (or counter-clockwise, let's do -90/270 for clockwise)
            img_ns_rotated = img_ns.rotate(-90, expand=True, fillcolor='white') 
            
            # Save as new file to avoid caching issues
            new_ns_path = os.path.join(base_path, "North-South Collector Configuration Schematic_v2.png")
            img_ns_rotated.save(new_ns_path)
            print(f"✅ Rotated and saved to {new_ns_path}")
        except Exception as e:
            print(f"❌ Error rotating N-S image: {e}")
    else:
        print(f"❌ N-S Image not found at {ns_path}")

    # 2. Standardize Frame for Polar Image
    polar_path = os.path.join(base_path, "Polar axis tracking collector orientation.png")
    ref_path = os.path.join(base_path, "horizontal_panel_schematic_1763815355294.png")

    if os.path.exists(polar_path) and os.path.exists(ref_path):
        try:
            img_polar = Image.open(polar_path)
            img_ref = Image.open(ref_path)
            
            target_size = img_ref.size # (Width, Height) of the square images
            print(f"Target Size: {target_size}")
            
            # Create new white square canvas
            new_img = Image.new("RGB", target_size, "white")
            
            # Resize Polar image to fit within target_size while maintaining aspect ratio
            img_polar.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Calculate centering position
            x_offset = (target_size[0] - img_polar.width) // 2
            y_offset = (target_size[1] - img_polar.height) // 2
            
            # Paste centered
            new_img.paste(img_polar, (x_offset, y_offset))
            
            new_polar_path = os.path.join(base_path, "Polar axis tracking collector orientation_v2.png")
            new_img.save(new_polar_path)
            print(f"✅ Resized/Padded and saved to {new_polar_path}")
            
        except Exception as e:
            print(f"❌ Error processing Polar image: {e}")
    else:
        print(f"❌ Polar or Ref Image not found")

except Exception as main_e:
    print(f"CRITICAL ERROR: {main_e}")

print("Done.")
log_file.close()
