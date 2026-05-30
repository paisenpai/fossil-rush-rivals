import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

# Scan sliced faces for blue-ish pixels (sweat, tears) to detect Anxious/Defeated
# Blue color: b > r and b > g and b > 100
for row in range(3):
    for col in range(3):
        img = pygame.image.load(f"assets/processed/faces/face_r{row}_c{col}.png")
        w, h = img.get_size()
        
        blue_pixels = 0
        for x in range(w):
            for y in range(h):
                r, g, b, a = img.get_at((x, y))
                if a > 0:
                    # Check for blue tear/sweat drops: high blue component relative to red/green
                    if b > r + 30 and b > g + 20 and b > 120:
                        blue_pixels += 1
                        
        print(f"Face Row {row}, Col {col} has {blue_pixels} blue pixels.")
