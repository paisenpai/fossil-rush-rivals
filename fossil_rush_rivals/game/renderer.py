from typing import Optional

import pygame

from . import config
from .grid import Grid, Tile


def draw_text(surface: pygame.Surface, text: str, pos: tuple[int, int], font: pygame.font.Font) -> None:
    rendered = font.render(text, True, config.TEXT_COLOR)
    surface.blit(rendered, pos)


def draw_grid(surface: pygame.Surface, grid: Grid, font: pygame.font.Font, hover_tile: Optional[Tile]) -> None:
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
                pygame.draw.rect(surface, config.BACKGROUND_COLOR, rect)
                continue
            color = config.PANEL_COLOR
            if hover_tile and hover_tile.x == col and hover_tile.y == row:
                color = config.HOVER_COLOR
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, config.GRID_LINE_COLOR, rect, 1)
            label = tile.label()
            label_surface = font.render(label, True, config.TEXT_COLOR)
            label_rect = label_surface.get_rect(center=rect.center)
            surface.blit(label_surface, label_rect)


def draw_narration(surface: pygame.Surface, font: pygame.font.Font, narration: str) -> None:
    grid_width = config.GRID_COLS * config.TILE_SIZE
    grid_height = config.GRID_ROWS * config.TILE_SIZE
    box_top = config.GRID_TOP + grid_height + config.ACTION_BAR_HEIGHT + (config.ACTION_BAR_GAP * 2)
    box_rect = pygame.Rect(config.GRID_LEFT, box_top, grid_width, config.NARRATION_BOX_HEIGHT)
    pygame.draw.rect(surface, config.PANEL_COLOR, box_rect)
    pygame.draw.rect(surface, config.GRID_LINE_COLOR, box_rect, 1)
    draw_text(surface, narration, (box_rect.x + 12, box_rect.y + 22), font)


def draw_header(surface: pygame.Surface, title_font: pygame.font.Font, label_font: pygame.font.Font, phase_text: str) -> None:
    title_surface = title_font.render(config.TITLE_TEXT, True, config.TEXT_COLOR)
    title_rect = title_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 40))
    surface.blit(title_surface, title_rect)

    phase_surface = label_font.render(phase_text, True, config.TEXT_COLOR)
    phase_rect = phase_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 80))
    surface.blit(phase_surface, phase_rect)


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
    title_rect = pygame.Rect(80, 120, config.WINDOW_WIDTH - 160, 140)
    _panel(surface, title_rect)
    title_surface = title_font.render("Fossil Rush Rivals", True, config.TEXT_COLOR)
    title_pos = title_surface.get_rect(center=title_rect.center)
    surface.blit(title_surface, title_pos)

    labels = ["Start Match", "Field Journal", "Quit"]
    rects = _button_rects(labels, start_y=320)
    for rect, label in zip(rects, labels):
        _panel(surface, rect)
        text = font.render(label, True, config.TEXT_COLOR)
        surface.blit(text, text.get_rect(center=rect.center))
    return rects


def draw_journal_screen(surface: pygame.Surface, font: pygame.font.Font) -> list[pygame.Rect]:
    panel_rect = pygame.Rect(120, 200, config.WINDOW_WIDTH - 240, 300)
    _panel(surface, panel_rect)
    draw_text(surface, "Field Journal", (panel_rect.x + 16, panel_rect.y + 16), font)
    draw_text(surface, "Placeholder journal screen.", (panel_rect.x + 16, panel_rect.y + 56), font)

    labels = ["Back"]
    rects = _button_rects(labels, start_y=panel_rect.y + 220)
    for rect, label in zip(rects, labels):
        _panel(surface, rect)
        text = font.render(label, True, config.TEXT_COLOR)
        surface.blit(text, text.get_rect(center=rect.center))
    return rects


def draw_side_panels(
    surface: pygame.Surface,
    font: pygame.font.Font,
    player_actions_left: int,
    ai_actions_left: int,
    current_turn: str,
    selected_action_label: str,
) -> None:
    left_x = config.GRID_LEFT
    right_x = config.WINDOW_WIDTH - config.GRID_RIGHT_MARGIN
    top_y = config.GRID_TOP - 26

    player_text = f"{config.PLAYER_LABEL}  Actions: {player_actions_left}"
    ai_text = f"{config.AI_LABEL}  Actions: {ai_actions_left}"

    draw_text(surface, player_text, (left_x, top_y), font)
    ai_surface = font.render(ai_text, True, config.TEXT_COLOR)
    ai_rect = ai_surface.get_rect(topright=(right_x, top_y))
    surface.blit(ai_surface, ai_rect)

    info_y = top_y - 22
    turn_text = f"Turn: {current_turn.title()}"
    action_text = f"Action: {selected_action_label}"
    draw_text(surface, turn_text, (left_x, info_y), font)
    action_surface = font.render(action_text, True, config.TEXT_COLOR)
    action_rect = action_surface.get_rect(topright=(right_x, info_y))
    surface.blit(action_surface, action_rect)


