from typing import Dict, List, Optional

import pygame

from . import config
from . import sprites
from .fossils import Fossil, fossil_tile_size
from .grid import Grid, Tile


def draw_text(
    surface: pygame.Surface,
    text: str,
    pos: tuple[int, int],
    font: pygame.font.Font,
    color: Optional[tuple[int, int, int]] = None,
) -> None:
    text_color = color if color else config.THEME_TEXT_CREAM
    # Draw drop shadow
    shadow_pos = (pos[0] + 1, pos[1] + 1)
    shadow_rendered = font.render(text, True, config.THEME_TEXT_SHADOW)
    surface.blit(shadow_rendered, shadow_pos)
    # Draw main text
    rendered = font.render(text, True, text_color)
    surface.blit(rendered, pos)


def _panel(surface: pygame.Surface, rect: pygame.Rect) -> None:
    # 1. Background Slate Fill
    pygame.draw.rect(surface, config.THEME_STONE_MED, rect)
    
    # 2. Outer Bevel Highlight (light gray) on top and left, dark shadow on bottom and right
    # Top border (highlight)
    pygame.draw.line(surface, config.THEME_STONE_LIGHT, rect.topleft, (rect.right - 1, rect.top), 2)
    # Left border (highlight)
    pygame.draw.line(surface, config.THEME_STONE_LIGHT, rect.topleft, (rect.left, rect.bottom - 1), 2)
    # Bottom border (shadow)
    pygame.draw.line(surface, config.THEME_STONE_DARK, (rect.left + 1, rect.bottom - 2), (rect.right - 1, rect.bottom - 2), 2)
    # Right border (shadow)
    pygame.draw.line(surface, config.THEME_STONE_DARK, (rect.right - 2, rect.top + 1), (rect.right - 2, rect.bottom - 1), 2)
    
    # 3. Inner dark stone inset border
    inner_rect = rect.inflate(-4, -4)
    pygame.draw.rect(surface, config.THEME_BG, inner_rect, 1)
    
    # 4. Brass corner rivets (only if the panel is large enough)
    if rect.width > 40 and rect.height > 40:
        rivet_offsets = [
            (8, 8),                            # Top-left
            (rect.width - 8, 8),               # Top-right
            (8, rect.height - 8),              # Bottom-left
            (rect.width - 8, rect.height - 8)  # Bottom-right
        ]
        for ox, oy in rivet_offsets:
            rx, ry = rect.x + ox, rect.y + oy
            # Rivet shadow
            pygame.draw.circle(surface, config.THEME_GOLD_SHADOW, (rx + 1, ry + 1), 3)
            # Rivet base
            pygame.draw.circle(surface, config.THEME_GOLD_ACCENT, (rx, ry), 3)
            # Rivet shine
            pygame.draw.circle(surface, (255, 245, 200), (rx - 1, ry - 1), 1)


def _draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    font: pygame.font.Font,
    active: bool = False,
) -> None:
    # Check if hovered dynamically
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    
    # Check if clicked dynamically
    is_clicked = is_hovered and pygame.mouse.get_pressed()[0]
    
    # Tactile spring-loaded press offsets
    offset_x = 2 if is_clicked else 0
    offset_y = 2 if is_clicked else 0
    
    draw_rect = rect.copy()
    if is_clicked:
        # Draw a deep shadow behind the shifted button
        shadow_rect = rect.copy()
        pygame.draw.rect(surface, (15, 12, 10), shadow_rect)
        draw_rect.x += offset_x
        draw_rect.y += offset_y
        
    # Pick colors based on button state
    if active:
        border_light = config.THEME_WOOD_DARK
        border_dark = config.THEME_WOOD_LIGHT
        bg_color = (70, 40, 25) # Depressed walnut fill
        text_color = config.THEME_TEXT_GOLD
    elif is_hovered:
        border_light = (255, 230, 150) # Bright gold highlight
        border_dark = config.THEME_GOLD_SHADOW
        bg_color = (130, 80, 52) # Lighter oak wood fill
        text_color = (255, 240, 150) # Glowing golden text
    else:
        border_light = config.THEME_WOOD_LIGHT
        border_dark = config.THEME_WOOD_DARK
        bg_color = config.THEME_WOOD_MED
        text_color = config.THEME_TEXT_CREAM
        
    # Draw Walnut wooden plaque background
    pygame.draw.rect(surface, bg_color, draw_rect)
    
    # Draw outer border bevel
    pygame.draw.line(surface, border_light, draw_rect.topleft, (draw_rect.right - 1, draw_rect.top), 2)
    pygame.draw.line(surface, border_light, draw_rect.topleft, (draw_rect.left, draw_rect.bottom - 1), 2)
    pygame.draw.line(surface, border_dark, (draw_rect.left + 1, draw_rect.bottom - 2), (draw_rect.right - 1, draw_rect.bottom - 2), 2)
    pygame.draw.line(surface, border_dark, (draw_rect.right - 2, draw_rect.top + 1), (draw_rect.right - 2, draw_rect.bottom - 1), 2)
    
    # Draw inner wood-carving inset line
    inner_inset = draw_rect.inflate(-6, -6)
    inset_color = config.THEME_WOOD_DARK if not is_hovered else config.THEME_GOLD_SHADOW
    pygame.draw.rect(surface, inset_color, inner_inset, 1)
    
    # Glowing outline on hover or active selection
    if is_hovered or active:
        pygame.draw.rect(surface, config.THEME_GOLD_ACCENT, draw_rect, 1)
        
    # Embossed text drop-shadow
    shadow_surface = font.render(label, True, config.THEME_TEXT_SHADOW)
    shadow_rect = shadow_surface.get_rect(center=draw_rect.center)
    shadow_rect.x += 1
    shadow_rect.y += 1
    surface.blit(shadow_surface, shadow_rect)
    
    # Main text
    text_rendered = font.render(label, True, text_color)
    text_rect = text_rendered.get_rect(center=draw_rect.center)
    surface.blit(text_rendered, text_rect)


def _obstacle_sprite_key(grid: Grid, tile: Tile) -> str:
    north = grid.get_tile(tile.x, tile.y - 1)
    south = grid.get_tile(tile.x, tile.y + 1)
    west = grid.get_tile(tile.x - 1, tile.y)
    east = grid.get_tile(tile.x + 1, tile.y)
    nw = grid.get_tile(tile.x - 1, tile.y - 1)
    ne = grid.get_tile(tile.x + 1, tile.y - 1)
    sw = grid.get_tile(tile.x - 1, tile.y + 1)
    se = grid.get_tile(tile.x + 1, tile.y + 1)

    n = north is not None and north.obstacle
    s = south is not None and south.obstacle
    w = west is not None and west.obstacle
    e = east is not None and east.obstacle
    diag_left = (nw is not None and nw.obstacle) or (sw is not None and sw.obstacle)
    diag_right = (ne is not None and ne.obstacle) or (se is not None and se.obstacle)

    if not n and not s and not w and not e and (diag_left or diag_right):
        return "obstacle_dleft" if diag_left else "obstacle_dright"

    if not s:
        if e and not w:
            return "obstacle_left"
        if w and not e:
            return "obstacle_right"
        return "obstacle_bcenter"

    return "obstacle_center"


