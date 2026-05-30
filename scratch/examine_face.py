import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

# Let's inspect the Player (Col 0) for Row 0, 1, 2
for row in range(3):
    img = pygame.image.load(f"assets/processed/faces/face_r{row}_c{col}.png" if 'col' in globals() else f"assets/processed/faces/face_r{row}_c0.png")
    w, h = img.get_size()
    
    # Find the bounding box of non-transparent pixels
    min_x, max_x = w, 0
    min_y, max_y = h, 0
    for x in range(w):
        for y in range(h):
            r, g, b, a = img.get_at((x, y))
            if a > 50: # non-transparent
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
                
    print(f"Row {row} Bounding Box: x={min_x}..{max_x}, y={min_y}..{max_y} (size {max_x-min_x}x{max_y-min_y})")
    
    # The face is usually in the middle. Let's crop a 30x30 region in the lower center of the head (where mouth/eyes are)
    # The head size is roughly 150x150 in the 418x418 cell. Let's find the center of the head:
    head_cx = (min_x + max_x) // 2
    head_cy = (min_y + max_y) // 2
    
    # Print a 40x40 ASCII art of the head center
    print(f"Row {row} Face ASCII:")
    # We will sample every 3 pixels to fit in 20x20 text box
    for y in range(head_cy - 20, head_cy + 25, 3):
        line = ""
        for x in range(head_cx - 20, head_cx + 25, 2):
            r, g, b, a = img.get_at((x, y))
            # If transparent or light gray
            if a < 50 or (r > 200 and g > 200 and b > 200):
                line += " "
            elif r < 60 and g < 60 and b < 60: # very dark (eyes, outline)
                line += "#"
            elif r > 180 and g < 100 and b < 100: # reddish (blush/mouth)
                line += "O"
            else: # skin / details
                line += "."
        print(line)
    print("-" * 50)