def draw_action_bar(surface: pygame.Surface, font: pygame.font.Font, selected_action: str) -> None:
    grid_width = config.GRID_COLS * config.TILE_SIZE
    bar_top = config.GRID_TOP + (config.GRID_ROWS * config.TILE_SIZE) + config.ACTION_BAR_GAP
    box_width = (grid_width - (config.ACTION_BAR_GAP * 3)) // 4

    actions = [
        (config.ACTION_SURVEY, "1", config.ACTION_LABELS[config.ACTION_SURVEY]),
        (config.ACTION_CAREFUL, "2", config.ACTION_LABELS[config.ACTION_CAREFUL]),
        (config.ACTION_RUSH, "3", config.ACTION_LABELS[config.ACTION_RUSH]),
        (config.ACTION_CLAIM, "4", config.ACTION_LABELS[config.ACTION_CLAIM]),
    ]

    for index, (action_key, hotkey, label) in enumerate(actions):
        box_x = config.GRID_LEFT + index * (box_width + config.ACTION_BAR_GAP)
        box_rect = pygame.Rect(box_x, bar_top, box_width, config.ACTION_BAR_HEIGHT)
        color = config.HOVER_COLOR if selected_action == action_key else config.PANEL_COLOR
        pygame.draw.rect(surface, color, box_rect)
        pygame.draw.rect(surface, config.GRID_LINE_COLOR, box_rect, 1)

        text = f"{label} [{hotkey}]"
        text_surface = font.render(text, True, config.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=box_rect.center)
        surface.blit(text_surface, text_rect)


def _panel(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surface, config.PANEL_COLOR, rect)
    pygame.draw.rect(surface, config.GRID_LINE_COLOR, rect, 1)


