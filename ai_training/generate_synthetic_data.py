import json
from pathlib import Path
from typing import List, Tuple

import numpy as np

GRID_COLS = 20
GRID_ROWS = 20
SEED = 12345
SAMPLES = 80000
HOTSPOT_COUNT = 4
HOTSPOT_SPREAD = 3.5
RUSH_DAMAGE_CHANCE = 0.5
RUSH_BREAK_CHANCE = 0.1

PLAYER_PROFILES = {
    "survey": {
        "survey_range": (10, 18),
        "reveal_range": (2, 7),
        "rush_rate": 0.30,
        "claim_rate": 0.25,
        "spread": 4.2,
    },
    "balanced": {
        "survey_range": (8, 16),
        "reveal_range": (4, 10),
        "rush_rate": 0.50,
        "claim_rate": 0.40,
        "spread": 3.4,
    },
    "rush": {
        "survey_range": (4, 12),
        "reveal_range": (6, 14),
        "rush_rate": 0.75,
        "claim_rate": 0.50,
        "spread": 2.8,
    },
}

SCENARIOS = [
    {
        "name": f"{player}_vs_{ai}",
        "player_profile": player,
        "ai_profile": ai,
    }
    for player in PLAYER_PROFILES
    for ai in PLAYER_PROFILES
]

FEATURE_NAMES = [
    "x_norm",
    "y_norm",
    "state_hidden",
    "state_surveyed",
    "state_revealed",
    "clue_detected",
    "claimed",
    "owned_by_actor",
    "action_survey",
    "action_careful",
    "action_rush",
    "action_claim",
    "revealed_neighbors",
    "surveyed_neighbors",
    "dist_survey",
    "dist_player_reveal",
    "dist_player",
    "time_left",
    "dig_progress",
    "dig_required",
    "actor_x",
    "actor_y",
    "actor_moving",
    "facing_n",
    "facing_ne",
    "facing_e",
    "facing_se",
    "facing_s",
    "facing_sw",
    "facing_w",
    "facing_nw",
]


def _random_coords(rng: np.random.Generator, count: int) -> List[Tuple[int, int]]:
    coords: List[Tuple[int, int]] = []
    for _ in range(count):
        coords.append((int(rng.integers(0, GRID_COLS)), int(rng.integers(0, GRID_ROWS))))
    return coords


def _clamp_coord(value: float, limit: int) -> int:
    return int(max(0, min(limit - 1, round(value))))


def _scatter_coords(
    rng: np.random.Generator,
    centers: List[Tuple[int, int]],
    count: int,
    spread: float,
) -> List[Tuple[int, int]]:
    coords: List[Tuple[int, int]] = []
    if not centers or count <= 0:
        return coords
    for _ in range(count):
        cx, cy = centers[int(rng.integers(0, len(centers)))]
        x = _clamp_coord(rng.normal(cx, spread), GRID_COLS)
        y = _clamp_coord(rng.normal(cy, spread), GRID_ROWS)
        coords.append((x, y))
    return coords


def _distance_norm(x: int, y: int, coords: List[Tuple[int, int]]) -> float:
    if not coords:
        return 1.0
    best = None
    for cx, cy in coords:
        dist = abs(cx - x) + abs(cy - y)
        if best is None or dist < best:
            best = dist
    max_dist = (GRID_COLS - 1) + (GRID_ROWS - 1)
    return float(best) / max_dist


