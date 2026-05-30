from typing import Dict, Iterable, List

from . import config
from .grid import Grid, Tile
from .fossils import Fossil, reveal_fossil


def is_tile_actionable(tile: Tile) -> bool:
    return tile.state in {"hidden", "surveyed"}


def is_tile_claimable(tile: Tile) -> bool:
    return tile.state in {"hidden", "surveyed"}


def _dig_required_for_tile(tile: Tile, fossils: Dict[str, Fossil]) -> int:
    if tile.content_type == "fossil" and tile.fossil_id and tile.fossil_id in fossils:
        fossil = fossils[tile.fossil_id]
        return 3 if len(fossil.tiles) > 1 else 2
    if tile.content_type == "decoy":
        return 2
    return 1


def _fossil_owned_by_other(tile: Tile, actor: str, fossils: Dict[str, Fossil] | None) -> bool:
    if not fossils:
        return False
    if tile.content_type != "fossil" or not tile.fossil_id:
        return False
    fossil = fossils.get(tile.fossil_id)
    return fossil is not None and fossil.owner is not None and fossil.owner != actor


def _apply_rush_damage(tile: Tile, fossils: Dict[str, Fossil], rng, actor: str) -> str:
    if tile.content_type != "fossil" or not tile.fossil_id:
        return ""
    fossil = fossils.get(tile.fossil_id)
    if not fossil or fossil.broken:
        return ""
    if rng.random() <= config.RUSH_BREAK_CHANCE:
        fossil.broken = True
        fossil.condition = 0.0
        fossil.authenticity = "fake"
        fossil.verified = False
        if config.AI_DEBUG_LOG:
            actor_label = config.PLAYER_LABEL if actor == "player" else config.AI_LABEL
            print(f"Debug: {actor_label} shattered {fossil.code} {fossil.name} via rush.")
        return f" The rush shatters {fossil.name}."
    if rng.random() <= config.RUSH_DAMAGE_CHANCE:
        fossil.condition = max(0.0, fossil.condition - rng.uniform(0.15, 0.35))
        if fossil.authenticity == "uncertain":
            fossil.authenticity = "suspicious"
        if config.AI_DEBUG_LOG:
            actor_label = config.PLAYER_LABEL if actor == "player" else config.AI_LABEL
            print(f"Debug: {actor_label} damaged {fossil.code} {fossil.name} via rush.")
        return f" The rush damages {fossil.name}."
    return ""


def apply_survey(tile: Tile, fossils: Dict[str, Fossil]) -> None:
    tile.state = "surveyed"
    if tile.content_type in {"fossil", "decoy"}:
        tile.dig_progress = max(tile.dig_progress, 1)
        tile.dig_required = max(tile.dig_required, _dig_required_for_tile(tile, fossils))
        if tile.content_type == "fossil" and tile.fossil_id and tile.fossil_id in fossils:
            fossil = fossils[tile.fossil_id]
            if len(fossil.tiles) > 1:
                tile.survey_hint = "dense fossil traces"
                return
        tile.survey_hint = "fossil traces"
    else:
        tile.dig_progress = 0
        tile.dig_required = 1
        tile.survey_hint = "faint traces"


def apply_partial_reveal(tile: Tile, fossils: Dict[str, Fossil]) -> None:
    tile.state = "surveyed"
    if tile.content_type in {"fossil", "decoy"}:
        tile.dig_progress = max(tile.dig_progress, 1)
        tile.dig_required = max(tile.dig_required, _dig_required_for_tile(tile, fossils))
        if tile.content_type == "fossil" and tile.fossil_id and tile.fossil_id in fossils:
            fossil = fossils[tile.fossil_id]
            if len(fossil.tiles) > 1:
                tile.survey_hint = "dense fossil traces"
                return
        tile.survey_hint = "fossil traces"
    else:
        tile.survey_hint = "disturbed ground"


