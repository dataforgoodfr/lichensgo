def hex_to_rgb(hex_color):
    """Convert hex color to RGB."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    """Convert RGB color to hex."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

def lighten_color(rgb_color, factor=0.5):
    """Lighten the color by mixing it with white."""
    white = (255, 255, 255)
    return tuple(int((1 - factor) * c + factor * w) for c, w in zip(rgb_color, white))

def create_pastel_palette(base_palette, factor=0.5):
    """Create a pastel version of the base color palette."""
    pastel_palette = []
    for hex_color in base_palette:
        rgb_color = hex_to_rgb(hex_color)
        pastel_rgb = lighten_color(rgb_color, factor)
        pastel_hex = rgb_to_hex(pastel_rgb)
        pastel_palette.append(pastel_hex)
    return pastel_palette


if __name__ == "__main__":

    base_color_palette = [
    "#333D43",
    "#37444C",
    "#3A4C58",
    "#3C5665",
    "#3D6176",
    "#3C6D8C",
    "#387CA6",
    "#4A86AB",
    "#608FAD",
    "#799AAF",
    "#90A7B5",
    "#A6B6BF",
    "#BDC6CC",
]

    # Create a pastel version of the base color palette
    pastel_color_palette = create_pastel_palette(base_color_palette, factor=0.7)

    # Print the pastel color palette
    print("Pastel Color Palette:", pastel_color_palette)
