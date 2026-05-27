import sys

import pygame

from . import config
from .ai_runtime import choose_action
from .excavation import advance_claims, apply_action, can_target_tile, next_turn_label
from .game_state import create_game_state
from .laboratory import (
    apply_lab_focus,
    choose_ai_focus_for_fossil,
    list_owned_fossils,
)
from .market import MARKET_TRENDS, build_market_events, update_emotions
from .renderer import (
    draw_action_bar,
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
    draw_side_panels,
    draw_title_screen,
)
from .ui import build_fonts


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption(config.TITLE_TEXT)
    clock = pygame.time.Clock()
    title_font, label_font = build_fonts()

    state = create_game_state()
    running = True
    title_buttons = []
    final_buttons = []
    journal_buttons = []

    while running:
        clock.tick(config.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                if state.phase == config.PHASE_EXCAVATION and state.current_turn == "player":
                    tile = state.grid.tile_at_pixel(event.pos)
                    state.hover_tile = tile
                    if tile:
                        state.narration = f"Hovering tile {tile.x + 1}, {tile.y + 1}."
                    else:
                        state.narration = config.NARRATION_TEXT
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state.phase == config.PHASE_TITLE and title_buttons:
                    if title_buttons[0].collidepoint(event.pos):
                        state = create_game_state(start_in_title=False)
                    elif title_buttons[1].collidepoint(event.pos):
                        state.phase = config.PHASE_JOURNAL
                    elif title_buttons[2].collidepoint(event.pos):
                        running = False
                elif state.phase == config.PHASE_JOURNAL and journal_buttons:
                    if journal_buttons[0].collidepoint(event.pos):
                        state.phase = config.PHASE_TITLE
                elif state.phase == config.PHASE_MARKET and state.market_substate == config.MARKET_SUB_FINAL:
                    if final_buttons:
                        if final_buttons[0].collidepoint(event.pos):
                            state = create_game_state(start_in_title=True)
                        elif final_buttons[1].collidepoint(event.pos):
                            state = create_game_state(start_in_title=False)
                        elif final_buttons[2].collidepoint(event.pos):
                            state = create_game_state(start_in_title=True)
                elif state.phase == config.PHASE_EXCAVATION and state.current_turn == "player":
                    if state.player_actions_left <= 0:
                        state.narration = "No actions left for the player."
                    else:
                        tile = state.grid.tile_at_pixel(event.pos)
                        if tile and can_target_tile(tile, state.selected_action, "player", state.grid):
                            state.narration = apply_action(
                                state.selected_action,
                                state.grid,
                                tile,
                                "player",
                                state.rng,
                                state.fossils,
                            )
                            state.player_actions_left -= 1
                            advance_claims(state.grid)
                            state.current_turn = next_turn_label(state.current_turn)
                        elif tile:
                            state.narration = "That tile is not a valid target."
            elif event.type == pygame.KEYDOWN:
                if state.phase == config.PHASE_EXCAVATION:
                    if event.key == pygame.K_1:
                        state.selected_action = config.ACTION_SURVEY
                    elif event.key == pygame.K_2:
                        state.selected_action = config.ACTION_CAREFUL
                    elif event.key == pygame.K_3:
                        state.selected_action = config.ACTION_RUSH
                    elif event.key == pygame.K_4:
                        state.selected_action = config.ACTION_CLAIM
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
                        if event.key == pygame.K_LEFT:
                            state.lab_selected_focus_index = (state.lab_selected_focus_index - 1) % len(
                                config.LAB_CHOICES
                            )
                        elif event.key == pygame.K_RIGHT:
                            state.lab_selected_focus_index = (state.lab_selected_focus_index + 1) % len(
                                config.LAB_CHOICES
                            )
                        elif event.key == pygame.K_UP and player_fossils:
                            if available_indices:
                                prev_indices = [idx for idx in available_indices if idx < state.lab_selected_fossil_index]
                                state.lab_selected_fossil_index = prev_indices[-1] if prev_indices else available_indices[0]
                        elif event.key == pygame.K_DOWN and player_fossils:
                            if available_indices:
                                next_indices = [idx for idx in available_indices if idx > state.lab_selected_fossil_index]
                                state.lab_selected_fossil_index = next_indices[0] if next_indices else available_indices[-1]
                        elif event.key == pygame.K_RETURN and player_fossils:
                            selected_focus = config.LAB_CHOICES[state.lab_selected_focus_index]
                            target_fossil = player_fossils[state.lab_selected_fossil_index]
                            if target_fossil.fossil_id in state.lab_processed_player:
                                state.lab_result_lines = ["That fossil was already processed."]
                            else:
                                state.lab_pending_focus = selected_focus
                                state.lab_pending_target = target_fossil.fossil_id
                                state.lab_substate = config.LAB_SUB_CONFIRM
                    elif state.lab_substate == config.LAB_SUB_CONFIRM:
                        if event.key == pygame.K_RETURN:
                            pending = state.fossils.get(state.lab_pending_target)
                            result_lines = []
                            if pending:
                                result_lines.append(apply_lab_focus(pending, state.lab_pending_focus, state.rng))
                                state.lab_processed_player.append(pending.fossil_id)
                            state.lab_result_lines = result_lines

                            player_fossils = list_owned_fossils(state.fossils, "player")
                            remaining = [
                                fossil
                                for fossil in player_fossils
                                if fossil.fossil_id not in state.lab_processed_player
                            ]
                            if remaining:
                                next_id = remaining[0].fossil_id
                                state.lab_selected_fossil_index = max(
                                    0,
                                    player_fossils.index(state.fossils[next_id]),
                                )
                                state.lab_substate = config.LAB_SUB_CHOOSE_FOCUS
                            else:
                                state.lab_substate = config.LAB_SUB_RESULT
                            state.lab_pending_focus = None
                            state.lab_pending_target = None
                        elif event.key == pygame.K_BACKSPACE:
                            state.lab_substate = config.LAB_SUB_CHOOSE_FOCUS
                            state.lab_pending_focus = None
                            state.lab_pending_target = None
                    elif state.lab_substate == config.LAB_SUB_RESULT:
                        if event.key == pygame.K_RETURN:
                            state.phase = config.PHASE_MARKET
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

        if state.phase == config.PHASE_EXCAVATION and state.current_turn == "ai":
            if state.ai_actions_left > 0:
                choice = choose_action(state.grid, "ai", state.rng)
                if choice:
                    state.narration = apply_action(
                        choice.action,
                        state.grid,
                        choice.tile,
                        "ai",
                        state.rng,
                        state.fossils,
                    )
                    state.ai_actions_left -= 1
                    advance_claims(state.grid)
                else:
                    state.narration = "Rival AI has no valid actions."
                state.current_turn = next_turn_label(state.current_turn)
            else:
                state.current_turn = next_turn_label(state.current_turn)

        if (
            state.phase == config.PHASE_EXCAVATION
            and state.player_actions_left <= 0
            and state.ai_actions_left <= 0
        ):
            state.phase = config.PHASE_LAB
            state.narration = "Choose a Lab Focus."
            if not state.market_trend:
                state.market_trend = state.rng.choice(MARKET_TRENDS)
            state.lab_substate = config.LAB_SUB_CHOOSE_FOCUS
            state.lab_processed_player = []
            state.lab_selected_focus_index = 0
            state.lab_selected_fossil_index = 0
            state.lab_ai_results = []
            state.lab_pending_focus = None
            state.lab_pending_target = None
            ai_fossils = list_owned_fossils(state.fossils, "ai")
            for fossil in ai_fossils:
                focus = choose_ai_focus_for_fossil(fossil, state.rng, state.market_trend)
                state.lab_ai_results.append(apply_lab_focus(fossil, focus, state.rng))

        screen.fill(config.BACKGROUND_COLOR)
        draw_header(screen, title_font, label_font, state.phase)
        if state.phase == config.PHASE_TITLE:
            title_buttons = draw_title_screen(screen, title_font, label_font)
            final_buttons = []
            journal_buttons = []
        elif state.phase == config.PHASE_JOURNAL:
            journal_buttons = draw_journal_screen(screen, label_font)
            title_buttons = []
            final_buttons = []
        elif state.phase == config.PHASE_EXCAVATION:
            draw_side_panels(
                screen,
                label_font,
                state.player_actions_left,
                state.ai_actions_left,
                state.current_turn,
                config.ACTION_LABELS[state.selected_action],
            )
            draw_grid(screen, state.grid, label_font, state.hover_tile)
            draw_action_bar(screen, label_font, state.selected_action)
            draw_narration(screen, label_font, state.narration)
        elif state.phase == config.PHASE_LAB:
            player_list = [f"{index + 1}. {fossil.name}" for index, fossil in enumerate(list_owned_fossils(state.fossils, "player"))]
            ai_list = [f"{index + 1}. {fossil.name}" for index, fossil in enumerate(list_owned_fossils(state.fossils, "ai"))]
            if state.lab_substate == config.LAB_SUB_CHOOSE_FOCUS:
                focus_label = config.LAB_CHOICES[state.lab_selected_focus_index]
                draw_lab_focus_screen(
                    screen,
                    label_font,
                    player_list,
                    ai_list,
                    state.market_trend,
                    focus_label,
                    state.lab_selected_fossil_index,
                    len(state.lab_processed_player),
                )
            elif state.lab_substate == config.LAB_SUB_RESULT:
                result_lines = state.lab_result_lines + state.lab_ai_results
                draw_lab_result_screen(screen, label_font, result_lines)
            elif state.lab_substate == config.LAB_SUB_CONFIRM:
                target = state.fossils.get(state.lab_pending_target)
                target_name = target.name if target else "Unknown"
                draw_lab_confirm_screen(screen, label_font, state.lab_pending_focus, target_name)
        elif state.phase == config.PHASE_MARKET:
            if state.market_substate == config.MARKET_SUB_INTRO:
                draw_market_intro_screen(screen, label_font, state.market_trend)
            elif state.market_substate == config.MARKET_SUB_REVEAL:
                draw_market_auction_screen(
                    screen,
                    label_font,
                    state.player_score,
                    state.ai_score,
                    state.player_emotion,
                    state.ai_emotion,
                    state.market_trend,
                    state.market_current_event,
                )
            elif state.market_substate == config.MARKET_SUB_FINAL:
                final_buttons = draw_market_final_screen(screen, label_font, state.market_final_lines)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