def apply_reveal(tile: Tile, owner: str) -> None:
    tile.state = "revealed"
    if tile.content_type == "fossil":
        tile.owner = owner
    else:
        tile.owner = None
    if tile.content_type in {"fossil", "decoy"}:
        tile.dig_progress = max(tile.dig_progress, tile.dig_required)
    else:
        tile.dig_progress = 0


def _apply_dig(tile: Tile, owner: str, fossils: Dict[str, Fossil], action: str, rng) -> str:
    if tile.state == "surveyed" and tile.content_type in {"fossil", "decoy"}:
        tile.dig_progress += 1
        if tile.dig_progress < tile.dig_required:
            label = "fossil" if tile.content_type == "fossil" else "decoy"
            if tile.content_type == "fossil" and tile.fossil_id and tile.fossil_id in fossils:
                label = fossils[tile.fossil_id].name
            rush_note = ""
            if action == config.ACTION_RUSH:
                rush_note = _apply_rush_damage(tile, fossils, rng, owner)
            return (
                f"{config.PLAYER_LABEL if owner == 'player' else config.AI_LABEL} partially exposes"
                f" {label} at {tile.x + 1}, {tile.y + 1}.{rush_note}"
            )

    apply_reveal(tile, owner=owner)
    fossil_name = reveal_fossil(fossils, tile, owner)
    actor_label = config.PLAYER_LABEL if owner == "player" else config.AI_LABEL
    rush_note = ""
    if action == config.ACTION_RUSH:
        rush_note = _apply_rush_damage(tile, fossils, rng, owner)
    if fossil_name:
        return f"{actor_label} reveals {fossil_name} at {tile.x + 1}, {tile.y + 1}.{rush_note}"
    if tile.content_type == "decoy":
        return f"{actor_label} uncovers a decoy at {tile.x + 1}, {tile.y + 1}."
    return f"{actor_label} reveals empty ground at {tile.x + 1}, {tile.y + 1}."


def apply_claim(tile: Tile, owner: str) -> None:
    tile.claimed_by = owner
    tile.claim_turns_left = 1


def can_target_tile(
    tile: Tile,
    action: str,
    actor: str,
    grid: Grid | None = None,
    fossils: Dict[str, Fossil] | None = None,
) -> bool:
    if action in {config.ACTION_CAREFUL, config.ACTION_RUSH, config.ACTION_SURVEY}:
        if action in {config.ACTION_CAREFUL, config.ACTION_RUSH} and _fossil_owned_by_other(tile, actor, fossils):
            return False
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


def _valid_partial_tiles(tiles: Iterable[Tile], actor: str, fossils: Dict[str, Fossil]) -> List[Tile]:
    valid: List[Tile] = []
    for tile in tiles:
        if _fossil_owned_by_other(tile, actor, fossils):
            continue
        if is_tile_actionable(tile) and (tile.claimed_by is None or tile.claimed_by == actor):
            valid.append(tile)
    return valid


def apply_action(action: str, grid: Grid, tile: Tile, actor: str, rng, fossils: Dict[str, Fossil]) -> str:
    actor_label = config.PLAYER_LABEL if actor == "player" else config.AI_LABEL
    if action == config.ACTION_SURVEY:
        tiles = _cross_tiles(grid, tile)
        count = 0
        for survey_tile in tiles:
            if _fossil_owned_by_other(survey_tile, actor, fossils):
                continue
            if is_tile_actionable(survey_tile):
                apply_survey(survey_tile, fossils)
                count += 1
        return f"{actor_label} surveys a cross of {count} tiles."
    if action == config.ACTION_CAREFUL:
        return _apply_dig(tile, actor, fossils, action, rng)
    if action == config.ACTION_RUSH:
        action_text = _apply_dig(tile, actor, fossils, action, rng)
        neighbors = _adjacent_tiles(grid, tile)
        valid = _valid_partial_tiles(neighbors, actor, fossils)
        if valid:
            count = min(len(valid), rng.randint(3, 6))
            for splash_tile in rng.sample(valid, count):
                apply_partial_reveal(splash_tile, fossils)
            return f"{action_text} The rush shakes {count} adjacent tiles."
        return action_text
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
