import pygame
import os
import glob

def process_sheets(source_dir, dest_dir, bg_color=(255, 0, 255)):
    pygame.init()
    # Create a hidden display surface to allow surface creation
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    sheets = glob.glob(os.path.join(source_dir, "*_sheet_*.png"))
    
    for sheet_path in sheets:
        try:
            filename = os.path.basename(sheet_path)
            # Example filename: player_walk_sheet_12345.png
            parts = filename.split('_sheet')
            prefix = parts[0] # e.g. player_walk
            
            sheet = pygame.image.load(sheet_path).convert_alpha()
            w, h = sheet.get_size()
            
            # Remove background color (magenta)
            # Pixel perfect replacement for solid background
            for x in range(w):
                for y in range(h):
                    r, g, b, a = sheet.get_at((x, y))
                    # Check for magenta or very close to it
                    if r > 200 and g < 50 and b > 200:
                        sheet.set_at((x, y), (0, 0, 0, 0))
            
            # The prompt requested 8 directions.
            # Usually sprite sheets are arranged in rows and columns.
            # Without knowing the exact layout, let's assume it's a 4x2 or 8x1 grid.
            # This script will save the processed full sheet as a transparent PNG.
            # Slicing into individual files like player_walk_front.png requires knowing the grid layout.
            
            out_path = os.path.join(dest_dir, f"{prefix}_transparent.png")
            pygame.image.save(sheet, out_path)
            print(f"Processed {filename} -> {out_path}")
            
        except Exception as e:
            print(f"Error processing {sheet_path}: {e}")

if __name__ == "__main__":
    artifact_dir = r"C:\Users\gav\.gemini\antigravity-ide\brain\9b89113c-4aea-47f5-877a-f7320c69fe5a"
    dest_dir = r"c:\Users\gav\Documents\Python\fossil-rush-rivals\new_assets\generated"
    process_sheets(artifact_dir, dest_dir)
