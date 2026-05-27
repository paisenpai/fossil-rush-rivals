from dataclasses import dataclass
from typing import Dict, List, Optional

import random

from .grid import Grid, Tile
from .fossils import Fossil, place_fossils
from . import config


@dataclass
class GameState:
    phase: str
    match_seed: int
    grid: Grid
    hover_tile: Optional[Tile]
    narration: str
    current_turn: str
    player_actions_left: int
    ai_actions_left: int
    selected_action: str
    rng: random.Random
    fossils: Dict[str, Fossil]
    lab_choice_player: Optional[str]
    lab_choice_ai: Optional[str]
    lab_target_player: Optional[str]
    lab_target_ai: Optional[str]
    lab_substate: str
    lab_result_lines: List[str]
    lab_selected_focus_index: int
    lab_selected_fossil_index: int
    lab_processed_player: List[str]
    lab_ai_results: List[str]
    lab_pending_focus: Optional[str]
    lab_pending_target: Optional[str]
    player_score: int
    ai_score: int
    market_trend: str
    market_narration: List[str]
    player_emotion: str
    ai_emotion: str
    market_substate: str
    market_events: List[dict]
    market_event_index: int
    market_final_lines: List[str]
    market_current_event: str


def create_game_state(start_in_title: bool = True) -> GameState:
    match_seed = config.MATCH_SEED if start_in_title else random.randint(1, 1_000_000_000)
    grid = Grid(seed=match_seed)
    rng = random.Random(match_seed)
    fossils = place_fossils(grid, rng)
    return GameState(
        phase=config.PHASE_TITLE if start_in_title else config.PHASE_EXCAVATION,
        match_seed=match_seed,
        grid=grid,
        hover_tile=None,
        narration=config.NARRATION_TEXT,
        current_turn="player",
        player_actions_left=config.PLAYER_ACTIONS,
        ai_actions_left=config.AI_ACTIONS,
        selected_action=config.ACTION_CAREFUL,
        rng=rng,
        fossils=fossils,
        lab_choice_player=None,
        lab_choice_ai=None,
        lab_target_player=None,
        lab_target_ai=None,
        lab_substate=config.LAB_SUB_CHOOSE_FOCUS,
        lab_result_lines=[],
        lab_selected_focus_index=0,
        lab_selected_fossil_index=0,
        lab_processed_player=[],
        lab_ai_results=[],
        lab_pending_focus=None,
        lab_pending_target=None,
        player_score=0,
        ai_score=0,
        market_trend="",
        market_narration=[],
        player_emotion="Focused",
        ai_emotion="Focused",
        market_substate=config.MARKET_SUB_INTRO,
        market_events=[],
        market_event_index=0,
        market_final_lines=[],
        market_current_event="",
    )
