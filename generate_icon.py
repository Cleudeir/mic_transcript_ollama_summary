from PIL import Image, ImageDraw, ImageFont

# Generate a simple microphone-themed icon using only Pillow (no Cairo required)
# Creates icon.ico with multiple sizes.


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Colors
    blue = (25, 118, 210, 255)  # #1976d2
    white = (255, 255, 255, 255)

    # Rounded square background
    radius = int(size * 0.18)
    margin = int(size * 0.06)
    d.rounded_rectangle(
        [margin, margin, size - margin, size - margin], radius=radius, fill=blue
    )

    # Mic body
    mic_h = int(size * 0.46)
    mic_w = int(size * 0.19)
    mic_x = (size - mic_w) // 2
    mic_y = int(size * 0.23)
    d.rounded_rectangle(
        [mic_x, mic_y, mic_x + mic_w, mic_y + mic_h], radius=int(mic_w / 2), fill=white
    )

    # Mic stem
    stem_w = int(size * 0.06)
    stem_h = int(size * 0.12)
    stem_x = (size - stem_w) // 2
    stem_y = mic_y + mic_h
    d.rounded_rectangle(
        [stem_x, stem_y, stem_x + stem_w, stem_y + stem_h],
        radius=int(stem_w / 2),
        fill=white,
    )

    # Mic base
    base_w = int(size * 0.34)
    base_h = int(size * 0.08)
    base_x = (size - base_w) // 2
    base_y = stem_y + stem_h + int(size * 0.02)
    d.rounded_rectangle(
        [base_x, base_y, base_x + base_w, base_y + base_h],
        radius=int(base_h / 2),
        fill=white,
    )

    return img


sizes = [256, 128, 64, 48, 32, 24, 16]
icons = [draw_icon(s) for s in sizes]
icons[0].save("icon.ico", format="ICO", sizes=[(s, s) for s in sizes])
print("icon.ico generated with sizes:", sizes)