def draw_grid(
    surface: pygame.Surface,
    grid: Grid,
    font: pygame.font.Font,
    hover_tile: Optional[Tile],
    fossils: Dict[str, Fossil],
) -> None:
    now = pygame.time.get_ticks()
    for row in range(config.GRID_ROWS):
        for col in range(config.GRID_COLS):
            tile = grid.tiles[row][col]
            rect = pygame.Rect(
                config.GRID_LEFT + col * config.TILE_SIZE,
                config.GRID_TOP + row * config.TILE_SIZE,
                config.TILE_SIZE,
                config.TILE_SIZE,
            )
            if not tile.active:
                continue

            is_hovered = hover_tile and hover_tile.x == col and hover_tile.y == row

            # Draw the appropriate terrain, obstacle, or dirt sprite
            sprite = None
            if tile.obstacle:
                sprite_key = _obstacle_sprite_key(grid, tile)
                sprite = sprites.get_item_sprite(sprite_key, scaled=True)
            elif tile.state == "hidden":
                if tile.claimed_by:
                    sprite = sprites.get_item_sprite("claimed_zone", scaled=True)
                else:
                    sprite = sprites.get_item_sprite("hidden_dirt", scaled=True)
            elif tile.state == "surveyed":
                if tile.survey_state == "initial":
                    if now - tile.survey_started_at >= 1000:
                        tile.survey_state = tile.survey_result or "none"
                    else:
                        sprite = sprites.get_item_sprite("surveyed_dirt_initial", scaled=True)

                if not sprite:
                    if tile.survey_state == "detected":
                        sprite = sprites.get_item_sprite("surveyed_dirt_detected", scaled=True)
                    elif tile.survey_state == "none":
                        sprite = sprites.get_item_sprite("surveyed_dirt_none", scaled=True)
                    else:
                        sprite = sprites.get_item_sprite("surveyed_dirt", scaled=True)
            elif tile.state == "revealed":
                if tile.content_type == "empty":
                    sprite = sprites.get_item_sprite("empty_dirt", scaled=True)
                elif tile.content_type == "decoy":
                    sprite = sprites.get_item_sprite("decoy", scaled=True)
                elif tile.content_type == "fossil":
                    base_key = tile.last_dirt_key or "hidden_dirt"
                    sprite = sprites.get_item_sprite(base_key, scaled=True)

            # Blit sprite, or use the original fallback if sprites aren't loaded yet
            if sprite:
                surface.blit(sprite, rect)
            else:
                color = (101, 67, 33) if not is_hovered else (60, 140, 60)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, config.GRID_LINE_COLOR, rect, 1)
                label = tile.label()
                label_surface = font.render(label, True, config.TEXT_COLOR)
                label_rect = label_surface.get_rect(center=rect.center)
                surface.blit(label_surface, label_rect)

    for row in range(config.GRID_ROWS):
        for col in range(config.GRID_COLS):
            tile = grid.tiles[row][col]
            if not tile.active:
                continue
            if tile.state != "revealed" or tile.content_type != "fossil" or not tile.fossil_id:
                continue
            if tile.fossil_variant != "core":
                continue
            sprite = sprites.get_item_sprite(tile.fossil_id, scaled=False)
            if not sprite:
                continue
            tile_w, tile_h = fossil_tile_size(tile.fossil_id)
            target_size = (tile_w * config.TILE_SIZE, tile_h * config.TILE_SIZE)
            scaled = pygame.transform.smoothscale(sprite, target_size)
            rect = pygame.Rect(
                config.GRID_LEFT + col * config.TILE_SIZE,
                config.GRID_TOP + row * config.TILE_SIZE,
                target_size[0],
                target_size[1],
            )
            surface.blit(scaled, rect)

    for row in range(config.GRID_ROWS):
        for col in range(config.GRID_COLS):
            tile = grid.tiles[row][col]
            rect = pygame.Rect(
                config.GRID_LEFT + col * config.TILE_SIZE,
                config.GRID_TOP + row * config.TILE_SIZE,
                config.TILE_SIZE,
                config.TILE_SIZE,
            )
            if not tile.active:
                continue
            is_hovered = hover_tile and hover_tile.x == col and hover_tile.y == row

            # Draw progress numbers on surveyed tiles if dig has started
            if tile.state == "surveyed" and tile.content_type in {"fossil", "decoy"} and tile.dig_progress > 0:
                prog_text = str(tile.dig_progress)
                prog_surface = font.render(prog_text, True, (255, 235, 100))
                prog_rect = prog_surface.get_rect(center=rect.center)
                surface.blit(prog_surface, prog_rect)

            # Apply colour overlay on top of sprite — brown by default, green on hover
            tint_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            if is_hovered and not tile.obstacle:
                # Warm gold hover tint for cleaner placeholders
                tint_surf.fill((210, 170, 70, 90))
                surface.blit(tint_surf, rect.topleft)
                # Gold outline
                pygame.draw.rect(surface, (235, 195, 80), rect, 2)
            elif tile.claimed_by:
                claim_color = (60, 200, 80, 80) if tile.claimed_by == "player" else (210, 60, 60, 80)
                tint_surf.fill(claim_color)
                surface.blit(tint_surf, rect.topleft)
                border_color = (60, 210, 60) if tile.claimed_by == "player" else (255, 100, 100)
                pygame.draw.rect(surface, border_color, rect, 2)
            elif tile.state in {"hidden", "surveyed"}:
                # Warm earthy brown tint over unrevealed tiles
                tint_surf.fill((100, 55, 10, 70))
                surface.blit(tint_surf, rect.topleft)


