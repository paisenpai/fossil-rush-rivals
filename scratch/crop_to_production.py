import os
import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

output_dir = "assets/sprites"
os.makedirs(f"{output_dir}/items", exist_ok=True)
os.makedirs(f"{output_dir}/characters", exist_ok=True)

def remove_bg(surf, threshold=240):
    surf = surf.convert_alpha()
    w, h = surf.get_size()
    for x in range(w):
        for y in range(h):
            r, g, b, a = surf.get_at((x, y))
            if r > threshold and g > threshold and b > threshold and abs(r - g) < 10 and abs(r - b) < 10:
                surf.set_at((x, y), (0, 0, 0, 0))
    return surf

# Characters
print("Cropping characters...")
char_sheet = pygame.image.load("assets/characters.png")
char_crops = {
    "player": {
        "front_idle": (30, 182, 153, 223),
        "back_idle": (211, 182, 122, 223),
        "left_idle": (351, 182, 118, 223),
        "right_idle": (488, 182, 119, 223),
        "walk_1": (58, 489, 121, 229),
        "walk_2": (240, 489, 124, 229),
        "digging": (421, 489, 184, 229),
    },
    "rival": {
        "front_idle": (654, 182, 133, 223),
        "back_idle": (821, 182, 130, 223),
        "left_idle": (959, 182, 101, 223),
        "right_idle": (1099, 182, 104, 223),
        "walk_1": (674, 489, 125, 229),
        "walk_2": (856, 489, 117, 229),
        "digging": (1003, 489, 201, 229),
    },
    "auctioneer": {
        "front_idle": (287, 906, 127, 266),
        "left_idle": (474, 906, 116, 266),
        "right_idle": (650, 906, 110, 266),
        "gesture": (807, 906, 196, 266),
    }
}

for char, anims in char_crops.items():
    for anim_name, (x, y, w, h) in anims.items():
        sub = char_sheet.subsurface(pygame.Rect(x, y, w, h))
        cleaned = remove_bg(sub, threshold=230)
        pygame.image.save(cleaned, f"{output_dir}/characters/{char}_{anim_name}.png")

# Items
print("Cropping items...")
items_sheet = pygame.image.load("assets/items.png")

panels = [
  ("set_trike_horn", (76, 53, 174, 194)),
  ("set_trike_frill", (309, 68, 205, 174)),
  ("set_trike_tooth", (573, 76, 105, 155)),
  ("set_mosasaur_tooth", (779, 45, 138, 198)),
  ("set_mosasaur_vertebra", (1004, 69, 195, 170)),
  ("set_mosasaur_paddle", (1262, 76, 201, 159)),
  
  ("set_mammoth_molar", (64, 286, 185, 199)),
  ("set_mammoth_tusk", (301, 297, 201, 176)),
  ("set_mammoth_leg", (533, 275, 188, 209)),
  ("fossil_ammonite", (768, 285, 183, 190)),
  ("fossil_trilobite", (1000, 279, 191, 210)),
  ("fossil_shark_tooth", (1265, 290, 191, 188)),
  
  ("fossil_fern", (44, 501, 207, 208)),
  ("fossil_wood", (290, 512, 195, 185)),
  ("fossil_brachiopod", (533, 516, 199, 179)),
  ("fossil_crinoid", (787, 514, 123, 183)),
  ("fossil_coprolite", (994, 522, 201, 171)),
  ("fossil_bone_fragment", (1258, 528, 187, 165)),
  
  ("decoy", (40, 733, 220, 208)),
  ("hidden_dirt", (279, 737, 205, 210)),
  ("surveyed_dirt", (514, 733, 207, 213)),
  ("empty_dirt", (751, 735, 212, 213)),
  ("claimed_zone", (991, 730, 210, 218))
]

for filename, p in panels:
    rect = pygame.Rect(p[0], p[1], p[2], p[3])
    sub = items_sheet.subsurface(rect)
    cleaned = remove_bg(sub, threshold=240)
    pygame.image.save(cleaned, f"{output_dir}/items/{filename}.png")
    
print("All clean production sprites created successfully!")
