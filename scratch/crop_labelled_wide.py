import os
import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

output_dir = "assets/processed/panels_labelled_wide"
os.makedirs(output_dir, exist_ok=True)

labels_sheet = pygame.image.load("assets/items_label.png")

cell_w = 256
cell_h = 256
rows = 4
cols = 6

for r in range(rows):
    for c in range(cols):
        # Shift the 256x256 cell up by 40 pixels to capture text above
        x = c * cell_w
        y = max(0, r * cell_h - 40)
        rect = pygame.Rect(x, y, cell_w, cell_h)
        
        sub = labels_sheet.subsurface(rect)
        pygame.image.save(sub, f"{output_dir}/label_r{r}_c{c}.png")
        
print("Wide label crops completed successfully!")
