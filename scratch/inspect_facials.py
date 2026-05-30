import pygame
import os

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

img = pygame.image.load("assets/characters_facial_expression.png")
w, h = img.get_size()
print(f"Loaded image size: {w}x{h}")

# Check background color by looking at the corner pixels
corner_colors = [img.get_at((0, 0)), img.get_at((w-1, 0)), img.get_at((0, h-1)), img.get_at((w-1, h-1))]
print(f"Corner colors: {corner_colors}")

# Let's count non-white columns and rows to see where content is located
row_has_pixels = []
for y in range(h):
    has_pixel = False
    for x in range(w):
        r, g, b, a = img.get_at((x, y))
        # Non-white / non-transparent check
        if not (r > 240 and g > 240 and b > 240):
            has_pixel = True
            break
    row_has_pixels.append(has_pixel)

col_has_pixels = []
for x in range(w):
    has_pixel = False
    for y in range(h):
        r, g, b, a = img.get_at((x, y))
        if not (r > 240 and g > 240 and b > 240):
            has_pixel = True
            break
    col_has_pixels.append(has_pixel)

# Group contiguous true pixels
def get_segments(pixel_list):
    segments = []
    start = None
    for i, has in enumerate(pixel_list):
        if has and start is None:
            start = i
        elif not has and start is not None:
            segments.append((start, i - 1))
            start = None
    if start is not None:
        segments.append((start, len(pixel_list) - 1))
    return segments

row_segments = get_segments(row_has_pixels)
col_segments = get_segments(col_has_pixels)

print("Row segments:", row_segments)
print("Col segments:", col_segments)