def draw_lab_focus_screen(
    surface: pygame.Surface,
    font: pygame.font.Font,
    player_list: list[str],
    ai_list: list[str],
    market_trend: str,
    focus_label: str,
    fossil_index: int,
    processed_count: int,
) -> None:
    header_rect = pygame.Rect(80, 140, config.WINDOW_WIDTH - 160, 60)
    left_rect = pygame.Rect(80, 220, (config.WINDOW_WIDTH - 180) // 2, 300)
    right_rect = pygame.Rect(left_rect.right + 20, 220, (config.WINDOW_WIDTH - 180) // 2, 300)
    footer_rect = pygame.Rect(80, 540, config.WINDOW_WIDTH - 160, 120)

    for rect in [header_rect, left_rect, right_rect, footer_rect]:
        _panel(surface, rect)

    title = "Laboratory Verification"
    trend = f"Market trend tonight: {market_trend}"
    draw_text(surface, title, (header_rect.x + 16, header_rect.y + 12), font)
    draw_text(surface, trend, (header_rect.x + 16, header_rect.y + 34), font)

    draw_text(surface, "Player collection", (left_rect.x + 12, left_rect.y + 12), font)
    for index, line in enumerate(player_list[:6]):
        draw_text(surface, line, (left_rect.x + 12, left_rect.y + 40 + index * 24), font)

    draw_text(surface, "AI rival collection", (right_rect.x + 12, right_rect.y + 12), font)
    for index, line in enumerate(ai_list[:6]):
        draw_text(surface, line, (right_rect.x + 12, right_rect.y + 40 + index * 24), font)

    draw_text(surface, f"Focus: {focus_label}", (footer_rect.x + 16, footer_rect.y + 12), font)
    draw_text(surface, "Left/Right: change focus", (footer_rect.x + 16, footer_rect.y + 38), font)
    draw_text(surface, "Up/Down: select fossil", (footer_rect.x + 16, footer_rect.y + 62), font)
    draw_text(surface, "Enter: confirm focus", (footer_rect.x + 16, footer_rect.y + 86), font)

    if player_list:
        focus_rect = pygame.Rect(footer_rect.right - 180, footer_rect.y + 30, 150, 40)
        _panel(surface, focus_rect)
        draw_text(surface, "Confirm", (focus_rect.x + 32, focus_rect.y + 10), font)

    if player_list:
        cursor_y = left_rect.y + 40 + fossil_index * 24
        cursor_rect = pygame.Rect(left_rect.x + 8, cursor_y - 2, left_rect.width - 16, 22)
        pygame.draw.rect(surface, config.HOVER_COLOR, cursor_rect, 1)
        draw_text(
            surface,
            f"Processed: {processed_count}/{len(player_list)}",
            (left_rect.x + 12, left_rect.bottom - 30),
            font,
        )


def draw_lab_result_screen(surface: pygame.Surface, font: pygame.font.Font, lines: list[str]) -> None:
    panel_rect = pygame.Rect(120, 220, config.WINDOW_WIDTH - 240, 260)
    _panel(surface, panel_rect)
    draw_text(surface, "Lab Result", (panel_rect.x + 16, panel_rect.y + 16), font)
    for index, line in enumerate(lines[:6]):
        draw_text(surface, line, (panel_rect.x + 16, panel_rect.y + 56 + index * 26), font)
    draw_text(surface, "Press Enter to continue to the Midnight Market.", (panel_rect.x + 16, panel_rect.y + 200), font)


def draw_lab_confirm_screen(surface: pygame.Surface, font: pygame.font.Font, focus: str, target: str) -> None:
    panel_rect = pygame.Rect(120, 200, config.WINDOW_WIDTH - 240, 300)
    _panel(surface, panel_rect)
    draw_text(surface, "Confirm Lab Focus", (panel_rect.x + 16, panel_rect.y + 16), font)
    draw_text(surface, f"Focus: {focus}", (panel_rect.x + 16, panel_rect.y + 60), font)
    draw_text(surface, f"Target: {target}", (panel_rect.x + 16, panel_rect.y + 90), font)
    draw_text(surface, "Press Enter to confirm or Backspace to cancel.", (panel_rect.x + 16, panel_rect.y + 140), font)


def draw_market_intro_screen(surface: pygame.Surface, font: pygame.font.Font, trend: str) -> None:
    panel_rect = pygame.Rect(120, 220, config.WINDOW_WIDTH - 240, 260)
    _panel(surface, panel_rect)
    draw_text(surface, "Midnight Market", (panel_rect.x + 16, panel_rect.y + 16), font)
    draw_text(surface, "The auctioneer opens the final valuation.", (panel_rect.x + 16, panel_rect.y + 60), font)
    draw_text(surface, "Buyer panel: Museum, Collector, Researcher", (panel_rect.x + 16, panel_rect.y + 90), font)
    draw_text(surface, f"Market trend: {trend}", (panel_rect.x + 16, panel_rect.y + 120), font)
    draw_text(surface, "Press Enter to begin the auction.", (panel_rect.x + 16, panel_rect.y + 170), font)


def draw_market_auction_screen(
    surface: pygame.Surface,
    font: pygame.font.Font,
    player_score: int,
    ai_score: int,
    player_emotion: str,
    ai_emotion: str,
    market_trend: str,
    current_event: str,
) -> None:
    top_rect = pygame.Rect(80, 140, config.WINDOW_WIDTH - 160, 110)
    mid_rect = pygame.Rect(80, 270, config.WINDOW_WIDTH - 160, 260)
    bottom_rect = pygame.Rect(80, 550, config.WINDOW_WIDTH - 160, 110)
    narration_rect = pygame.Rect(80, 680, config.WINDOW_WIDTH - 160, 120)

    for rect in [top_rect, mid_rect, bottom_rect, narration_rect]:
        _panel(surface, rect)

    ai_text = f"{config.AI_LABEL}  Score: {ai_score}  Emotion: {ai_emotion}"
    surface.blit(font.render(ai_text, True, config.TEXT_COLOR), (top_rect.x + 16, top_rect.y + 16))

    auctioneer = "Auctioneer"
    buyer_left = "Museum"
    buyer_right = "Collector"
    buyer_bottom = "Researcher"
    trend_text = f"Market trend: {market_trend}"

    surface.blit(font.render(auctioneer, True, config.TEXT_COLOR), (mid_rect.centerx - 60, mid_rect.y + 20))
    surface.blit(font.render(buyer_left, True, config.TEXT_COLOR), (mid_rect.x + 20, mid_rect.y + 20))
    surface.blit(font.render(buyer_right, True, config.TEXT_COLOR), (mid_rect.right - 120, mid_rect.y + 20))
    surface.blit(font.render(buyer_bottom, True, config.TEXT_COLOR), (mid_rect.centerx - 60, mid_rect.y + 60))
    surface.blit(font.render(trend_text, True, config.TEXT_COLOR), (mid_rect.x + 20, mid_rect.y + 110))

    player_text = f"{config.PLAYER_LABEL}  Score: {player_score}  Emotion: {player_emotion}"
    surface.blit(font.render(player_text, True, config.TEXT_COLOR), (bottom_rect.x + 16, bottom_rect.y + 16))

    surface.blit(font.render(current_event, True, config.TEXT_COLOR), (narration_rect.x + 16, narration_rect.y + 16))
    surface.blit(
        font.render("Press Enter to advance.", True, config.TEXT_COLOR),
        (narration_rect.x + 16, narration_rect.y + 48),
    )


def draw_market_final_screen(surface: pygame.Surface, font: pygame.font.Font, lines: list[str]) -> list[pygame.Rect]:
    panel_rect = pygame.Rect(120, 200, config.WINDOW_WIDTH - 240, 380)
    _panel(surface, panel_rect)
    draw_text(surface, "Final Valuation", (panel_rect.x + 16, panel_rect.y + 16), font)
    for index, line in enumerate(lines[:10]):
        draw_text(surface, line, (panel_rect.x + 16, panel_rect.y + 56 + index * 26), font)
    labels = ["Update Field Journal", "Replay", "Title Screen"]
    rects = _button_rects(labels, start_y=panel_rect.y + 320)
    for rect, label in zip(rects, labels):
        _panel(surface, rect)
        text = font.render(label, True, config.TEXT_COLOR)
        surface.blit(text, text.get_rect(center=rect.center))
    return rects
