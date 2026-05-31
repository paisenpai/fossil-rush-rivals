import json
from pathlib import Path
from typing import List, Tuple

import numpy as np

GRID_COLS = 20
GRID_ROWS = 20
SEED = 12345
SAMPLES = 50000
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
    "claimed",
    "owned_by_actor",
    "action_rush",
    "action_claim",
    "revealed_neighbors",
    "surveyed_neighbors",
    "dist_survey",
    "dist_player_reveal",
    "remaining_actions",
    "dig_progress",
    "dig_required",
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
            rng,
            hotspots,
            player_profile,
        )
        ai_survey_coords, ai_reveal_coords, rush_rate, claim_rate, ai_spread = _build_activity_cloud(
            rng,
            hotspots,
            ai_profile,
        )

        all_survey_coords = player_survey_coords + ai_survey_coords
        all_reveal_coords = player_reveal_coords + ai_reveal_coords

        state_hidden = float(rng.random() < 0.7)
        state_surveyed = float(state_hidden == 0.0 and rng.random() < 0.5)
        state_revealed = float(state_hidden == 0.0 and state_surveyed == 0.0)
        claimed = float(rng.random() < 0.15)
        owned_by_actor = float(rng.random() < 0.25)

        action_rush = float(rng.random() < rush_rate)
        action_claim = float(rng.random() < claim_rate)

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

        remaining_actions = float(rng.integers(1, 16)) / 15.0

        if player_profile_key == "rush" and ai_profile_key == "survey":
            focus_bonus = player_pressure * 0.35 + contest_pressure * 0.30
            aggression_bonus = action_rush * 0.35 + action_claim * 0.30
        elif player_profile_key == "survey" and ai_profile_key == "rush":
            focus_bonus = ai_pressure * 0.35 + contest_pressure * 0.30
            aggression_bonus = action_rush * 0.45 + action_claim * 0.35
        else:
            focus_bonus = contest_pressure * 0.40 + player_pressure * 0.20 + survey_pressure * 0.15
            aggression_bonus = action_rush * 0.40 + action_claim * 0.35

        fossil_bias = (
            (1.0 - dist_hotspot) * 0.42
            + survey_pressure * 0.20
            + player_pressure * 0.16
            + ai_pressure * 0.10
            + contest_pressure * 0.12
        )
        fossil_hit = float(rng.random() < min(0.95, 0.10 + fossil_bias + focus_bonus * 0.25))
        set_piece_hit = float(rng.random() < min(0.55, 0.07 + fossil_bias * 0.45 + contest_pressure * 0.10))
        multi_tile_hit = float(rng.random() < min(0.75, 0.16 + fossil_bias * 0.35 + contest_pressure * 0.15))
        decoy_hit = float(rng.random() < 0.06)

        dig_required = 1.0
        dig_progress = 0.0
        if state_surveyed == 1.0:
            if fossil_hit or decoy_hit:
                dig_required = 3.0 if multi_tile_hit else 2.0
                dig_progress = 1.0
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
                claimed,
                owned_by_actor,
                action_rush,
                action_claim,
                revealed_neighbors,
                surveyed_neighbors,
                dist_survey,
                dist_player_reveal,
                remaining_actions,
                dig_progress_norm,
                dig_required_norm,
            ],
            dtype=float,
        )
        features[idx] = feature_row

        base_score = (
            (1.0 - dist_survey) * 0.30
            + surveyed_neighbors * 0.20
            + revealed_neighbors * 0.18
            + focus_bonus
        )
        reward_bonus = fossil_hit * 0.45 + set_piece_hit * 0.65 + multi_tile_hit * 0.4
        rush_penalty = 0.0
        if action_rush and fossil_hit:
            if rng.random() < RUSH_BREAK_CHANCE:
                rush_penalty = 0.45
            elif rng.random() < RUSH_DAMAGE_CHANCE:
                rush_penalty = 0.18
        score = min(1.0, base_score + aggression_bonus + reward_bonus - rush_penalty)

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
        "notes": "Synthetic dataset with simulated player-versus-rival excavation scenarios, large fossil dig requirements, rush damage risk, and reward shaping.",
        "scenarios": [scenario["name"] for scenario in SCENARIOS],
    }
    (data_dir / "training_report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
