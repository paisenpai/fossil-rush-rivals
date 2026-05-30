import pygame
import os

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

img = pygame.image.load("assets/characters_facial_expression.png")
w, h = img.get_size()
cell_sz = 418

output_dir = "assets/processed/faces"
os.makedirs(output_dir, exist_ok=True)

def remove_bg(surf, threshold=240):
    surf = surf.convert_alpha()
    w, h = surf.get_size()
    for x in range(w):
        for y in range(h):
            r, g, b, a = surf.get_at((x, y))
            # Background is very light gray or white
            if r > threshold and g > threshold and b > threshold and abs(r - g) < 15 and abs(r - b) < 15:
                surf.set_at((x, y), (0, 0, 0, 0))
    return surf

for row in range(3):
    for col in range(3):
        cx = col * cell_sz
        cy = row * cell_sz
        sub = img.subsurface(pygame.Rect(cx, cy, cell_sz, cell_sz))
        
        # Transparentize and save
        cleaned = remove_bg(sub, threshold=230)
        filename = f"face_r{row}_c{col}.png"
        pygame.image.save(cleaned, os.path.join(output_dir, filename))
        print(f"Saved sliced face: {filename}")
