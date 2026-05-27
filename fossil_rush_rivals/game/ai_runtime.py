from dataclasses import dataclass
from typing import List, Optional

from . import config
from .excavation import can_target_tile
from .grid import Grid, Tile


@dataclass
class AiChoice:
    action: str
    tile: Tile


def _valid_tiles(grid: Grid, action: str, actor: str) -> List[Tile]:
    tiles: List[Tile] = []
    for row in grid.tiles:
        for tile in row:
            if can_target_tile(tile, action, actor, grid):
                tiles.append(tile)
    return tiles


def choose_action(grid: Grid, actor: str, rng) -> Optional[AiChoice]:
    actions = [
        config.ACTION_SURVEY,
        config.ACTION_CAREFUL,
        config.ACTION_RUSH,
        config.ACTION_CLAIM,
    ]
    valid_actions = []
    for action in actions:
        tiles = _valid_tiles(grid, action, actor)
        if tiles:
            valid_actions.append((action, tiles))
    if not valid_actions:
        return None
    action, tiles = rng.choice(valid_actions)
    tile = rng.choice(tiles)
    return AiChoice(action=action, tile=tile)
