from dataclasses import dataclass
from typing import Dict, List, Optional

import random

from .grid import Grid, Tile
from .fossils import Fossil, place_fossils
from .journal import load_journal
from . import config


@dataclass
class GameState:
    phase: str
    match_seed: int
    grid: Grid
    hover_tile: Optional[Tile]
    narration: str
    player_rush_left: int
    player_claim_left: int
    ai_rush_left: int
    ai_claim_left: int
    player_pos: tuple[int, int]
    ai_pos: tuple[int, int]
    player_facing: str
    ai_facing: str
    player_last_move_ticks: int
    ai_last_move_ticks: int
    player_move_cooldown_until: int
    ai_move_cooldown_until: int
    player_action_cooldown_until: int
    ai_action_cooldown_until: int
    player_last_action: Optional[str]
    ai_last_action: Optional[str]
    player_last_action_ticks: int
    ai_last_action_ticks: int
    player_survey_ready_at: int
    ai_survey_ready_at: int
    ai_next_think_at: int
    ai_target_action: Optional[str]
    ai_target_pos: Optional[tuple[int, int]]
    excavation_start_ticks: int
    excavation_end_ticks: int
    excavation_time_left_ms: int
    ai_status: str
    rng: random.Random
    fossils: Dict[str, Fossil]
    lab_substate: str
    lab_result_lines: List[str]
    lab_selected_fossil_index: int
    lab_processed_player: List[str]
    lab_ai_results: List[str]
    lab_focus_player: Dict[str, str]
    lab_focus_ai: Dict[str, str]
    player_score: int
    ai_score: int
    market_trend: str
    player_emotion: str
    ai_emotion: str
    market_substate: str
    market_events: List[dict]
    market_event_index: int
    market_final_lines: List[str]
    market_current_event: str
    journal_data: Dict[str, object]
    journal_selected_key: Optional[str]
    journal_page: int
    journal_view: str
    journal_show_sets: bool
    journal_show_individuals: bool
    bg_key: str
    is_paused: bool
    excavation_countdown_started_at: int
    excavation_countdown_done: bool
    market_popup_started_at: int
    timeup_popup_started_at: int
    timeup_proceed_pressed: bool
    timeup_proceed_at: int
    last_player_emotion: str
    market_final_sfx_played: bool


def create_game_state(start_in_title: bool = True) -> GameState:
    match_seed = config.MATCH_SEED if start_in_title else random.randint(1, 1_000_000_000)
    grid = Grid(seed=match_seed)
    rng = random.Random(match_seed)
    fossils = place_fossils(grid, rng)
    journal_data = load_journal()
    player_tile = grid.random_active_tile(rng)
    ai_tile = grid.random_active_tile(rng)
    if player_tile is None:
        player_tile = grid.tiles[0][0]
    if ai_tile is None:
        ai_tile = grid.tiles[-1][-1]
    return GameState(
        phase=config.PHASE_TITLE if start_in_title else config.PHASE_EXCAVATION,
        match_seed=match_seed,
        grid=grid,
        hover_tile=None,
        narration=config.NARRATION_TEXT,
        player_rush_left=config.RUSH_ACTION_LIMIT,
        player_claim_left=config.CLAIM_ACTION_LIMIT,
        ai_rush_left=config.RUSH_ACTION_LIMIT,
        ai_claim_left=config.CLAIM_ACTION_LIMIT,
        player_pos=(player_tile.x, player_tile.y),
        ai_pos=(ai_tile.x, ai_tile.y),
        player_facing="s",
        ai_facing="n",
        player_last_move_ticks=0,
        ai_last_move_ticks=0,
        player_move_cooldown_until=0,
        ai_move_cooldown_until=0,
        player_action_cooldown_until=0,
        ai_action_cooldown_until=0,
        player_last_action=None,
        ai_last_action=None,
        player_last_action_ticks=0,
        ai_last_action_ticks=0,
        player_survey_ready_at=0,
        ai_survey_ready_at=0,
        ai_next_think_at=0,
        ai_target_action=None,
        ai_target_pos=None,
        excavation_start_ticks=0,
        excavation_end_ticks=0,
        excavation_time_left_ms=config.EXCAVATION_DURATION_MS,
        ai_status="",
        rng=rng,
        fossils=fossils,
        lab_substate=config.LAB_SUB_CHOOSE_FOCUS,
        lab_result_lines=[],
        lab_selected_fossil_index=0,
        lab_processed_player=[],
        lab_ai_results=[],
        lab_focus_player={},
        lab_focus_ai={},
        player_score=0,
        ai_score=0,
        market_trend="",
        player_emotion="Focused",
        ai_emotion="Focused",
        market_substate=config.MARKET_SUB_INTRO,
        market_events=[],
        market_event_index=0,
        market_final_lines=[],
        market_current_event="",
        journal_data=journal_data,
        journal_selected_key=None,
        journal_page=0,
        journal_view="root",
        journal_show_sets=True,
        journal_show_individuals=True,
        bg_key="homescreen" if start_in_title else "playing_day",
        is_paused=False,
        excavation_countdown_started_at=0,
        excavation_countdown_done=False,
        market_popup_started_at=0,
        timeup_popup_started_at=0,
        timeup_proceed_pressed=False,
        timeup_proceed_at=0,
        last_player_emotion="Focused",
        market_final_sfx_played=False,
    )

