import pygame
import numpy as np

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

img = pygame.image.load("assets/characters_facial_expression.png")
w, h = img.get_size()
print(f"Image Size: {w}x{h}")

# Background check (typically near-white/light-grey)
# Let's create a binary mask of "foreground" pixels (non-light-grey)
fg_mask = np.zeros((w, h), dtype=bool)
for x in range(w):
    for y in range(h):
        r, g, b, a = img.get_at((x, y))
        # Threshold: if not very close to light gray or white
        if not (r > 220 and g > 220 and b > 220):
            fg_mask[x, y] = True

# Let's find vertical projections of foreground pixels
v_proj = np.any(fg_mask, axis=1)

# Find contiguous column groups
col_segments = []
in_seg = False
start = 0
for x in range(w):
    if v_proj[x] and not in_seg:
        start = x
        in_seg = True
    elif not v_proj[x] and in_seg:
        if x - start > 10: # filter out tiny noise lines
            col_segments.append((start, x - 1))
        in_seg = False
if in_seg:
    col_segments.append((start, w - 1))

print("Contiguous column segments of pixels:")
for idx, (x1, x2) in enumerate(col_segments):
    print(f"Col {idx}: x={x1}..{x2} (width {x2 - x1 + 1})")

# Let's do the same vertically for each column segment to find row boundaries!
for col_idx, (x1, x2) in enumerate(col_segments):
    col_mask = fg_mask[x1:x2+1, :]
    h_proj = np.any(col_mask, axis=0)
    
    row_segments = []
    in_seg = False
    start = 0
    for y in range(h):
        if h_proj[y] and not in_seg:
            start = y
            in_seg = True
        elif not h_proj[y] and in_seg:
            if y - start > 10:
                row_segments.append((start, y - 1))
            in_seg = False
    if in_seg:
        row_segments.append((start, h - 1))
        
    print(f"\nRow segments for Col {col_idx}:")
    for row_idx, (y1, y2) in enumerate(row_segments):
        print(f"  Row {row_idx}: y={y1}..{y2} (height {y2 - y1 + 1})")