def _build_activity_cloud(
    rng: np.random.Generator,
    centers: List[Tuple[int, int]],
    profile: dict,
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]], float, float, float]:
    survey_count = int(rng.integers(profile["survey_range"][0], profile["survey_range"][1]))
    reveal_count = int(rng.integers(profile["reveal_range"][0], profile["reveal_range"][1]))
    survey_coords = _scatter_coords(rng, centers, survey_count, profile["spread"])
    reveal_coords = _scatter_coords(rng, centers, reveal_count, profile["spread"] * 0.72)
    rush_rate = float(profile["rush_rate"])
    claim_rate = float(profile["claim_rate"])
    spread = float(profile["spread"])
    return survey_coords, reveal_coords, rush_rate, claim_rate, spread


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)

    rng = np.random.default_rng(SEED)

    features = np.zeros((SAMPLES, len(FEATURE_NAMES)), dtype=float)
    labels = np.zeros((SAMPLES,), dtype=int)
    values = np.zeros((SAMPLES,), dtype=float)

    for idx in range(SAMPLES):
        x = int(rng.integers(0, GRID_COLS))
        y = int(rng.integers(0, GRID_ROWS))

        hotspots = _random_coords(rng, HOTSPOT_COUNT)

        scenario = SCENARIOS[int(rng.integers(0, len(SCENARIOS)))]
        player_profile_key = scenario["player_profile"]
        ai_profile_key = scenario["ai_profile"]
        player_profile = PLAYER_PROFILES[player_profile_key]
        ai_profile = PLAYER_PROFILES[ai_profile_key]

        player_survey_coords, player_reveal_coords, _player_rush_rate, _player_claim_rate, player_spread = _build_activity_cloud(
            rng, hotspots, player_profile,
        )
        ai_survey_coords, ai_reveal_coords, rush_rate, claim_rate, ai_spread = _build_activity_cloud(
            rng, hotspots, ai_profile,
        )

        all_survey_coords = player_survey_coords + ai_survey_coords
        all_reveal_coords = player_reveal_coords + ai_reveal_coords

        # ------ Tile state ------
        # Generate balanced tile states with enough surveyed-with-clue samples
        state_roll = rng.random()
        if state_roll < 0.40:
            state_hidden = 1.0; state_surveyed = 0.0; state_revealed = 0.0
        elif state_roll < 0.75:
            state_hidden = 0.0; state_surveyed = 1.0; state_revealed = 0.0
        else:
            state_hidden = 0.0; state_surveyed = 0.0; state_revealed = 1.0

        claimed = float(rng.random() < 0.15)
        owned_by_actor = float(rng.random() < 0.25)

        # ------ Action ------
        # Generate all 4 actions with good coverage
        action_roll = rng.random()
        action_survey = 0.0; action_careful = 0.0; action_rush = 0.0; action_claim = 0.0
        if action_roll < 0.30:
            action_survey = 1.0
        elif action_roll < 0.55:
            action_careful = 1.0
        elif action_roll < 0.75:
            action_rush = 1.0
        else:
            action_claim = 1.0

        # ------ Context features ------
        contest_pressure = 1.0 - min(
            _distance_norm(x, y, player_reveal_coords),
            _distance_norm(x, y, ai_reveal_coords),
        )
        player_pressure = 1.0 - _distance_norm(x, y, player_reveal_coords)
        ai_pressure = 1.0 - _distance_norm(x, y, ai_reveal_coords)
        survey_pressure = 1.0 - _distance_norm(x, y, all_survey_coords)
        revealed_neighbors = min(5.0, (player_pressure + ai_pressure) * 3.0 + rng.random() * 1.5) / 8.0
        surveyed_neighbors = min(5.0, survey_pressure * 4.0 + rng.random() * 1.5) / 8.0
        dist_hotspot = _distance_norm(x, y, hotspots)

        dist_survey = _distance_norm(x, y, all_survey_coords)
        dist_player_reveal = _distance_norm(x, y, player_reveal_coords)

        player_x = float(rng.integers(0, GRID_COLS))
        player_y = float(rng.integers(0, GRID_ROWS))
        dist_player = _distance_norm(x, y, [(int(player_x), int(player_y))])

        time_left = float(rng.integers(5, 60)) / 60.0

        actor_x = float(rng.integers(0, GRID_COLS)) / max(GRID_COLS - 1, 1)
        actor_y = float(rng.integers(0, GRID_ROWS)) / max(GRID_ROWS - 1, 1)
        actor_moving = float(rng.random() < 0.55)
        facing_index = int(rng.integers(0, 8))
        facing_flags = [0.0] * 8
        facing_flags[facing_index] = 1.0

        # ------ Fossil simulation ------
        fossil_bias = (
            (1.0 - dist_hotspot) * 0.42
            + survey_pressure * 0.20
            + player_pressure * 0.16
            + ai_pressure * 0.10
            + contest_pressure * 0.12
        )
        fossil_hit = float(rng.random() < min(0.95, 0.10 + fossil_bias * 0.5))
        set_piece_hit = float(rng.random() < min(0.55, 0.07 + fossil_bias * 0.45))
        multi_tile_hit = float(rng.random() < min(0.75, 0.16 + fossil_bias * 0.35))
        decoy_hit = float(rng.random() < 0.06)

        # ------ Clue detection ------
        clue_detected = 0.0
        if state_surveyed == 1.0:
            if fossil_hit or decoy_hit:
                clue_detected = 1.0

        dig_required = 1.0
        dig_progress = 0.0
        if state_surveyed == 1.0 and clue_detected == 1.0:
            dig_required = 3.0 if multi_tile_hit else 2.0
            dig_progress = dig_required
        elif state_revealed == 1.0:
            if fossil_hit or decoy_hit:
                dig_required = 3.0 if multi_tile_hit else 2.0
                dig_progress = dig_required

        dig_progress_norm = 0.0
        dig_required_norm = 0.0
        if dig_progress > 0.0:
            dig_progress_norm = dig_progress / max(dig_required, 1.0)
            dig_required_norm = min(dig_required, 3.0) / 3.0

        feature_row = np.array(
            [
                x / max(GRID_COLS - 1, 1),
                y / max(GRID_ROWS - 1, 1),
                state_hidden,
                state_surveyed,
                state_revealed,
                clue_detected,
                claimed,
                owned_by_actor,
                action_survey,
                action_careful,
                action_rush,
                action_claim,
                revealed_neighbors,
                surveyed_neighbors,
                dist_survey,
                dist_player_reveal,
                dist_player,
                time_left,
                dig_progress_norm,
                dig_required_norm,
                actor_x,
                actor_y,
                actor_moving,
                *facing_flags,
            ],
            dtype=float,
        )
        features[idx] = feature_row

        # ============================================================
        # SCORING LOGIC — teaches the AI the correct game strategy
        # ============================================================
        #
        # The AI should learn this priority:
        #   1. Dig tiles that have clues (surveyed + clue_detected) -> HIGHEST
        #   2. Survey hidden tiles to discover clues             -> HIGH
        #   3. Claim zones near clues when player is close       -> MEDIUM-HIGH
        #   4. Everything else (blind dig, re-survey, etc.)      -> LOW/ZERO

        score = 0.0

        if action_survey == 1.0:
            if state_hidden == 1.0:
                # GOOD: surveying unexplored tiles is the right first step
                score = 0.55 + (1.0 - dist_hotspot) * 0.20 + survey_pressure * 0.10
            elif state_surveyed == 1.0:
                # BAD: re-surveying already surveyed tiles is wasteful
                score = 0.05
            else:
                # state_revealed - surveying already dug tiles is pointless
                score = 0.02

        elif action_careful == 1.0:
            if state_surveyed == 1.0 and clue_detected == 1.0:
                if time_left < 0.3:
                    # Time is running out! Careful dig is too slow, rush it instead!
                    score = 0.40
                elif dist_player < 0.2 and claimed == 0.0:
                    # Player is too close, better to claim first!
                    score = 0.60
                else:
                    # BEST: standard high quality dig
                    score = 0.90 + set_piece_hit * 0.05 + multi_tile_hit * 0.05
            elif state_surveyed == 1.0 and clue_detected == 0.0:
                score = 0.03
            elif state_hidden == 1.0:
                score = 0.05
            else:
                score = 0.02

        elif action_rush == 1.0:
            if state_surveyed == 1.0 and clue_detected == 1.0:
                # If time is running out OR player is extremely close, rush is highly favored!
                if time_left < 0.3:
                    score = 0.95
                elif dist_player < 0.2:
                    score = 0.93
                else:
                    # Standard rush dig (risky but okay)
                    rush_penalty = 0.0
                    if fossil_hit:
                        if rng.random() < RUSH_BREAK_CHANCE:
                            rush_penalty = 0.30
                        elif rng.random() < RUSH_DAMAGE_CHANCE:
                            rush_penalty = 0.15
                    score = 0.80 + multi_tile_hit * 0.05 - rush_penalty
            elif state_surveyed == 1.0 and clue_detected == 0.0:
                score = 0.03
            elif state_hidden == 1.0:
                score = 0.04
            else:
                score = 0.02

        elif action_claim == 1.0:
            if state_surveyed == 1.0 and clue_detected == 1.0:
                # If player is close and tile is not claimed, we MUST claim to protect it!
                if dist_player < 0.2 and claimed == 0.0:
                    score = 0.98
                else:
                    player_closeness = 1.0 - dist_player
                    score = 0.40 + player_closeness * 0.40 + set_piece_hit * 0.10
            elif state_hidden == 1.0:
                player_closeness = 1.0 - dist_player
                score = 0.15 + player_closeness * 0.25
            else:
                score = 0.10

        score = max(0.0, min(1.0, score))
        values[idx] = score
        if score < 0.33:
            labels[idx] = 0
        elif score < 0.66:
            labels[idx] = 1
        else:
            labels[idx] = 2

    np.savez(
        data_dir / "synthetic_data.npz",
        features=features,
        labels=labels,
        values=values,
        feature_names=np.array(FEATURE_NAMES, dtype=object),
    )

    report = {
        "seed": SEED,
        "samples": SAMPLES,
        "feature_count": features.shape[1],
        "feature_names": FEATURE_NAMES,
        "notes": "Synthetic dataset with strategy-aware scoring: survey hidden > dig clues > claim defensively. Blind digging heavily penalized.",
        "scenarios": [scenario["name"] for scenario in SCENARIOS],
    }
    (data_dir / "training_report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
