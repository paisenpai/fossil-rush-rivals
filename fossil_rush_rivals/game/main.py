import sys

import pygame

from . import config
from .ai_runtime import choose_action, load_runtime_models
from .excavation import advance_claims, apply_action, can_target_tile
from .game_state import create_game_state
from .laboratory import (
    apply_lab_focus,
    choose_ai_focus_for_fossil,
    list_owned_fossils,
)
from .market import MARKET_TRENDS, build_market_events, update_emotions
from .journal import build_journal_view, get_entry_details, load_journal, save_journal, update_from_match
from .renderer import (
    draw_action_bar,
    draw_dig_complete_screen,
    draw_grid,
    draw_header,
    draw_lab_confirm_screen,
    draw_lab_focus_screen,
    draw_lab_result_screen,
    draw_market_auction_screen,
    draw_market_final_screen,
    draw_market_intro_screen,
    draw_journal_screen,
    draw_narration,
    draw_excavation_hud,
    draw_characters,
    draw_title_screen,
    draw_pause_menu,
)
from .ui import build_fonts
from . import sprites


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption(config.TITLE_TEXT)
    clock = pygame.time.Clock()
    title_font, label_font = build_fonts()

    # Load and cache all transparent sprites at startup
    sprites.load_sprites()

    load_runtime_models()

    state = create_game_state()
    running = True
    title_buttons = []
    final_buttons = []
    journal_buttons = []
    journal_close_button = None
    journal_card_rects: list[pygame.Rect] = []
    journal_card_keys: list[str] = []
    journal_prev_button = None
    journal_next_button = None
    journal_set_toggle = None
    journal_individual_toggle = None
    lab_done_button = None
    action_bar_buttons: list[tuple[pygame.Rect, str]] = []
    pause_resume_btn = None
    pause_retry_btn = None
    pause_quit_btn = None

    def _direction_from_delta(dx: int, dy: int) -> str:
        mapping = {
            (0, -1): "n",
            (1, -1): "ne",
            (1, 0): "e",
            (1, 1): "se",
            (0, 1): "s",
            (-1, 1): "sw",
            (-1, 0): "w",
            (-1, -1): "nw",
        }
        return mapping.get((dx, dy), "s")

    def _can_move_to(actor: str, col: int, row: int) -> bool:
        tile = state.grid.get_tile(col, row)
        if not tile:
            return False
        if tile.obstacle:
            return False
        if tile.claimed_by is not None and tile.claimed_by != actor and tile.claim_ms_left > 0:
            return False
        return True

    while running:
        delta_ms = clock.tick(config.FPS)
        
        if state.is_paused:
            state.excavation_start_ticks += delta_ms
            state.player_move_cooldown_until += delta_ms
            state.ai_move_cooldown_until += delta_ms
            state.player_action_cooldown_until += delta_ms
            state.ai_action_cooldown_until += delta_ms
            state.player_survey_ready_at += delta_ms
            state.ai_survey_ready_at += delta_ms
            state.ai_next_think_at += delta_ms

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state.phase in {config.PHASE_EXCAVATION, config.PHASE_DIG_COMPLETE}:
                    state.is_paused = not state.is_paused
            elif event.type == pygame.MOUSEMOTION:
                if state.is_paused:
                    continue
                if state.phase == config.PHASE_EXCAVATION:
                    tile = state.grid.tile_at_pixel(event.pos)
                    state.hover_tile = tile
                    if tile:
                        state.narration = f"Hovering tile {tile.x + 1}, {tile.y + 1}."
                    else:
                        state.narration = config.NARRATION_TEXT
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state.is_paused:
                    if pause_resume_btn and pause_resume_btn.collidepoint(event.pos):
                        state.is_paused = False
                    elif pause_retry_btn and pause_retry_btn.collidepoint(event.pos):
                        state = create_game_state(start_in_title=False)
                    elif pause_quit_btn and pause_quit_btn.collidepoint(event.pos):
                        state = create_game_state(start_in_title=True)
                    continue
                if state.phase == config.PHASE_TITLE and title_buttons:
                    if title_buttons[0].collidepoint(event.pos):
                        state = create_game_state(start_in_title=False)
                    elif title_buttons[1].collidepoint(event.pos):
                        state.journal_data = load_journal()
                        state.journal_selected_key = None
                        state.journal_page = 0
                        state.journal_view = "root"
                        state.journal_show_sets = True
                        state.journal_show_individuals = True
                        state.phase = config.PHASE_JOURNAL
                        cards, _ = build_journal_view(
                            state.journal_data,
                            state.journal_view,
                            state.journal_show_sets,
                            state.journal_show_individuals,
                        )
                        if cards:
                            state.journal_selected_key = cards[0]["key"]
                    elif title_buttons[2].collidepoint(event.pos):
                        running = False
                elif state.phase == config.PHASE_JOURNAL:
                    if journal_buttons and journal_buttons[0].collidepoint(event.pos):
                        state.phase = config.PHASE_TITLE
                    elif journal_close_button and journal_close_button.collidepoint(event.pos):
                        if state.journal_view.startswith("set:"):
                            state.journal_view = "root"
                            state.journal_page = 0
                            state.journal_selected_key = None
                        else:
                            state.journal_selected_key = None
                    elif journal_set_toggle and journal_set_toggle.collidepoint(event.pos):
                        state.journal_show_sets = not state.journal_show_sets
                        state.journal_page = 0
                    elif journal_individual_toggle and journal_individual_toggle.collidepoint(event.pos):
                        state.journal_show_individuals = not state.journal_show_individuals
                        state.journal_page = 0
                    elif journal_prev_button and journal_prev_button.collidepoint(event.pos):
                        state.journal_page = max(0, state.journal_page - 1)
                    elif journal_next_button and journal_next_button.collidepoint(event.pos):
                        state.journal_page += 1
                    else:
                        for rect, key in zip(journal_card_rects, journal_card_keys):
                            if rect.collidepoint(event.pos):
                                if key.startswith("set:"):
                                    state.journal_view = key
                                    state.journal_selected_key = None
                                    state.journal_page = 0
                                else:
                                    state.journal_selected_key = key
                                break
                elif state.phase == config.PHASE_MARKET and state.market_substate == config.MARKET_SUB_FINAL:
                    if final_buttons:
                        if final_buttons[0].collidepoint(event.pos):
                            state.journal_data = update_from_match(
                                state.journal_data,
                                state.fossils,
                                state.player_score,
                                state.market_trend,
                            )
                            save_journal(state.journal_data)
                            state.journal_selected_key = None
                            state.journal_page = 0
                            state.journal_view = "root"
                            state.journal_show_sets = True
                            state.journal_show_individuals = True
                            state.phase = config.PHASE_JOURNAL
                            cards, _ = build_journal_view(
                                state.journal_data,
                                state.journal_view,
                                state.journal_show_sets,
                                state.journal_show_individuals,
                            )
                            if cards:
                                state.journal_selected_key = cards[0]["key"]
                        elif final_buttons[1].collidepoint(event.pos):
                            state = create_game_state(start_in_title=False)
                        elif final_buttons[2].collidepoint(event.pos):
                            state = create_game_state(start_in_title=True)
                elif state.phase == config.PHASE_LAB and state.lab_substate == config.LAB_SUB_CHOOSE_FOCUS:
                    if lab_done_button and lab_done_button.collidepoint(event.pos):
                        state.lab_substate = config.LAB_SUB_CONFIRM
            elif event.type == pygame.KEYDOWN:
                if state.is_paused:
                    continue
                if state.phase == config.PHASE_EXCAVATION:
                    now = pygame.time.get_ticks()
                    action_key = None
                    if event.key == pygame.K_SPACE:
                        if event.mod & pygame.KMOD_SHIFT:
                            action_key = config.ACTION_RUSH
                        else:
                            action_key = config.ACTION_CAREFUL
                    elif event.key == pygame.K_e:
                        action_key = config.ACTION_SURVEY
                    elif event.key == pygame.K_q:
                        action_key = config.ACTION_CLAIM

                    if action_key:
                        if now < state.player_action_cooldown_until:
                            state.narration = "You are still recovering from your last action."
                            continue
                        if action_key == config.ACTION_SURVEY and now < state.player_survey_ready_at:
                            state.narration = "Survey is recharging."
                            continue
                        if action_key == config.ACTION_RUSH and state.player_rush_left <= 0:
                            state.narration = "No rush digs left for the player."
                            continue
                        if action_key == config.ACTION_CLAIM and state.player_claim_left <= 0:
                            state.narration = "No claim zones left for the player."
                            continue

                        tile = state.grid.get_tile(*state.player_pos)
                        if tile and can_target_tile(
                            tile,
                            action_key,
                            "player",
                            state.grid,
                            state.fossils,
                        ):
                            state.narration = apply_action(
                                action_key,
                                state.grid,
                                tile,
                                "player",
                                state.rng,
                                state.fossils,
                                now,
                            )
                            state.player_last_action = action_key
                            state.player_last_action_ticks = now
                            state.player_action_cooldown_until = now + config.ACTION_COOLDOWNS_MS[action_key]
                            if action_key == config.ACTION_RUSH:
                                state.player_rush_left -= 1
                            elif action_key == config.ACTION_CLAIM:
                                state.player_claim_left -= 1
                            elif action_key == config.ACTION_SURVEY:
                                state.player_survey_ready_at = now + config.SURVEY_COOLDOWN_MS
                        else:
                            state.narration = "That tile is not a valid target."
                elif state.phase == config.PHASE_DIG_COMPLETE:
                    if event.key == pygame.K_RETURN:
                        # Now set up the lab phase
                        state.phase = config.PHASE_LAB
                        state.bg_key = "lab_afternoon"
                        state.narration = "Choose a Lab Focus."
                        if not state.market_trend:
                            state.market_trend = state.rng.choice(MARKET_TRENDS)
                        state.lab_substate = config.LAB_SUB_CHOOSE_FOCUS
                        state.lab_processed_player = []
                        state.lab_selected_fossil_index = 0
                        state.lab_ai_results = []
                        state.lab_focus_player = {}
                        state.lab_focus_ai = {}
                        player_fossils = list_owned_fossils(state.fossils, "player")
                        for fossil in player_fossils:
                            state.lab_focus_player[fossil.fossil_id] = config.LAB_CHOICES[0]
                        ai_fossils = list_owned_fossils(state.fossils, "ai")
                        for fossil in ai_fossils:
                            focus = choose_ai_focus_for_fossil(fossil, state.rng, state.market_trend)
                            state.lab_focus_ai[fossil.fossil_id] = focus
                            if config.AI_DEBUG_LOG:
                                print(f"Debug: Rival lab choice {focus} for {fossil.name}.")
                elif state.phase == config.PHASE_LAB:
                    if state.lab_substate == config.LAB_SUB_CHOOSE_FOCUS:
                        player_fossils = list_owned_fossils(state.fossils, "player")
                        available_indices = [
                            index
                            for index, fossil in enumerate(player_fossils)
                            if fossil.fossil_id not in state.lab_processed_player
                        ]
                        if available_indices:
                            state.lab_selected_fossil_index = min(
                                max(state.lab_selected_fossil_index, available_indices[0]),
                                available_indices[-1],
                            )
                        if event.key in {pygame.K_LEFT, pygame.K_RIGHT} and player_fossils:
                            target_fossil = player_fossils[state.lab_selected_fossil_index]
                            current_focus = state.lab_focus_player.get(
                                target_fossil.fossil_id,
                                config.LAB_CHOICES[0],
                            )
                            current_index = config.LAB_CHOICES.index(current_focus)
                            direction = -1 if event.key == pygame.K_LEFT else 1
                            next_index = (current_index + direction) % len(config.LAB_CHOICES)
                            state.lab_focus_player[target_fossil.fossil_id] = config.LAB_CHOICES[next_index]
                        elif event.key == pygame.K_UP and player_fossils:
                            if available_indices:
                                prev_indices = [idx for idx in available_indices if idx < state.lab_selected_fossil_index]
                                state.lab_selected_fossil_index = prev_indices[-1] if prev_indices else available_indices[0]
                                target_fossil = player_fossils[state.lab_selected_fossil_index]
                                state.lab_focus_player.setdefault(target_fossil.fossil_id, config.LAB_CHOICES[0])
                        elif event.key == pygame.K_DOWN and player_fossils:
                            if available_indices:
                                next_indices = [idx for idx in available_indices if idx > state.lab_selected_fossil_index]
                                state.lab_selected_fossil_index = next_indices[0] if next_indices else available_indices[-1]
                                target_fossil = player_fossils[state.lab_selected_fossil_index]
                                state.lab_focus_player.setdefault(target_fossil.fossil_id, config.LAB_CHOICES[0])
                        elif event.key == pygame.K_RETURN:
                            if player_fossils:
                                state.lab_substate = config.LAB_SUB_CONFIRM
                            else:
                                state.lab_result_lines = ["No fossils to process."]
                                state.lab_ai_results = []
                                ai_fossils = list_owned_fossils(state.fossils, "ai")
                                for fossil in ai_fossils:
                                    focus = state.lab_focus_ai.get(fossil.fossil_id, config.LAB_CHOICES[0])
                                    state.lab_ai_results.append(apply_lab_focus(fossil, focus, state.rng))
                                state.lab_substate = config.LAB_SUB_RESULT
                    elif state.lab_substate == config.LAB_SUB_CONFIRM:
                        if event.key == pygame.K_RETURN:
                            result_lines = []
                            player_fossils = list_owned_fossils(state.fossils, "player")
                            if not player_fossils:
                                result_lines.append("No fossils to process.")
                            else:
                                for fossil in player_fossils:
                                    if fossil.fossil_id in state.lab_processed_player:
                                        continue
                                    focus = state.lab_focus_player.get(fossil.fossil_id, config.LAB_CHOICES[0])
                                    result_lines.append(apply_lab_focus(fossil, focus, state.rng))
                                    state.lab_processed_player.append(fossil.fossil_id)
                            state.lab_result_lines = result_lines

                            state.lab_ai_results = []
                            ai_fossils = list_owned_fossils(state.fossils, "ai")
                            for fossil in ai_fossils:
                                focus = state.lab_focus_ai.get(fossil.fossil_id, config.LAB_CHOICES[0])
                                ai_line = apply_lab_focus(fossil, focus, state.rng)
                                if config.AI_DEBUG_LOG:
                                    state.lab_ai_results.append(ai_line)

                            state.lab_substate = config.LAB_SUB_RESULT
                        elif event.key == pygame.K_BACKSPACE:
                            state.lab_substate = config.LAB_SUB_CHOOSE_FOCUS
                    elif state.lab_substate == config.LAB_SUB_RESULT:
                        if event.key == pygame.K_RETURN:
                            state.phase = config.PHASE_MARKET
                            state.bg_key = "auction_night"
                            state.market_substate = config.MARKET_SUB_INTRO
                elif state.phase == config.PHASE_MARKET:
                    if state.market_substate == config.MARKET_SUB_INTRO:
                        if event.key == pygame.K_RETURN:
                            state.market_events = build_market_events(state.fossils, state.market_trend)
                            state.market_event_index = 0
                            state.player_score = 0
                            state.ai_score = 0
                            state.market_substate = config.MARKET_SUB_REVEAL
                            if state.market_events:
                                event_data = state.market_events[0]
                                state.market_current_event = event_data["text"]
                    elif state.market_substate == config.MARKET_SUB_REVEAL:
                        if event.key == pygame.K_RETURN:
                            if state.market_event_index < len(state.market_events):
                                event_data = state.market_events[state.market_event_index]
                                state.player_score += event_data["player"]
                                state.ai_score += event_data["ai"]
                                state.market_current_event = event_data["text"]
                                state.player_emotion, state.ai_emotion = update_emotions(
                                    state.player_score, state.ai_score
                                )
                                state.market_event_index += 1
                            if state.market_event_index >= len(state.market_events):
                                winner = "Player" if state.player_score >= state.ai_score else "Rival AI"
                                state.market_final_lines = [
                                    f"Player score: {state.player_score}",
                                    f"Rival score: {state.ai_score}",
                                    f"Winner: {winner}",
                                ]
                                state.market_substate = config.MARKET_SUB_FINAL
                    elif state.market_substate == config.MARKET_SUB_FINAL:
                        if event.key == pygame.K_RETURN:
                            state = create_game_state(start_in_title=True)

        if state.phase == config.PHASE_EXCAVATION and not state.is_paused:
            now = pygame.time.get_ticks()
            if state.excavation_start_ticks == 0:
                state.excavation_start_ticks = now
                state.excavation_end_ticks = now + config.EXCAVATION_DURATION_MS
                state.excavation_time_left_ms = config.EXCAVATION_DURATION_MS

            pressed = pygame.key.get_pressed()
            dx = int(pressed[pygame.K_RIGHT] or pressed[pygame.K_d]) - int(pressed[pygame.K_LEFT] or pressed[pygame.K_a])
            dy = int(pressed[pygame.K_DOWN] or pressed[pygame.K_s]) - int(pressed[pygame.K_UP] or pressed[pygame.K_w])
            dx = max(-1, min(1, dx))
            dy = max(-1, min(1, dy))
            if (dx != 0 or dy != 0) and now >= state.player_move_cooldown_until:
                target_col = state.player_pos[0] + dx
                target_row = state.player_pos[1] + dy
                if _can_move_to("player", target_col, target_row):
                    state.player_pos = (target_col, target_row)
                    state.player_facing = _direction_from_delta(dx, dy)
                    state.player_last_move_ticks = now
                    state.player_move_cooldown_until = now + config.MOVE_COOLDOWN_MS
                else:
                    state.narration = "You cannot move there."

            state.excavation_time_left_ms = max(0, state.excavation_end_ticks - now)
            advance_claims(state.grid, delta_ms)

            if now >= state.ai_next_think_at:
                move_window = config.AI_THINK_INTERVAL_RANGE_MS
                state.ai_next_think_at = now + state.rng.randint(move_window[0], move_window[1])
                choice = choose_action(
                    state.grid,
                    "ai",
                    state.rng,
                    fossils=state.fossils,
                    rush_left=state.ai_rush_left,
                    claim_left=state.ai_claim_left,
                    time_left_ms=state.excavation_time_left_ms,
                    actor_pos=state.ai_pos,
                    actor_facing=state.ai_facing,
                    actor_is_moving=(now - state.ai_last_move_ticks) < config.MOVE_COOLDOWN_MS,
                    player_pos=state.player_pos,
                )
                if choice:
                    state.ai_target_action = choice.action
                    state.ai_target_pos = (choice.tile.x, choice.tile.y)
                    state.ai_status = f"Targeting {config.ACTION_LABELS[choice.action]}"
                else:
                    state.ai_target_action = None
                    state.ai_target_pos = None
                    state.ai_status = "Searching"

            if state.ai_target_pos:
                ax, ay = state.ai_pos
                tx, ty = state.ai_target_pos
                if (ax, ay) != (tx, ty) and now >= state.ai_move_cooldown_until:
                    def _bfs_next_step(start_x, start_y, goal_x, goal_y):
                        queue = [(start_x, start_y)]
                        came_from = {(start_x, start_y): None}
                        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
                        while queue:
                            cx, cy = queue.pop(0)
                            if (cx, cy) == (goal_x, goal_y):
                                curr = (cx, cy)
                                while came_from[curr] != (start_x, start_y):
                                    curr = came_from[curr]
                                return curr
                            for dx, dy in offsets:
                                nx, ny = cx + dx, cy + dy
                                if (nx, ny) not in came_from and _can_move_to("ai", nx, ny):
                                    came_from[(nx, ny)] = (cx, cy)
                                    queue.append((nx, ny))
                        return start_x, start_y
                    
                    next_x, next_y = _bfs_next_step(ax, ay, tx, ty)

                    if (next_x, next_y) != (ax, ay):
                        state.ai_pos = (next_x, next_y)
                        state.ai_facing = _direction_from_delta(next_x - ax, next_y - ay)
                        state.ai_last_move_ticks = now
                        state.ai_move_cooldown_until = now + config.MOVE_COOLDOWN_MS
                    else:
                        state.ai_target_pos = None
                        state.ai_target_action = None
                elif (ax, ay) == (tx, ty) and state.ai_target_action:
                    action_key = state.ai_target_action
                    if now >= state.ai_action_cooldown_until:
                        if action_key == config.ACTION_SURVEY and now < state.ai_survey_ready_at:
                            state.ai_target_action = None
                            state.ai_target_pos = None
                        elif action_key == config.ACTION_RUSH and state.ai_rush_left <= 0:
                            state.ai_target_action = None
                            state.ai_target_pos = None
                        elif action_key == config.ACTION_CLAIM and state.ai_claim_left <= 0:
                            state.ai_target_action = None
                            state.ai_target_pos = None
                        else:
                            tile = state.grid.get_tile(ax, ay)
                            if tile and can_target_tile(tile, action_key, "ai", state.grid, state.fossils):
                                state.narration = apply_action(
                                    action_key,
                                    state.grid,
                                    tile,
                                    "ai",
                                    state.rng,
                                    state.fossils,
                                    now,
                                )
                                state.ai_last_action = action_key
                                state.ai_last_action_ticks = now
                                state.ai_action_cooldown_until = now + config.ACTION_COOLDOWNS_MS[action_key]
                                if action_key == config.ACTION_RUSH:
                                    state.ai_rush_left -= 1
                                elif action_key == config.ACTION_CLAIM:
                                    state.ai_claim_left -= 1
                                elif action_key == config.ACTION_SURVEY:
                                    state.ai_survey_ready_at = now + config.SURVEY_COOLDOWN_MS
                                state.ai_target_action = None
                                state.ai_target_pos = None
                            else:
                                state.ai_target_action = None
                                state.ai_target_pos = None

            if state.excavation_time_left_ms <= 0:
                state.phase = config.PHASE_DIG_COMPLETE
                state.narration = "The dig site has closed."

        bg_sprite = sprites.get_background_sprite(state.bg_key)
        if bg_sprite:
            screen.blit(bg_sprite, (0, 0))
        else:
            screen.fill(config.BACKGROUND_COLOR)
        if state.phase not in {config.PHASE_EXCAVATION, config.PHASE_DIG_COMPLETE}:
            draw_header(screen, title_font, label_font, state.phase)
        if state.phase == config.PHASE_TITLE:
            title_buttons = draw_title_screen(screen, title_font, label_font)
            final_buttons = []
            journal_buttons = []
        elif state.phase == config.PHASE_JOURNAL:
            cards, view_title = build_journal_view(
                state.journal_data,
                state.journal_view,
                state.journal_show_sets,
                state.journal_show_individuals,
            )
            
            per_page = config.JOURNAL_CARDS_PER_PAGE
            max_page = 0
            if cards:
                max_page = (len(cards) - 1) // per_page
            if state.journal_page > max_page:
                state.journal_page = max_page
                
            selected = get_entry_details(state.journal_data, state.journal_selected_key)
            if selected:
                selected["key"] = state.journal_selected_key
            (
                back_rect,
                close_rect,
                card_rects,
                card_keys,
                prev_rect,
                next_rect,
                set_toggle_rect,
                indiv_toggle_rect,
            ) = draw_journal_screen(
                screen,
                label_font,
                cards,
                selected,
                state.journal_page,
                view_title,
                state.journal_show_sets,
                state.journal_show_individuals,
                state.journal_view,
            )
            journal_buttons = [back_rect]
            journal_close_button = close_rect
            journal_card_rects = card_rects
            journal_card_keys = card_keys
            journal_prev_button = prev_rect
            journal_next_button = next_rect
            journal_set_toggle = set_toggle_rect
            journal_individual_toggle = indiv_toggle_rect
            title_buttons = []
            final_buttons = []
        elif state.phase in {config.PHASE_EXCAVATION, config.PHASE_DIG_COMPLETE}:
            draw_grid(screen, state.grid, label_font, state.hover_tile, state.fossils)
            draw_characters(screen, label_font, state)
            if state.phase == config.PHASE_EXCAVATION:
                draw_excavation_hud(screen, label_font, state)
            else:
                # Overlay the dig-complete announcement on top of the frozen grid
                draw_dig_complete_screen(screen, label_font)
                # Redraw the header on top of the overlay so "Dig Site Closed" remains visible
                draw_header(screen, title_font, label_font, state.phase)
            
            if state.is_paused:
                pause_resume_btn, pause_retry_btn, pause_quit_btn = draw_pause_menu(screen, title_font, label_font)
        elif state.phase == config.PHASE_LAB:
            player_fossils = list_owned_fossils(state.fossils, "player")
            ai_fossils = list_owned_fossils(state.fossils, "ai")
            if state.lab_substate == config.LAB_SUB_CHOOSE_FOCUS:
                focus_label = ""
                if player_fossils:
                    selected_fossil = player_fossils[state.lab_selected_fossil_index]
                    focus_label = state.lab_focus_player.get(selected_fossil.fossil_id, config.LAB_CHOICES[0])
                lab_done_button = draw_lab_focus_screen(
                    screen,
                    label_font,
                    player_fossils,
                    ai_fossils,
                    state.lab_focus_player,
                    state.lab_focus_ai,
                    state.market_trend,
                    focus_label,
                    state.lab_selected_fossil_index,
                    len(state.lab_processed_player),
                )
            elif state.lab_substate == config.LAB_SUB_RESULT:
                lab_done_button = None
                result_lines = state.lab_result_lines
                draw_lab_result_screen(screen, label_font, result_lines)
            elif state.lab_substate == config.LAB_SUB_CONFIRM:
                lab_done_button = None
                target_name = f"{len(player_fossils)} fossils"
                draw_lab_confirm_screen(screen, label_font, "Selected per fossil", target_name)
        elif state.phase == config.PHASE_MARKET:
            if state.market_substate == config.MARKET_SUB_INTRO:
                draw_market_intro_screen(screen, label_font, state.market_trend)
            elif state.market_substate == config.MARKET_SUB_REVEAL:
                draw_market_auction_screen(
                    screen,
                    label_font,
                    state,
                )
            elif state.market_substate == config.MARKET_SUB_FINAL:
                final_buttons = draw_market_final_screen(screen, label_font, state.market_final_lines)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