def draw_characters(surface: pygame.Surface, font: pygame.font.Font, state) -> None:
    now = pygame.time.get_ticks()
    def _sprite_direction(facing: str) -> str:
        if facing in config.DIRECTION_KEYS:
            return facing
        return "s"

    def _action_pose(action_key: Optional[str]) -> Optional[str]:
        if action_key == config.ACTION_CAREFUL:
            return "mine"
        if action_key == config.ACTION_RUSH:
            return "smash"
        if action_key == config.ACTION_CLAIM:
            return "claim"
        if action_key == config.ACTION_SURVEY:
            return "survey"
        return None

    actor_settings = [
        (
            "player",
            state.player_pos,
            state.player_facing,
            (now - state.player_last_move_ticks) < config.MOVE_COOLDOWN_MS,
            state.player_last_action,
            state.player_last_action_ticks,
        ),
        (
            "rival",
            state.ai_pos,
            state.ai_facing,
            (now - state.ai_last_move_ticks) < config.MOVE_COOLDOWN_MS,
            state.ai_last_action,
            state.ai_last_action_ticks,
        ),
    ]

    for actor_key, (col, row), facing, is_moving, last_action, last_action_ticks in actor_settings:
        tile_rect = pygame.Rect(
            config.GRID_LEFT + col * config.TILE_SIZE,
            config.GRID_TOP + row * config.TILE_SIZE,
            config.TILE_SIZE,
            config.TILE_SIZE,
        )
        direction = _sprite_direction(facing)
        pose = None
        if last_action and (now - last_action_ticks) <= config.ACTION_POSE_MS:
            pose = _action_pose(last_action)
        if not pose:
            pose = "walk"

        if pose in {"smash", "claim", "survey"}:
            direction = "n" if facing in {"n", "ne", "nw"} else "s"
        elif pose == "mine":
            if facing in {"n", "ne", "nw"}:
                direction = "n"
            elif facing in {"s", "se", "sw"}:
                direction = "s"
            elif facing == "w":
                direction = "w"
            else:
                direction = "e"

        sprite_key = f"{pose}_{direction}"
        sprite = sprites.get_character_sprite(actor_key, sprite_key)
        if not sprite and direction != "s":
            sprite = sprites.get_character_sprite(actor_key, f"{pose}_s")

        if sprite:
            scaled = pygame.transform.smoothscale(sprite, (config.TILE_SIZE, config.TILE_SIZE))
            surface.blit(scaled, tile_rect)
        else:
            color = (220, 180, 120) if actor_key == "player" else (210, 90, 90)
            pygame.draw.rect(surface, color, tile_rect)


