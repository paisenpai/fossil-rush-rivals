from typing import Dict, Iterable, List

from . import config
from .grid import Grid, Tile
from .fossils import Fossil, reveal_fossil


def is_tile_actionable(tile: Tile) -> bool:
    return tile.state in {"hidden", "surveyed"}


def is_tile_claimable(tile: Tile) -> bool:
    return tile.state in {"hidden", "surveyed"}


def apply_survey(tile: Tile) -> None:
    tile.state = "surveyed"
    tile.survey_hint = "faint traces"


def apply_partial_reveal(tile: Tile) -> None:
    tile.state = "surveyed"
    tile.survey_hint = "disturbed ground"


def apply_reveal(tile: Tile, owner: str) -> None:
    tile.state = "revealed"
    if tile.content_type == "fossil":
        tile.owner = owner
    else:
        tile.owner = None


def apply_claim(tile: Tile, owner: str) -> None:
    tile.claimed_by = owner
    tile.claim_turns_left = 1


def can_target_tile(tile: Tile, action: str, actor: str, grid: Grid | None = None) -> bool:
    if action in {config.ACTION_CAREFUL, config.ACTION_RUSH, config.ACTION_SURVEY}:
        if tile.claimed_by is not None and tile.claimed_by != actor:
            return False
        if tile.state == "surveyed":
            return True
        return is_tile_actionable(tile) and (tile.claimed_by is None or tile.claimed_by == actor)
    if action == config.ACTION_CLAIM:
        if grid:
            for claim_tile in _area_tiles(grid, tile, radius=1):
                if is_tile_claimable(claim_tile) and claim_tile.claimed_by is None:
                    return True
            return False
        return is_tile_claimable(tile) and tile.claimed_by is None
    return False


def _adjacent_tiles(grid: Grid, center: Tile) -> List[Tile]:
    tiles: List[Tile] = []
    for row in range(center.y - 1, center.y + 2):
        for col in range(center.x - 1, center.x + 2):
            if col == center.x and row == center.y:
                continue
            neighbor = grid.get_tile(col, row)
            if neighbor:
                tiles.append(neighbor)
    return tiles


def _cross_tiles(grid: Grid, center: Tile) -> List[Tile]:
    tiles: List[Tile] = []
    offsets = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]
    for dx, dy in offsets:
        neighbor = grid.get_tile(center.x + dx, center.y + dy)
        if neighbor:
            tiles.append(neighbor)
    return tiles


def _area_tiles(grid: Grid, center: Tile, radius: int) -> List[Tile]:
    tiles: List[Tile] = []
    for row in range(center.y - radius, center.y + radius + 1):
        for col in range(center.x - radius, center.x + radius + 1):
            neighbor = grid.get_tile(col, row)
            if neighbor:
                tiles.append(neighbor)
    return tiles


def _valid_partial_tiles(tiles: Iterable[Tile], actor: str) -> List[Tile]:
    valid: List[Tile] = []
    for tile in tiles:
        if is_tile_actionable(tile) and (tile.claimed_by is None or tile.claimed_by == actor):
            valid.append(tile)
    return valid


def apply_action(action: str, grid: Grid, tile: Tile, actor: str, rng, fossils: Dict[str, Fossil]) -> str:
    actor_label = config.PLAYER_LABEL if actor == "player" else config.AI_LABEL
    if action == config.ACTION_SURVEY:
        tiles = _cross_tiles(grid, tile)
        count = 0
        for survey_tile in tiles:
            if is_tile_actionable(survey_tile):
                apply_survey(survey_tile)
                count += 1
        return f"{actor_label} surveys a cross of {count} tiles."
    if action == config.ACTION_CAREFUL:
        apply_reveal(tile, owner=actor)
        fossil_name = reveal_fossil(fossils, tile, actor)
        if fossil_name:
            return f"{actor_label} reveals {fossil_name} at {tile.x + 1}, {tile.y + 1}."
        if tile.content_type == "decoy":
            return f"{actor_label} uncovers a decoy at {tile.x + 1}, {tile.y + 1}."
        return f"{actor_label} reveals empty ground at {tile.x + 1}, {tile.y + 1}."
    if action == config.ACTION_RUSH:
        apply_reveal(tile, owner=actor)
        fossil_name = reveal_fossil(fossils, tile, actor)
        neighbors = _adjacent_tiles(grid, tile)
        valid = _valid_partial_tiles(neighbors, actor)
        if valid:
            count = min(len(valid), rng.randint(3, 6))
            for splash_tile in rng.sample(valid, count):
                apply_partial_reveal(splash_tile)
            base_text = f"{actor_label} smashes tile {tile.x + 1}, {tile.y + 1}"
            if fossil_name:
                base_text += f" and hits {fossil_name}"
            return f"{base_text}, shaking {count} adjacent tiles."
        if fossil_name:
            return f"{actor_label} smashes tile {tile.x + 1}, {tile.y + 1} and hits {fossil_name}."
        return f"{actor_label} smashes tile {tile.x + 1}, {tile.y + 1}."
    if action == config.ACTION_CLAIM:
        tiles = _area_tiles(grid, tile, radius=1)
        count = 0
        for claim_tile in tiles:
            if is_tile_claimable(claim_tile):
                apply_claim(claim_tile, owner=actor)
                count += 1
        return f"{actor_label} claims a 3x3 zone ({count} tiles)."
    return ""


def advance_claims(grid: Grid) -> None:
    for row in grid.tiles:
        for tile in row:
            if tile.claimed_by is not None:
                tile.claim_turns_left -= 1
                if tile.claim_turns_left <= 0:
                    tile.claimed_by = None
                    tile.claim_turns_left = 0


def next_turn_label(current: str) -> str:
    return "ai" if current == "player" else "player"
