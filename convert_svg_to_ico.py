from cairosvg import svg2png
from PIL import Image
import os

svg_path = "icon.svg"
png_path = "icon_tmp.png"
ico_path = "icon.ico"

# Convert SVG to PNG
svg2png(url=svg_path, write_to=png_path, output_width=256, output_height=256)

# Convert PNG to ICO
img = Image.open(png_path)
img.save(
    ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
)

os.remove(png_path)
print(f"Created {ico_path}")
