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
    current_turn: str
    player_actions_left: int
    ai_actions_left: int
    player_rush_left: int
    player_claim_left: int
    ai_rush_left: int
    ai_claim_left: int
    selected_action: str
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


def create_game_state(start_in_title: bool = True) -> GameState:
    match_seed = config.MATCH_SEED if start_in_title else random.randint(1, 1_000_000_000)
    grid = Grid(seed=match_seed)
    rng = random.Random(match_seed)
    fossils = place_fossils(grid, rng)
    journal_data = load_journal()
    return GameState(
        phase=config.PHASE_TITLE if start_in_title else config.PHASE_EXCAVATION,
        match_seed=match_seed,
        grid=grid,
        hover_tile=None,
        narration=config.NARRATION_TEXT,
        current_turn="player",
        player_actions_left=config.PLAYER_ACTIONS,
        ai_actions_left=config.AI_ACTIONS,
        player_rush_left=config.RUSH_ACTION_LIMIT,
        player_claim_left=config.CLAIM_ACTION_LIMIT,
        ai_rush_left=config.RUSH_ACTION_LIMIT,
        ai_claim_left=config.CLAIM_ACTION_LIMIT,
        selected_action=config.ACTION_CAREFUL,
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
    )
