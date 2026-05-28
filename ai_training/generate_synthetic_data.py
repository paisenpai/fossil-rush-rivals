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

        state_hidden = float(rng.random() < 0.7)
        state_surveyed = float(state_hidden == 0.0 and rng.random() < 0.5)
        state_revealed = float(state_hidden == 0.0 and state_surveyed == 0.0)
        claimed = float(rng.random() < 0.15)
        owned_by_actor = float(rng.random() < 0.25)

        action_rush = float(rng.random() < 0.25)
        action_claim = float(rng.random() < 0.2)

        revealed_neighbors = float(rng.integers(0, 6)) / 8.0
        surveyed_neighbors = float(rng.integers(0, 6)) / 8.0

        survey_count = int(rng.integers(4, 14))
        reveal_count = int(rng.integers(2, 10))
        surveyed_coords = _scatter_coords(rng, hotspots, survey_count, HOTSPOT_SPREAD)
        player_reveal_coords = _scatter_coords(rng, hotspots, reveal_count, HOTSPOT_SPREAD * 0.75)
        dist_hotspot = _distance_norm(x, y, hotspots)

        dist_survey = _distance_norm(x, y, surveyed_coords)
        dist_player_reveal = _distance_norm(x, y, player_reveal_coords)

        remaining_actions = float(rng.integers(1, 16)) / 15.0

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
            ],
            dtype=float,
        )
        features[idx] = feature_row

        fossil_bias = (1.0 - dist_hotspot) * 0.6 + (1.0 - dist_survey) * 0.3 + surveyed_neighbors * 0.2
        fossil_hit = float(rng.random() < min(0.95, 0.12 + fossil_bias))
        set_piece_hit = float(rng.random() < min(0.55, 0.08 + fossil_bias * 0.5))

        base_score = (1.0 - dist_survey) * 0.45 + surveyed_neighbors * 0.3 + revealed_neighbors * 0.25
        aggression_bonus = action_rush * 0.15 + action_claim * 0.12
        reward_bonus = fossil_hit * 0.25 + set_piece_hit * 0.45
        score = min(1.0, base_score + aggression_bonus + reward_bonus)

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
        "notes": "Synthetic dataset with fossil and set-piece reward shaping.",
    }
    (data_dir / "training_report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
