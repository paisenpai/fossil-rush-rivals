import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

img = pygame.image.load("assets/characters_facial_expression.png")
w, h = img.get_size()

# Let's check a 3x3 grid (cell size 418x418)
cell_sz = 418
for row in range(3):
    for col in range(3):
        cx = col * cell_sz
        cy = row * cell_sz
        sub = img.subsurface(pygame.Rect(cx, cy, cell_sz, cell_sz))
        
        # Count non-background pixels. Background is roughly light gray/white (r > 200, g > 200, b > 200)
        non_bg = 0
        for x in range(cell_sz):
            for y in range(cell_sz):
                r, g, b, a = sub.get_at((x, y))
                if not (r > 220 and g > 220 and b > 220):
                    non_bg += 1
        print(f"Cell ({row}, {col}) non-bg pixels: {non_bg}")