def draw_excavation_hud(surface: pygame.Surface, font: pygame.font.Font, state) -> None:
    bar_width = config.EXCAVATION_TOP_BAR_WIDTH
    bar_height = config.EXCAVATION_TOP_BAR_HEIGHT
    bar_x = (config.WINDOW_WIDTH - bar_width) // 2
    bar_y = config.EXCAVATION_TOP_BAR_TOP
    hud_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    _panel(surface, hud_rect)

    time_left = max(0, state.excavation_time_left_ms)
    seconds = time_left // 1000
    time_text = f"Time Left: {seconds // 60:02d}:{seconds % 60:02d}"
    text_w = font.size(time_text)[0]
    draw_text(
        surface,
        time_text,
        (hud_rect.centerx - text_w // 2, hud_rect.y + (hud_rect.height - font.get_height()) // 2),
        font,
        config.THEME_TEXT_CREAM,
    )


def draw_narration(surface: pygame.Surface, font: pygame.font.Font, narration: str) -> None:
    grid_width = config.GRID_COLS * config.TILE_SIZE
    grid_height = config.GRID_ROWS * config.TILE_SIZE
    box_top = config.GRID_TOP + grid_height + config.ACTION_BAR_HEIGHT + (config.ACTION_BAR_GAP * 2)
    box_rect = pygame.Rect(config.GRID_LEFT, box_top, grid_width, config.NARRATION_BOX_HEIGHT)
    _panel(surface, box_rect)
    draw_text(surface, narration, (box_rect.x + 16, box_rect.y + 22), font, config.THEME_TEXT_GOLD)


def draw_header(surface: pygame.Surface, title_font: pygame.font.Font, label_font: pygame.font.Font, phase_text: str) -> None:
    if phase_text == config.PHASE_TITLE:
        return
    # Draw phase label centered at the top
    phase_w = label_font.size(phase_text)[0]
    phase_x = (config.WINDOW_WIDTH - phase_w) // 2
    draw_text(surface, phase_text, (phase_x, 24), label_font, config.THEME_TEXT_CREAM)


def _button_rects(labels: list[str], start_y: int) -> list[pygame.Rect]:
    total_height = len(labels) * config.BUTTON_HEIGHT + (len(labels) - 1) * config.BUTTON_GAP
    top = start_y
    if top == -1:
        top = (config.WINDOW_HEIGHT - total_height) // 2
    rects = []
    for index, _label in enumerate(labels):
        rect = pygame.Rect(
            (config.WINDOW_WIDTH - config.BUTTON_WIDTH) // 2,
            top + index * (config.BUTTON_HEIGHT + config.BUTTON_GAP),
            config.BUTTON_WIDTH,
            config.BUTTON_HEIGHT,
        )
        rects.append(rect)
    return rects


def draw_title_screen(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
) -> list[pygame.Rect]:
    labels = ["Start Match", "Field Journal", "Quit"]
    rects = _button_rects(labels, start_y=0)
    buttons_total_h = rects[-1].bottom - rects[0].top
    total_h = buttons_total_h
    logo_size = None
    logo_gap = 20

    title_logo = sprites.get_title_image_sprite()
    if title_logo:
        orig_w, orig_h = title_logo.get_size()
        max_w = config.WINDOW_WIDTH - 120
        max_h = 240
        scale_ratio = min(max_w / orig_w, max_h / orig_h)
        scaled_w = int(orig_w * scale_ratio)
        scaled_h = int(orig_h * scale_ratio)
        scaled_logo = pygame.transform.smoothscale(title_logo, (scaled_w, scaled_h))
        logo_size = (scaled_w, scaled_h)
        total_h += scaled_h + logo_gap

    center_y = config.WINDOW_HEIGHT // 2
    top_y = center_y - (total_h // 2)

    if title_logo and logo_size:
        logo_x = (config.WINDOW_WIDTH - logo_size[0]) // 2
        logo_y = top_y
        surface.blit(scaled_logo, (logo_x, logo_y))
        buttons_start_y = logo_y + logo_size[1] + logo_gap
    else:
        buttons_start_y = top_y

    rects = _button_rects(labels, start_y=buttons_start_y)
    for rect, label in zip(rects, labels):
        _draw_button(surface, rect, label, font)
    return rects


def draw_journal_screen(
    surface: pygame.Surface,
    font: pygame.font.Font,
    cards: list[dict],
    selected: Optional[dict],
    page: int,
    view_title: str,
    show_sets: bool,
    show_individuals: bool,
    view_mode: str,
) -> tuple[
    pygame.Rect,
    pygame.Rect,
    list[pygame.Rect],
    list[str],
    Optional[pygame.Rect],
    Optional[pygame.Rect],
    Optional[pygame.Rect],
    Optional[pygame.Rect],
]:
    top_rect = pygame.Rect(60, 120, config.WINDOW_WIDTH - 120, 60)
    left_rect = pygame.Rect(60, 200, 360, 720)
    right_rect = pygame.Rect(left_rect.right + 20, 200, config.WINDOW_WIDTH - left_rect.right - 80, 720)
    view_rect = pygame.Rect(right_rect.x + 20, right_rect.y + 20, right_rect.width - 40, 300)
    desc_rect = pygame.Rect(right_rect.x + 20, view_rect.bottom + 20, right_rect.width - 40, 260)

    for rect in [top_rect, left_rect, right_rect, view_rect, desc_rect]:
        _panel(surface, rect)

    back_rect = pygame.Rect(top_rect.x + 12, top_rect.y + 12, 120, 36)
    close_rect = pygame.Rect(top_rect.right - 132, top_rect.y + 12, 120, 36)
    
    _draw_button(surface, back_rect, "Back", font)
    _draw_button(surface, close_rect, "Close View", font)
    
    # Embossed view title
    draw_text(surface, view_title, (top_rect.x + 220, top_rect.y + 18), font, config.THEME_TEXT_GOLD)

    set_header_rect = None
    indiv_header_rect = None
    cards_top = left_rect.y + 16
    if view_mode == "root":
        set_header_rect = pygame.Rect(left_rect.x + 16, left_rect.y + 12, left_rect.width - 32, 32)
        toggle = "-" if show_sets else "+"
        _draw_button(surface, set_header_rect, f"{toggle} Sets", font, active=show_sets)
        
        indiv_header_rect = pygame.Rect(left_rect.x + 16, left_rect.y + 52, left_rect.width - 32, 32)
        toggle = "-" if show_individuals else "+"
        _draw_button(surface, indiv_header_rect, f"{toggle} Individuals", font, active=show_individuals)
        cards_top = left_rect.y + 96
    elif view_mode.startswith("set:"):
        header_rect = pygame.Rect(left_rect.x + 16, left_rect.y + 12, left_rect.width - 32, 32)
        _draw_button(surface, header_rect, "Set Pieces", font, active=True)
        cards_top = left_rect.y + 56

    per_page = config.JOURNAL_CARDS_PER_PAGE
    start = page * per_page
    visible = cards[start : start + per_page]
    card_rects: list[pygame.Rect] = []
    card_keys: list[str] = []
    col_width = (left_rect.width - 40) // 2
    row_height = 120
    for index, card in enumerate(visible):
        col = index % 2
        row = index // 2
        card_x = left_rect.x + 16 + col * (col_width + 8)
        card_y = cards_top + row * (row_height + 8)
        card_rect = pygame.Rect(card_x, card_y, col_width, row_height)
        
        # Style cards as beautiful indented slot cards
        is_selected = selected and selected.get("key") == card.get("key")
        is_hovered = card_rect.collidepoint(pygame.mouse.get_pos())
        
        pygame.draw.rect(surface, config.THEME_STONE_DARK if is_selected else config.THEME_BG, card_rect)
        pygame.draw.rect(surface, config.THEME_WOOD_DARK if is_selected else config.THEME_STONE_MED, card_rect, 1)
        
        if is_selected:
            pygame.draw.rect(surface, config.THEME_GOLD_ACCENT, card_rect, 2)
        elif is_hovered:
            pygame.draw.rect(surface, config.THEME_WOOD_LIGHT, card_rect, 1)
            
        draw_text(surface, card.get("title", ""), (card_rect.x + 10, card_rect.y + 12), font, config.THEME_TEXT_GOLD if is_selected else None)
        draw_text(surface, card.get("subtitle", ""), (card_rect.x + 10, card_rect.y + 44), font)
        
        card_rects.append(card_rect)
        card_keys.append(card.get("key", ""))

    prev_rect = None
    next_rect = None
    if len(cards) > per_page:
        prev_rect = pygame.Rect(left_rect.x + 16, left_rect.bottom - 46, 100, 32)
        next_rect = pygame.Rect(left_rect.right - 116, left_rect.bottom - 46, 100, 32)
        _draw_button(surface, prev_rect, "Prev", font)
        _draw_button(surface, next_rect, "Next", font)

    draw_text(surface, "Fossil View", (view_rect.x + 16, view_rect.y + 16), font, config.THEME_TEXT_GOLD)
    if not selected:
        draw_text(surface, "Select an entry to inspect.", (desc_rect.x + 16, desc_rect.y + 16), font)
    else:
        # Draw the high-resolution fossil sprite centered inside the view_rect!
        fossil_key = selected.get("key")
        if fossil_key and fossil_key.startswith("fossil:"):
            fossil_id = fossil_key.split(":", 1)[1]
            fossil_sprite = sprites.get_item_sprite(fossil_id, scaled=False)
            if fossil_sprite:
                orig_w, orig_h = fossil_sprite.get_size()
                scale_ratio = min(180 / orig_w, 180 / orig_h)
                scaled_w = int(orig_w * scale_ratio)
                scaled_h = int(orig_h * scale_ratio)
                scaled_sprite = pygame.transform.smoothscale(fossil_sprite, (scaled_w, scaled_h))
                
                # Center inside the view_rect, shifted slightly down
                sprite_x = view_rect.x + (view_rect.width - scaled_w) // 2
                sprite_y = view_rect.y + 60 + (view_rect.height - 80 - scaled_h) // 2
                surface.blit(scaled_sprite, (sprite_x, sprite_y))

        draw_text(surface, selected.get("title", ""), (view_rect.x + 16, view_rect.y + 42), font, config.THEME_TEXT_GOLD)
        draw_text(surface, selected.get("subtitle", ""), (desc_rect.x + 16, desc_rect.y + 16), font)
        detail = selected.get("detail", "")
        if detail:
            draw_text(surface, detail, (desc_rect.x + 16, desc_rect.y + 44), font)
        lines = selected.get("lines", [])
        for index, line in enumerate(lines[:5]):
            draw_text(surface, str(line), (desc_rect.x + 16, desc_rect.y + 72 + index * 24), font)
        found_count = selected.get("found_count")
        if found_count is not None:
            count_text = f"Found: {found_count}"
            count_surface = font.render(count_text, True, config.THEME_TEXT_GOLD)
            count_rect = count_surface.get_rect(bottomright=(desc_rect.right - 12, desc_rect.bottom - 12))
            
            # Use draw_text to draw right-aligned count text with drop shadow
            count_w = font.size(count_text)[0]
            draw_text(surface, count_text, (desc_rect.right - 12 - count_w, desc_rect.bottom - 12 - count_rect.height), font, config.THEME_TEXT_GOLD)

    return (
        back_rect,
        close_rect,
        card_rects,
        card_keys,
        prev_rect,
        next_rect,
        set_header_rect,
        indiv_header_rect,
    )


def draw_action_bar(
    surface: pygame.Surface,
    font: pygame.font.Font,
    rush_left: int,
    claim_left: int,
    survey_ready_at: int,
) -> list[tuple[pygame.Rect, str]]:
    grid_width = config.GRID_COLS * config.TILE_SIZE
    bar_top = config.GRID_TOP + (config.GRID_ROWS * config.TILE_SIZE) + config.ACTION_BAR_GAP
    box_width = (grid_width - (config.ACTION_BAR_GAP * 3)) // 4

    survey_ready = "Ready" if pygame.time.get_ticks() >= survey_ready_at else "Cooldown"
    actions = [
        (config.ACTION_SURVEY, "E", f"Survey [{survey_ready}]"),
        (config.ACTION_CAREFUL, "Space", "Careful Dig"),
        (config.ACTION_RUSH, "Shift+Space", f"Rush Dig ({rush_left})"),
        (config.ACTION_CLAIM, "Q", f"Claim Zone ({claim_left})"),
    ]

    button_rects: list[tuple[pygame.Rect, str]] = []
    for index, (action_key, hotkey, label) in enumerate(actions):
        box_x = config.GRID_LEFT + index * (box_width + config.ACTION_BAR_GAP)
        box_rect = pygame.Rect(box_x, bar_top, box_width, config.ACTION_BAR_HEIGHT)

        _draw_button(surface, box_rect, label, font, active=False)
        button_rects.append((box_rect, action_key))

    return button_rects

def _truncate_text(text: str, font: pygame.font.Font, max_width: int) -> str:
    if not text:
        return ""
    if font.size(text)[0] <= max_width:
        return text
    ellipsis = "..."
    available = max_width - font.size(ellipsis)[0]
    if available <= 0:
        return ellipsis
    trimmed = text
    while trimmed and font.size(trimmed)[0] > available:
        trimmed = trimmed[:-1]
    return f"{trimmed}{ellipsis}"


def draw_dig_complete_screen(
    surface: pygame.Surface,
    font: pygame.font.Font,
) -> None:
    """Announcement screen shown when all excavation actions are spent."""
    # Dim full-screen overlay for drama
    overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 6, 4, 160))
    surface.blit(overlay, (0, 0))

    # Central announcement panel
    panel_w, panel_h = 620, 240
    panel_x = (config.WINDOW_WIDTH - panel_w) // 2
    panel_y = (config.WINDOW_HEIGHT - panel_h) // 2 - 40
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    _panel(surface, panel_rect)

    # Gold accent top border stripe
    stripe_rect = pygame.Rect(panel_rect.x + 6, panel_rect.y + 6, panel_rect.width - 12, 6)
    pygame.draw.rect(surface, config.THEME_GOLD_ACCENT, stripe_rect)

    # Main headline
    headline = "The Dig Site Has Closed!"
    headline_w = font.size(headline)[0]
    draw_text(
        surface,
        headline,
        (panel_rect.centerx - headline_w // 2, panel_rect.y + 30),
        font,
        config.THEME_TEXT_GOLD,
    )

    # Divider line
    div_y = panel_rect.y + 74
    pygame.draw.line(
        surface,
        config.THEME_GOLD_SHADOW,
        (panel_rect.x + 30, div_y),
        (panel_rect.right - 30, div_y),
        1,
    )

    # Subtitle
    sub = "Time is up at the dig site."
    sub_w = font.size(sub)[0]
    draw_text(surface, sub, (panel_rect.centerx - sub_w // 2, panel_rect.y + 88), font)

    # Pulsing "Press Enter" prompt
    pulse = abs((pygame.time.get_ticks() % 1200) - 600) / 600
    r = int(config.THEME_TEXT_GOLD[0] * (0.6 + 0.4 * pulse))
    g = int(config.THEME_TEXT_GOLD[1] * (0.6 + 0.4 * pulse))
    b = int(config.THEME_TEXT_GOLD[2] * (0.6 + 0.4 * pulse))
    prompt = "Press Enter to head to the Laboratory"
    prompt_w = font.size(prompt)[0]
    draw_text(
        surface,
        prompt,
        (panel_rect.centerx - prompt_w // 2, panel_rect.y + 180),
        font,
        (r, g, b),
    )


def draw_lab_focus_screen(
    surface: pygame.Surface,
    font: pygame.font.Font,
    player_fossils: List[Fossil],
    ai_fossils: List[Fossil],
    player_focus: Dict[str, str],
    ai_focus: Dict[str, str],
    market_trend: str,
    focus_label: str,
    fossil_index: int,
    processed_count: int,
) -> Optional[pygame.Rect]:
    header_rect = pygame.Rect(80, 140, config.WINDOW_WIDTH - 160, 60)
    left_rect = pygame.Rect(80, 220, (config.WINDOW_WIDTH - 180) // 2, 300)
    right_rect = pygame.Rect(left_rect.right + 20, 220, (config.WINDOW_WIDTH - 180) // 2, 300)
    footer_rect = pygame.Rect(80, 540, config.WINDOW_WIDTH - 160, 120)

    for rect in [header_rect, left_rect, right_rect, footer_rect]:
        _panel(surface, rect)

    title = "Laboratory Verification"
    trend = f"Market trend tonight: {market_trend}"
    draw_text(surface, title, (header_rect.x + 16, header_rect.y + 12), font, config.THEME_TEXT_GOLD)
    draw_text(surface, trend, (header_rect.x + 16, header_rect.y + 34), font)

    draw_text(surface, "Player collection", (left_rect.x + 12, left_rect.y + 12), font, config.THEME_TEXT_GOLD)
    for index, fossil in enumerate(player_fossils[:6]):
        line_y = left_rect.y + 40 + index * 24
        line_text = f"{index + 1}. {fossil.name}"
        draw_text(surface, line_text, (left_rect.x + 12, line_y), font)
        focus_text = f"<{player_focus.get(fossil.fossil_id, config.LAB_CHOICES[0])}>"
        focus_w = font.size(focus_text)[0]
        draw_text(surface, focus_text, (left_rect.right - 12 - focus_w, line_y), font, config.THEME_TEXT_GOLD if index == fossil_index else None)

    draw_text(surface, "Mined Fossil Gallery", (right_rect.x + 12, right_rect.y + 12), font, config.THEME_TEXT_GOLD)
    if player_fossils:
        cols = 3
        slot_w = 100
        slot_h = 90
        gap_x = 16
        gap_y = 12
        
        # Center the 3x2 item slot grid inside the right panel
        start_x = right_rect.x + (right_rect.width - (cols * slot_w + (cols - 1) * gap_x)) // 2
        start_y = right_rect.y + 50
        
        for index, fossil in enumerate(player_fossils[:6]):
            col = index % cols
            row = index // cols
            cell_x = start_x + col * (slot_w + gap_x)
            cell_y = start_y + row * (slot_h + gap_y)
            cell_rect = pygame.Rect(cell_x, cell_y, slot_w, slot_h)
            
            # Style each slot cell
            is_active_item = (index == fossil_index)
            pygame.draw.rect(surface, config.THEME_STONE_DARK if is_active_item else config.THEME_BG, cell_rect)
            pygame.draw.rect(surface, config.THEME_GOLD_ACCENT if is_active_item else config.THEME_STONE_MED, cell_rect, 1)
            
            if is_active_item:
                pygame.draw.rect(surface, config.THEME_GOLD_ACCENT, cell_rect, 2)
            
            # Retrieve and center transparent high-res item sprite
            fossil_sprite = sprites.get_item_sprite(fossil.fossil_id, scaled=False)
            if fossil_sprite:
                orig_w, orig_h = fossil_sprite.get_size()
                scale = min((slot_w - 20) / orig_w, (slot_h - 20) / orig_h)
                scaled_w = int(orig_w * scale)
                scaled_h = int(orig_h * scale)
                scaled_sprite = pygame.transform.smoothscale(fossil_sprite, (scaled_w, scaled_h))
                
                px = cell_x + (slot_w - scaled_w) // 2
                py = cell_y + (slot_h - scaled_h) // 2
                surface.blit(scaled_sprite, (px, py))
                
        # Draw selected fossil name centered below the grid
        if fossil_index < len(player_fossils):
            selected_fossil = player_fossils[fossil_index]
            banner_text = f"Selected: {selected_fossil.name}"
            banner_w = font.size(banner_text)[0]
            banner_x = right_rect.x + (right_rect.width - banner_w) // 2
            draw_text(surface, banner_text, (banner_x, right_rect.bottom - 40), font, config.THEME_TEXT_GOLD)
    else:
        draw_text(surface, "No fossils mined in this match.", (right_rect.x + 16, right_rect.y + 60), font)

    draw_text(surface, f"Focus: {focus_label}", (footer_rect.x + 16, footer_rect.y + 12), font, config.THEME_TEXT_GOLD)
    draw_text(surface, "Left/Right: change focus", (footer_rect.x + 16, footer_rect.y + 38), font)
    draw_text(surface, "Up/Down: select fossil", (footer_rect.x + 16, footer_rect.y + 62), font)
    draw_text(surface, "Enter or DONE: open confirmation", (footer_rect.x + 16, footer_rect.y + 86), font)

    done_rect = None
    if player_fossils:
        done_rect = pygame.Rect(footer_rect.right - 140, footer_rect.y + 30, 120, 40)
        _draw_button(surface, done_rect, "DONE", font)

    if player_fossils:
        # Draw a beautiful warm mahogany highlighted cursor bar with gold borders and transparent fill
        cursor_y = left_rect.y + 40 + fossil_index * 24
        cursor_rect = pygame.Rect(left_rect.x + 8, cursor_y - 2, left_rect.width - 16, 22)
        pygame.draw.rect(surface, config.THEME_GOLD_ACCENT, cursor_rect, 1)
        
        # Transparent gold overlay
        s = pygame.Surface((cursor_rect.width, cursor_rect.height), pygame.SRCALPHA)
        s.fill((212, 175, 55, 30))
        surface.blit(s, cursor_rect.topleft)

        draw_text(
            surface,
            f"Processed: {processed_count}/{len(player_fossils)}",
            (left_rect.x + 12, left_rect.bottom - 30),
            font,
            config.THEME_TEXT_GOLD
        )

    return done_rect


def draw_lab_result_screen(surface: pygame.Surface, font: pygame.font.Font, lines: list[str]) -> None:
    num_lines = len(lines)
    line_spacing = 26
    top_padding = 56
    bottom_padding = 60
    
    # Dynamic panel height calculation based on lines of results
    panel_height = top_padding + num_lines * line_spacing + bottom_padding
    
    # Center vertically on the screen
    panel_y = (config.WINDOW_HEIGHT - panel_height) // 2
    
    panel_rect = pygame.Rect(120, panel_y, config.WINDOW_WIDTH - 240, panel_height)
    _panel(surface, panel_rect)
    
    draw_text(surface, "Lab Result", (panel_rect.x + 16, panel_rect.y + 16), font, config.THEME_TEXT_GOLD)
    for index, line in enumerate(lines):
        draw_text(surface, line, (panel_rect.x + 16, panel_rect.y + top_padding + index * line_spacing), font)
        
    draw_text(
        surface, 
        "Press Enter to continue to the Midnight Market.", 
        (panel_rect.x + 16, panel_rect.bottom - 40), 
        font, 
        config.THEME_TEXT_GOLD
    )


def draw_lab_confirm_screen(surface: pygame.Surface, font: pygame.font.Font, focus: str, target: str) -> None:
    panel_rect = pygame.Rect(120, 200, config.WINDOW_WIDTH - 240, 300)
    _panel(surface, panel_rect)
    draw_text(surface, "Confirm Lab Focus", (panel_rect.x + 16, panel_rect.y + 16), font, config.THEME_TEXT_GOLD)
    draw_text(surface, f"Focus: {focus}", (panel_rect.x + 16, panel_rect.y + 60), font)
    draw_text(surface, f"Target: {target}", (panel_rect.x + 16, panel_rect.y + 90), font)
    draw_text(surface, "Press Enter to apply or Backspace to return.", (panel_rect.x + 16, panel_rect.y + 140), font, config.THEME_TEXT_GOLD)


def draw_market_intro_screen(surface: pygame.Surface, font: pygame.font.Font, trend: str) -> None:
    panel_rect = pygame.Rect(120, 220, config.WINDOW_WIDTH - 240, 260)
    _panel(surface, panel_rect)
    draw_text(surface, "Midnight Market", (panel_rect.x + 16, panel_rect.y + 16), font, config.THEME_TEXT_GOLD)
    draw_text(surface, "The auctioneer opens the final valuation.", (panel_rect.x + 16, panel_rect.y + 60), font)
    draw_text(surface, "Buyer panel: Museum, Collector, Researcher", (panel_rect.x + 16, panel_rect.y + 90), font)
    draw_text(surface, f"Market trend: {trend}", (panel_rect.x + 16, panel_rect.y + 120), font, config.THEME_TEXT_GOLD)
    draw_text(surface, "Press Enter to begin the auction.", (panel_rect.x + 16, panel_rect.y + 170), font, config.THEME_TEXT_GOLD)


def draw_market_auction_screen(
    surface: pygame.Surface,
    font: pygame.font.Font,
    state,
) -> None:
    import math

    # 1. Main Theater Frame Panel
    main_panel = pygame.Rect(40, 120, config.WINDOW_WIDTH - 80, 710)
    _panel(surface, main_panel)

    # 2. Left Column: Player's Stage Plaque
    player_col = pygame.Rect(main_panel.x + 20, main_panel.y + 20, 230, 670)
    pygame.draw.rect(surface, config.THEME_STONE_DARK, player_col)
    pygame.draw.rect(surface, config.THEME_STONE_MED, player_col, 2)
    
    label_w = font.size("PLAYER")[0]
    draw_text(surface, "PLAYER", (player_col.centerx - label_w // 2, player_col.y + 20), font, config.THEME_TEXT_GOLD)
    
    # Player emotion portrait inside framed badge
    avatar_rect = pygame.Rect(player_col.centerx - 55, player_col.y + 130, 110, 100)
    pygame.draw.rect(surface, config.THEME_BG, avatar_rect)
    pygame.draw.rect(surface, config.THEME_WOOD_DARK, avatar_rect, 2)
    border_color_p = config.THEME_GOLD_ACCENT if state.player_emotion in {"Elated", "Anxious"} else config.THEME_STONE_LIGHT
    pygame.draw.rect(surface, border_color_p, avatar_rect.inflate(-4, -4), 1)
    
    player_face = sprites.get_face_sprite("player", state.player_emotion)
    if player_face:
        orig_w, orig_h = player_face.get_size()
        scale = min(96 / orig_w, 90 / orig_h)
        scaled_w = int(orig_w * scale)
        scaled_h = int(orig_h * scale)
        scaled_face = pygame.transform.smoothscale(player_face, (scaled_w, scaled_h))
        fx = avatar_rect.x + (avatar_rect.width - scaled_w) // 2
        fy = avatar_rect.y + (avatar_rect.height - scaled_h) // 2
        surface.blit(scaled_face, (fx, fy))
    
    # Player Score Plaque
    score_plaque = pygame.Rect(player_col.x + 15, player_col.bottom - 90, player_col.width - 30, 70)
    pygame.draw.rect(surface, config.THEME_WOOD_MED, score_plaque)
    pygame.draw.rect(surface, config.THEME_WOOD_LIGHT, score_plaque, 2)
    score_label = "PLAYER SCORE"
    sl_w = font.size(score_label)[0]
    draw_text(surface, score_label, (score_plaque.centerx - sl_w // 2, score_plaque.y + 10), font, config.THEME_TEXT_CREAM)
    score_val = str(state.player_score)
    sv_w = font.size(score_val)[0]
    draw_text(surface, score_val, (score_plaque.centerx - sv_w // 2, score_plaque.y + 35), font, config.THEME_TEXT_GOLD)

    # 3. Right Column: Rival's Stage Plaque
    rival_col = pygame.Rect(main_panel.right - 250, main_panel.y + 20, 230, 670)
    pygame.draw.rect(surface, config.THEME_STONE_DARK, rival_col)
    pygame.draw.rect(surface, config.THEME_STONE_MED, rival_col, 2)
    
    label_w_r = font.size("RIVAL AI")[0]
    draw_text(surface, "RIVAL AI", (rival_col.centerx - label_w_r // 2, rival_col.y + 20), font, config.THEME_TEXT_GOLD)
    
    # Rival emotion portrait inside framed badge
    avatar_rect_r = pygame.Rect(rival_col.centerx - 55, rival_col.y + 130, 110, 100)
    pygame.draw.rect(surface, config.THEME_BG, avatar_rect_r)
    pygame.draw.rect(surface, config.THEME_WOOD_DARK, avatar_rect_r, 2)
    border_color_ai = config.THEME_GOLD_ACCENT if state.ai_emotion in {"Elated", "Anxious"} else config.THEME_STONE_LIGHT
    pygame.draw.rect(surface, border_color_ai, avatar_rect_r.inflate(-4, -4), 1)
    
    rival_face = sprites.get_face_sprite("rival", state.ai_emotion)
    if rival_face:
        orig_w, orig_h = rival_face.get_size()
        scale = min(96 / orig_w, 90 / orig_h)
        scaled_w = int(orig_w * scale)
        scaled_h = int(orig_h * scale)
        scaled_face = pygame.transform.smoothscale(rival_face, (scaled_w, scaled_h))
        fx = avatar_rect_r.x + (avatar_rect_r.width - scaled_w) // 2
        fy = avatar_rect_r.y + (avatar_rect_r.height - scaled_h) // 2
        surface.blit(scaled_face, (fx, fy))
    
    # Rival Score Plaque
    score_plaque_r = pygame.Rect(rival_col.x + 15, rival_col.bottom - 90, rival_col.width - 30, 70)
    pygame.draw.rect(surface, config.THEME_WOOD_MED, score_plaque_r)
    pygame.draw.rect(surface, config.THEME_WOOD_LIGHT, score_plaque_r, 2)
    score_label_r = "RIVAL AI SCORE"
    sl_w_r = font.size(score_label_r)[0]
    draw_text(surface, score_label_r, (score_plaque_r.centerx - sl_w_r // 2, score_plaque_r.y + 10), font, config.THEME_TEXT_CREAM)
    score_val_r = str(state.ai_score)
    sv_w_r = font.size(score_val_r)[0]
    draw_text(surface, score_val_r, (score_plaque_r.centerx - sv_w_r // 2, score_plaque_r.y + 35), font, config.THEME_TEXT_GOLD)

    # 4. Center Stage (Bidding Platform)
    center_stage = pygame.Rect(player_col.right + 15, main_panel.y + 20, main_panel.width - 500, 670)
    pygame.draw.rect(surface, (20, 18, 16), center_stage)
    pygame.draw.rect(surface, config.THEME_WOOD_LIGHT, center_stage, 2)
    
    # Center Stage Top: Auctioneer Header and Character
    al_w = font.size("AUCTIONEER")[0]
    draw_text(surface, "AUCTIONEER", (center_stage.centerx - al_w // 2, center_stage.y + 15), font, config.THEME_TEXT_GOLD)
    
    auc_badge = pygame.Rect(center_stage.centerx - 45, center_stage.y + 40, 90, 76)
    pygame.draw.rect(surface, config.THEME_BG, auc_badge)
    pygame.draw.rect(surface, config.THEME_GOLD_ACCENT, auc_badge, 2)
    
    is_revealing = state.market_event_index > 0 and state.market_event_index < len(state.market_events)
    auc_face_emotion = "Elated" if is_revealing else "Focused"
    auc_face = sprites.get_face_sprite("auctioneer", auc_face_emotion)
    if auc_face:
        orig_w, orig_h = auc_face.get_size()
        scale = min(74 / orig_w, 68 / orig_h)
        scaled_w = int(orig_w * scale)
        scaled_h = int(orig_h * scale)
        scaled_auc_face = pygame.transform.smoothscale(auc_face, (scaled_w, scaled_h))
        fx = auc_badge.x + (auc_badge.width - scaled_w) // 2
        fy = auc_badge.y + (auc_badge.height - scaled_h) // 2
        surface.blit(scaled_auc_face, (fx, fy))

    # Center Stage Middle: Current fossil showcase
    showcase_rect = pygame.Rect(center_stage.centerx - 90, center_stage.y + 190, 180, 120)
    current_fossil = None
    event_text = state.market_current_event
    for fossil in state.fossils.values():
        if fossil.name in event_text:
            current_fossil = fossil
            break

    if current_fossil:
        fossil_sprite = sprites.get_item_sprite(current_fossil.fossil_id, scaled=False)
        if fossil_sprite:
            orig_w, orig_h = fossil_sprite.get_size()
            scale_ratio = min(110 / orig_w, 110 / orig_h)
            scaled_w = int(orig_w * scale_ratio)
            scaled_h = int(orig_h * scale_ratio)
            scaled_sprite = pygame.transform.smoothscale(fossil_sprite, (scaled_w, scaled_h))
            bobbing = int(4 * math.sin(pygame.time.get_ticks() / 150))
            fs_x = showcase_rect.centerx - scaled_w // 2
            fs_y = showcase_rect.centery - scaled_h // 2 + bobbing
            surface.blit(scaled_sprite, (fs_x, fs_y))

    # Center Stage Lower-Middle: Active Market Trend Ribbon
    trend_rect = pygame.Rect(center_stage.x + 30, center_stage.y + 345, center_stage.width - 60, 42)
    trend_colors = {
        "Museum Night": (40, 50, 80),
        "Collector Craze": (95, 75, 40),
        "Research Grant": (35, 75, 55),
        "Fraud Panic": (85, 35, 35)
    }
    t_color = trend_colors.get(state.market_trend, (60, 60, 70))
    pygame.draw.rect(surface, t_color, trend_rect)
    pygame.draw.rect(surface, config.THEME_GOLD_ACCENT, trend_rect, 1)
    
    trend_label = f"Market Trend: {state.market_trend}"
    tl_w = font.size(trend_label)[0]
    draw_text(surface, trend_label, (trend_rect.centerx - tl_w // 2, trend_rect.y + 11), font, config.THEME_TEXT_GOLD)

    # Center Stage Bottom: Narrator plaque with Word Wrap
    narration_box = pygame.Rect(center_stage.x + 15, center_stage.y + 405, center_stage.width - 30, 210)
    pygame.draw.rect(surface, config.THEME_BG, narration_box)
    pygame.draw.rect(surface, config.THEME_STONE_LIGHT, narration_box, 1)
    
    words = state.market_current_event.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = (current_line + " " + word).strip()
        if font.size(test_line)[0] < narration_box.width - 24:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
        
    start_y = narration_box.y + 25 + (narration_box.height - 50 - len(lines) * 28) // 2
    for idx, line in enumerate(lines):
        line_w = font.size(line)[0]
        draw_text(surface, line, (narration_box.centerx - line_w // 2, start_y + idx * 28), font, config.THEME_TEXT_CREAM)

    # 5. Interactive Pulse Gilded Advance Button (Bottom Center)
    advance_rect = pygame.Rect(config.WINDOW_WIDTH // 2 - 170, main_panel.bottom + 25, 340, 52)
    
    pulse = int(127 + 127 * math.sin(pygame.time.get_ticks() / 200))
    glow_color = (pulse * 235 // 255, pulse * 195 // 255, pulse * 80 // 255)
    
    _panel(surface, advance_rect)
    pygame.draw.rect(surface, glow_color, advance_rect, 2)
    
    advance_label = "Press Enter to advance."
    al_w = font.size(advance_label)[0]
    draw_text(surface, advance_label, (advance_rect.centerx - al_w // 2, advance_rect.y + 14), font, config.THEME_TEXT_GOLD)


def draw_market_final_screen(surface: pygame.Surface, font: pygame.font.Font, lines: list[str]) -> list[pygame.Rect]:
    panel_rect = pygame.Rect(120, 200, config.WINDOW_WIDTH - 240, 380)
    _panel(surface, panel_rect)
    draw_text(surface, "Final Valuation", (panel_rect.x + 16, panel_rect.y + 16), font, config.THEME_TEXT_GOLD)
    for index, line in enumerate(lines[:10]):
        draw_text(surface, line, (panel_rect.x + 16, panel_rect.y + 56 + index * 26), font)
    labels = ["Update Field Journal", "Retry", "Main Menu"]
    rects = _button_rects(labels, start_y=panel_rect.y + 320)
    for rect, label in zip(rects, labels):
        _draw_button(surface, rect, label, font)
    return rects


def draw_pause_menu(surface: pygame.Surface, title_font: pygame.font.Font, label_font: pygame.font.Font) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    # Darken the screen
    overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    panel_w = 400
    panel_h = 300
    panel_rect = pygame.Rect(
        (config.WINDOW_WIDTH - panel_w) // 2,
        (config.WINDOW_HEIGHT - panel_h) // 2,
        panel_w,
        panel_h
    )
    _panel(surface, panel_rect)

    title_w = title_font.size("Paused")[0]
    draw_text(surface, "Paused", (panel_rect.centerx - title_w // 2, panel_rect.y + 30), title_font, config.THEME_TEXT_GOLD)

    resume_rect = pygame.Rect(panel_rect.centerx - config.BUTTON_WIDTH // 2, panel_rect.y + 100, config.BUTTON_WIDTH, config.BUTTON_HEIGHT)
    retry_rect = pygame.Rect(panel_rect.centerx - config.BUTTON_WIDTH // 2, panel_rect.y + 160, config.BUTTON_WIDTH, config.BUTTON_HEIGHT)
    quit_rect = pygame.Rect(panel_rect.centerx - config.BUTTON_WIDTH // 2, panel_rect.y + 220, config.BUTTON_WIDTH, config.BUTTON_HEIGHT)

    _draw_button(surface, resume_rect, "Resume (ESC)", label_font)
    _draw_button(surface, retry_rect, "Retry Match", label_font)
    _draw_button(surface, quit_rect, "Quit to Menu", label_font)

    return resume_rect, retry_rect, quit_rect

