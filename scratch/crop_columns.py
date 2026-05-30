import os
import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

output_dir = "assets/processed/vertical_columns"
os.makedirs(output_dir, exist_ok=True)

labels_sheet = pygame.image.load("assets/items_label.png")
w, h = labels_sheet.get_size()

cell_w = 256
cols = 6

for c in range(cols):
    rect = pygame.Rect(c * cell_w, 0, cell_w, h)
    sub = labels_sheet.subsurface(rect)
    pygame.image.save(sub, f"{output_dir}/column_{c}.png")
    
print("Vertical column slices completed!")
