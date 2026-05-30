import os
import pygame
from typing import Dict, Optional, Tuple

from . import config

# Caches for loaded surfaces
CHARACTER_SPRITES: Dict[str, Dict[str, pygame.Surface]] = {}
ITEM_SPRITES: Dict[str, pygame.Surface] = {}
ITEM_SPRITES_SCALED: Dict[str, pygame.Surface] = {}
FACE_SPRITES: Dict[str, Dict[str, pygame.Surface]] = {}
BACKGROUND_SPRITES: Dict[str, pygame.Surface] = {}
BACKGROUND_SPRITE: Optional[pygame.Surface] = None

_loaded = False


def load_sprites() -> None:
    """Loads and caches all sprite assets. Safe to call multiple times."""
    global _loaded, BACKGROUND_SPRITE, FACE_SPRITES, BACKGROUND_SPRITES
    if _loaded:
        return

    # Base asset directories
    base_dir = "assets/sprites"
    chars_dir = os.path.join(base_dir, "characters")
    items_dir = os.path.join(base_dir, "items")

    # Load Characters
    # Expected characters and their anim states
    chars_config = {
        "player": ["front_idle", "back_idle", "left_idle", "right_idle", "walk_1", "walk_2", "digging"],
        "rival": ["front_idle", "back_idle", "left_idle", "right_idle", "walk_1", "walk_2", "digging"],
        "auctioneer": ["front_idle", "left_idle", "right_idle", "gesture"]
    }

    for char_name, states in chars_config.items():
        CHARACTER_SPRITES[char_name] = {}
        for state in states:
            filename = f"{char_name}_{state}.png"
            path = os.path.join(chars_dir, filename)
            if os.path.exists(path):
                try:
                    surf = pygame.image.load(path).convert_alpha()
                    CHARACTER_SPRITES[char_name][state] = surf
                except Exception as e:
                    print(f"Warning: Failed to load character sprite {path}: {e}")
            else:
                print(f"Warning: Character sprite file {path} not found.")

    # Load Items (fossils and terrain/decoy)
    item_files = [
        # Set A
        "set_trike_horn", "set_trike_frill", "set_trike_tooth",
        # Set B
        "set_mosasaur_tooth", "set_mosasaur_vertebra", "set_mosasaur_paddle",
        # Set C
        "set_mammoth_molar", "set_mammoth_tusk", "set_mammoth_leg",
        # Standalones
        "fossil_ammonite", "fossil_trilobite", "fossil_shark_tooth",
        "fossil_fern", "fossil_wood", "fossil_brachiopod",
        "fossil_crinoid", "fossil_coprolite", "fossil_bone_fragment",
        # Terrain / Ground
        "decoy", "hidden_dirt", "surveyed_dirt", "empty_dirt", "claimed_zone"
    ]

    for item_key in item_files:
        path = os.path.join(items_dir, f"{item_key}.png")
        if os.path.exists(path):
            try:
                surf = pygame.image.load(path).convert_alpha()
                ITEM_SPRITES[item_key] = surf
                # Cache scaled 32x32 version for the excavation grid
                scaled = pygame.transform.smoothscale(surf, (config.TILE_SIZE, config.TILE_SIZE))
                ITEM_SPRITES_SCALED[item_key] = scaled
            except Exception as e:
                print(f"Warning: Failed to load item sprite {path}: {e}")
        else:
            print(f"Warning: Item sprite file {path} not found.")

    # Load Dynamic backgrounds
    bg_dir = "assets/sprites/backgrounds"
    bg_files = {
        "homescreen": "homescreen.png",
        "playing_day": "playingscreen_day.png",
        "lab_afternoon": "laboratoryphase_afternoon.png",
        "auction_night": "auction_night.png"
    }
    
    for key, filename in bg_files.items():
        path = os.path.join(bg_dir, filename)
        if os.path.exists(path):
            try:
                surf = pygame.image.load(path).convert()
                BACKGROUND_SPRITES[key] = pygame.transform.smoothscale(surf, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            except Exception as e:
                print(f"Warning: Failed to load background {path}: {e}")
        else:
            print(f"Warning: Background file {path} not found.")

    # Load Background fallback
    bg_path = "assets/background.png"
    if os.path.exists(bg_path):
        try:
            bg_surf = pygame.image.load(bg_path).convert()
            BACKGROUND_SPRITE = pygame.transform.smoothscale(bg_surf, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        except Exception as e:
            print(f"Warning: Failed to load background {bg_path}: {e}")
    else:
        print(f"Warning: Background file {bg_path} not found.")

    # Load and Slice Facial Expressions sheet
    faces_path = "assets/characters_facial_expression.png"
    if os.path.exists(faces_path):
        try:
            faces_sheet = pygame.image.load(faces_path).convert_alpha()
            sheet_w, sheet_h = faces_sheet.get_size()

            # Sub-method to transparentize sliced face backgrounds cleanly
            def clean_face_bg(surf):
                w, h = surf.get_size()
                for x in range(w):
                    for y in range(h):
                        r, g, b, a = surf.get_at((x, y))
                        if r > 220 and g > 220 and b > 220:
                            surf.set_at((x, y), (0, 0, 0, 0))
                return surf

            # The sheet is a 4-column × 3-row grid of face portraits.
            # Row 0 = Player, Row 1 = Rival, Row 2 = Auctioneer
            # Column 0 = Focused, Column 1 = Anxious, Column 2 = Elated, Column 3 = Defeated
            #
            # Measured crop boxes (x, y, w, h) for each cell — derived from the actual image layout.
            # Each character occupies roughly 1/4 of the sheet width per column, 1/3 of the height per row.
            col_w = sheet_w // 4   # ~270 px per column
            row_h = sheet_h // 3   # ~360 px per row

            emotions_order = ["Focused", "Anxious", "Elated", "Defeated"]
            chars_order = ["player", "rival", "auctioneer"]

            for char_idx, char_name in enumerate(chars_order):
                FACE_SPRITES[char_name] = {}
                row_y = char_idx * row_h

                for col_idx, emotion in enumerate(emotions_order):
                    col_x = col_idx * col_w
                    # Add small inset padding to trim the label area at top and border noise
                    inset_top = int(row_h * 0.22)   # skip the emotion text label row
                    inset_side = int(col_w * 0.08)  # trim left/right border noise
                    crop_x = col_x + inset_side
                    crop_y = row_y + inset_top
                    crop_w = col_w - inset_side * 2
                    crop_h = row_h - inset_top - int(row_h * 0.05)

                    # Clamp to sheet bounds
                    crop_x = max(0, min(crop_x, sheet_w - 1))
                    crop_y = max(0, min(crop_y, sheet_h - 1))
                    crop_w = min(crop_w, sheet_w - crop_x)
                    crop_h = min(crop_h, sheet_h - crop_y)

                    if crop_w > 0 and crop_h > 0:
                        sub = faces_sheet.subsurface(pygame.Rect(crop_x, crop_y, crop_w, crop_h))
                        FACE_SPRITES[char_name][emotion] = clean_face_bg(sub.copy())
                
        except Exception as e:
            print(f"Warning: Failed to slice facial expressions: {e}")
    else:
        print(f"Warning: Facial expressions sheet {faces_path} not found.")

    _loaded = True


def get_character_sprite(char_name: str, state: str) -> Optional[pygame.Surface]:
    """Retrieves a character sprite surface or None if not loaded."""
    load_sprites()
    return CHARACTER_SPRITES.get(char_name, {}).get(state, None)


def get_item_sprite(item_key: str, scaled: bool = False) -> Optional[pygame.Surface]:
    """Retrieves an item or terrain sprite surface or None if not loaded."""
    load_sprites()
    if scaled:
        return ITEM_SPRITES_SCALED.get(item_key, None)
    return ITEM_SPRITES.get(item_key, None)


def get_background_sprite(key: str = "homescreen") -> Optional[pygame.Surface]:
    """Retrieves the scaled background sprite surface or None if not loaded."""
    load_sprites()
    if key in BACKGROUND_SPRITES:
        return BACKGROUND_SPRITES[key]
    return BACKGROUND_SPRITE


def get_face_sprite(char_name: str, emotion: str) -> Optional[pygame.Surface]:
    """Retrieves a character face sprite surface or None if not loaded."""
    load_sprites()
    return FACE_SPRITES.get(char_name, {}).get(emotion, None)
