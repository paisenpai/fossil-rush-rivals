from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import json

from .ai_models import (
    AdaBoostModel,
    BackpropModel,
    DecisionTreeModel,
    EmModel,
    KMeansModel,
)

from . import config
from .excavation import can_target_tile
from .grid import Grid, Tile
from .fossils import Fossil


@dataclass
class AiChoice:
    action: str
    tile: Tile


@dataclass
class RuntimeModels:
    kmeans: KMeansModel
    decision_tree: DecisionTreeModel
    em: EmModel
    adaboost: AdaBoostModel
    backprop: BackpropModel
    rules_payload: Dict[str, object]
    market_payload: Dict[str, object]


_RUNTIME_MODELS: Optional[RuntimeModels] = None


def _load_json(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def load_runtime_models(data_dir: Optional[Path] = None) -> RuntimeModels:
    global _RUNTIME_MODELS
    if _RUNTIME_MODELS is not None:
        return _RUNTIME_MODELS

    root = Path(__file__).resolve().parents[2]
    data_path = data_dir or (root / "data")

    rules_payload = _load_json(data_path / "ai_rules.json")
    market_payload = _load_json(data_path / "market_model.json")
    weights_path = data_path / "model_weights.npz"
    if weights_path.exists():
        rules_payload["weights_blob"] = weights_path.read_bytes()

    _RUNTIME_MODELS = RuntimeModels(
        kmeans=KMeansModel(centers=rules_payload.get("kmeans", {}).get("centers", [])),
        decision_tree=DecisionTreeModel(
            rules=rules_payload.get("decision_tree", {}).get("rules", []),
            feature_importances=rules_payload.get("decision_tree", {}).get("feature_importances", {}),
        ),
        em=EmModel(means=rules_payload.get("em", {}).get("means", [])),
        adaboost=AdaBoostModel(weights=rules_payload.get("adaboost", {}).get("weights", [])),
        backprop=BackpropModel(layers=market_payload.get("layers", [])),
        rules_payload=rules_payload,
        market_payload=market_payload,
    )
    return _RUNTIME_MODELS


def _valid_tiles(grid: Grid, action: str, actor: str, fossils: Dict[str, Fossil] | None) -> List[Tile]:
    tiles: List[Tile] = []
    for row in grid.tiles:
        for tile in row:
            if can_target_tile(tile, action, actor, grid, fossils):
                tiles.append(tile)
    return tiles


def _neighbor_coords(x: int, y: int) -> List[Tuple[int, int]]:
    return [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
        (x - 1, y - 1),
        (x + 1, y - 1),
        (x - 1, y + 1),
        (x + 1, y + 1),
    ]


def _count_neighbors(grid: Grid, tile: Tile, actor: str) -> Tuple[int, int, int]:
    ai_revealed = 0
    player_revealed = 0
    surveyed = 0
    for nx, ny in _neighbor_coords(tile.x, tile.y):
        neighbor = grid.get_tile(nx, ny)
        if not neighbor:
            continue
        if neighbor.state == "revealed":
            if neighbor.owner == actor:
                ai_revealed += 1
            else:
                player_revealed += 1
        elif neighbor.state == "surveyed":
            surveyed += 1
    return ai_revealed, player_revealed, surveyed


def _distance_norm(tile: Tile, coords: List[Tuple[int, int]]) -> float:
    if not coords:
        return 1.0
    best = None
    for cx, cy in coords:
        dist = abs(cx - tile.x) + abs(cy - tile.y)
        if best is None or dist < best:
            best = dist
    max_dist = (config.GRID_COLS - 1) + (config.GRID_ROWS - 1)
    return float(best) / max_dist


def _tile_feature_vector(
    grid: Grid,
    tile: Tile,
    actor: str,
    action: str,
    surveyed_coords: List[Tuple[int, int]],
    player_reveal_coords: List[Tuple[int, int]],
    time_left_ms: int | None,
    actor_pos: Tuple[int, int] | None,
    actor_facing: str | None,
    actor_is_moving: bool | None,
    player_pos: Tuple[int, int] | None = None,
) -> List[float]:
    ai_revealed, player_revealed, surveyed_neighbors = _count_neighbors(grid, tile, actor)
    revealed_neighbors = ai_revealed + player_revealed
    dist_survey = _distance_norm(tile, surveyed_coords)
    dist_player_reveal = _distance_norm(tile, player_reveal_coords)
    dist_player = _distance_norm(tile, [player_pos]) if player_pos else 1.0
    x_norm = tile.x / max(config.GRID_COLS - 1, 1)
    y_norm = tile.y / max(config.GRID_ROWS - 1, 1)
    state_hidden = 1.0 if tile.state == "hidden" else 0.0
    state_surveyed = 1.0 if tile.state == "surveyed" else 0.0
    state_revealed = 1.0 if tile.state == "revealed" else 0.0
    claimed = 1.0 if tile.claimed_by else 0.0
    owned_by_actor = 1.0 if tile.owner == actor else 0.0
    action_rush = 1.0 if action == config.ACTION_RUSH else 0.0
    action_claim = 1.0 if action == config.ACTION_CLAIM else 0.0
    time_left_norm = 0.0
    if time_left_ms is not None:
        time_left_norm = min(max(time_left_ms, 0), config.EXCAVATION_DURATION_MS) / max(
            config.EXCAVATION_DURATION_MS,
            1,
        )
    dig_required = max(tile.dig_required, 1)
    dig_progress_norm = 0.0
    dig_required_norm = 0.0
    if tile.dig_progress > 0:
        dig_progress_norm = min(tile.dig_progress, dig_required) / dig_required
        dig_required_norm = min(dig_required, 3) / 3.0
    actor_x_norm = 0.0
    actor_y_norm = 0.0
    if actor_pos is not None:
        actor_x_norm = actor_pos[0] / max(config.GRID_COLS - 1, 1)
        actor_y_norm = actor_pos[1] / max(config.GRID_ROWS - 1, 1)
    facing_one_hot = [0.0] * len(config.DIRECTION_KEYS)
    if actor_facing in config.DIRECTION_KEYS:
        facing_one_hot[config.DIRECTION_KEYS.index(actor_facing)] = 1.0
    moving_flag = 1.0 if actor_is_moving else 0.0

    return [
        x_norm,
        y_norm,
        state_hidden,
        state_surveyed,
        state_revealed,
        claimed,
        owned_by_actor,
        action_rush,
        action_claim,
        revealed_neighbors / 8.0,
        surveyed_neighbors / 8.0,
        dist_survey,
        dist_player_reveal,
        dist_player,
        time_left_norm,
        dig_progress_norm,
        dig_required_norm,
        actor_x_norm,
        actor_y_norm,
        moving_flag,
        *facing_one_hot,
    ]


def _tile_feature_dict(
    grid: Grid,
    tile: Tile,
    actor: str,
    action: str,
    surveyed_coords: List[Tuple[int, int]],
    player_reveal_coords: List[Tuple[int, int]],
    time_left_ms: int | None,
    actor_pos: Tuple[int, int] | None,
    actor_facing: str | None,
    actor_is_moving: bool | None,
    player_pos: Tuple[int, int] | None = None,
) -> Dict[str, float]:
    ai_revealed, player_revealed, surveyed_neighbors = _count_neighbors(grid, tile, actor)
    revealed_neighbors = ai_revealed + player_revealed
    dist_survey = _distance_norm(tile, surveyed_coords)
    dist_player_reveal = _distance_norm(tile, player_reveal_coords)
    time_left_norm = 0.0
    if time_left_ms is not None:
        time_left_norm = min(max(time_left_ms, 0), config.EXCAVATION_DURATION_MS) / max(
            config.EXCAVATION_DURATION_MS,
            1,
        )
    dig_required = max(tile.dig_required, 1)
    dig_progress_norm = 0.0
    dig_required_norm = 0.0
    if tile.dig_progress > 0:
        dig_progress_norm = min(tile.dig_progress, dig_required) / dig_required
        dig_required_norm = min(dig_required, 3) / 3.0
    actor_x_norm = 0.0
    actor_y_norm = 0.0
    if actor_pos is not None:
        actor_x_norm = actor_pos[0] / max(config.GRID_COLS - 1, 1)
        actor_y_norm = actor_pos[1] / max(config.GRID_ROWS - 1, 1)
    moving_flag = 1.0 if actor_is_moving else 0.0
    facing_flags = {f"facing_{key}": 0.0 for key in config.DIRECTION_KEYS}
    if actor_facing in facing_flags:
        facing_flags[f"facing_{actor_facing}"] = 1.0
    return {
        "x_norm": tile.x / max(config.GRID_COLS - 1, 1),
        "y_norm": tile.y / max(config.GRID_ROWS - 1, 1),
        "state_hidden": 1.0 if tile.state == "hidden" else 0.0,
        "state_surveyed": 1.0 if tile.state == "surveyed" else 0.0,
        "state_revealed": 1.0 if tile.state == "revealed" else 0.0,
        "claimed": 1.0 if tile.claimed_by else 0.0,
        "owned_by_actor": 1.0 if tile.owner == actor else 0.0,
        "action_rush": 1.0 if action == config.ACTION_RUSH else 0.0,
        "action_claim": 1.0 if action == config.ACTION_CLAIM else 0.0,
        "revealed_neighbors": revealed_neighbors / 8.0,
        "surveyed_neighbors": surveyed_neighbors / 8.0,
        "dist_survey": dist_survey,
        "dist_player_reveal": dist_player_reveal,
        "dist_player": _distance_norm(tile, [player_pos]) if player_pos else 1.0,
        "time_left": time_left_norm,
        "dig_progress": dig_progress_norm,
        "dig_required": dig_required_norm,
        "ai_revealed": ai_revealed,
        "actor_x": actor_x_norm,
        "actor_y": actor_y_norm,
        "actor_moving": moving_flag,
        **facing_flags,
    }


def _models_ready(models: RuntimeModels) -> bool:
    return any(
        [
            bool(models.kmeans.centers),
            bool(models.decision_tree.rules),
            bool(models.em.means),
            bool(models.adaboost.weights),
            bool(models.backprop.layers),
        ]
    )


def choose_action(
    grid: Grid,
    actor: str,
    rng,
    fossils: Dict[str, Fossil] | None = None,
    rush_left: int | None = None,
    claim_left: int | None = None,
    time_left_ms: int | None = None,
    actor_pos: Tuple[int, int] | None = None,
    actor_facing: str | None = None,
    actor_is_moving: bool | None = None,
    player_pos: Tuple[int, int] | None = None,
) -> Optional[AiChoice]:
    actions = [
        config.ACTION_SURVEY,
        config.ACTION_CAREFUL,
        config.ACTION_RUSH,
        config.ACTION_CLAIM,
    ]
    if rush_left is not None and rush_left <= 0:
        actions.remove(config.ACTION_RUSH)
    if claim_left is not None and claim_left <= 0:
        actions.remove(config.ACTION_CLAIM)
    valid_actions = []
    for action in actions:
        tiles = _valid_tiles(grid, action, actor, fossils)
        if tiles:
            valid_actions.append((action, tiles))
    if not valid_actions:
        return None

    models = load_runtime_models()
    if not _models_ready(models):
        action, tiles = rng.choice(valid_actions)
        tile = rng.choice(tiles)
        return AiChoice(action=action, tile=tile)

    surveyed_coords = [(tile.x, tile.y) for row in grid.tiles for tile in row if tile.state == "surveyed"]
    player_reveal_coords = [
        (tile.x, tile.y)
        for row in grid.tiles
        for tile in row
        if tile.state == "revealed" and tile.owner == "player"
    ]

    scored: List[Tuple[float, str, Tile]] = []
    for action, tiles in valid_actions:
        for tile in tiles:
            vector = _tile_feature_vector(
                grid,
                tile,
                actor,
                action,
                surveyed_coords,
                player_reveal_coords,
                time_left_ms,
                actor_pos,
                actor_facing,
                actor_is_moving,
                player_pos,
            )
            feature_dict = _tile_feature_dict(
                grid,
                tile,
                actor,
                action,
                surveyed_coords,
                player_reveal_coords,
                time_left_ms,
                actor_pos,
                actor_facing,
                actor_is_moving,
                player_pos,
            )
            kmeans_score = models.kmeans.score_zone(vector)
            em_score = models.em.estimate(vector)
            tree_score = models.decision_tree.score(feature_dict)
            market_score = models.backprop.predict_value(vector)
            
            # Distance penalty so AI prefers closer tiles!
            dist_to_ai = abs(tile.x - actor_pos[0]) + abs(tile.y - actor_pos[1]) if actor_pos else 0
            distance_penalty = dist_to_ai * 0.03
            
            combined = kmeans_score + em_score + tree_score + market_score

            aggression_bonus = 0.0
            if action == config.ACTION_RUSH:
                aggression_bonus += (1.0 - feature_dict["dist_survey"]) * 0.3
                aggression_bonus += (1.0 - feature_dict["dist_player_reveal"]) * 0.2
                aggression_bonus += feature_dict["surveyed_neighbors"] * 0.15
                if feature_dict["ai_revealed"] > 0:
                    aggression_bonus += 0.8
            elif action == config.ACTION_CLAIM:
                aggression_bonus += (1.0 - feature_dict["dist_survey"]) * 0.25
                aggression_bonus += (1.0 - feature_dict["dist_player_reveal"]) * 0.2
                aggression_bonus += feature_dict["surveyed_neighbors"] * 0.1
                if feature_dict["ai_revealed"] > 0:
                    aggression_bonus += 0.6
            elif action == config.ACTION_CAREFUL:
                aggression_bonus += (1.0 - feature_dict["dist_survey"]) * 0.1
                if feature_dict["ai_revealed"] > 0:
                    aggression_bonus += 0.7
            combined += aggression_bonus - distance_penalty
            adjusted = models.adaboost.adjust_score(combined)
            scored.append((adjusted, action, tile))

    scored.sort(key=lambda item: (-item[0], item[1], item[2].y, item[2].x))
    best_score, best_action, best_tile = scored[0]
    if config.AI_DEBUG_LOG:
        print(
            "AI debug: action={action} tile=({x},{y}) score={score:.3f}".format(
                action=best_action,
                x=best_tile.x,
                y=best_tile.y,
                score=best_score,
            )
        )
    if best_score == 0.0:
        action, tiles = rng.choice(valid_actions)
        tile = rng.choice(tiles)
        return AiChoice(action=action, tile=tile)
    return AiChoice(action=best_action, tile=best_tile)
