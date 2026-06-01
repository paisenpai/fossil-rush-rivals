from dataclasses import dataclass
from typing import List, Optional, Tuple

import math
import random

from . import config


@dataclass
class Tile:
    x: int
    y: int
    active: bool = True
    state: str = "hidden"
    content_type: str = "empty"
    fossil_id: Optional[str] = None
    fossil_code: Optional[str] = None
    fossil_variant: Optional[str] = None
    owner: Optional[str] = None
    claimed_by: Optional[str] = None
    claim_ms_left: int = 0
    dig_progress: int = 0
    dig_required: int = 1
    survey_hint: Optional[str] = None
    survey_state: Optional[str] = None
    survey_result: Optional[str] = None
    survey_started_at: int = 0
    obstacle: bool = False

    def label(self) -> str:
        if self.state == "hidden":
            if self.claimed_by and self.claim_ms_left > 0:
                return "X"
            return "?"
        if self.state == "surveyed":
            if self.claimed_by and self.claim_ms_left > 0:
                return "X"
            if self.content_type in {"fossil", "decoy"} and self.dig_progress > 0:
                return str(min(self.dig_progress, max(self.dig_required, 1)))
            return "S"
        if self.state == "revealed":
            if self.content_type == "decoy":
                return "D"
            if self.content_type == "empty":
                return "."
            if self.owner in {"player", "ai"}:
                prefix = "P" if self.owner == "player" else "A"
                if self.fossil_code:
                    return f"{prefix}-{self.fossil_code}"
                return prefix
            return "."
        return "."


class Grid:
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.tiles = self._build_tiles()
        self._apply_active_shape()

    def _build_tiles(self) -> List[List[Tile]]:
        tiles: List[List[Tile]] = []
        for row in range(config.GRID_ROWS):
            row_tiles: List[Tile] = []
            for col in range(config.GRID_COLS):
                row_tiles.append(Tile(x=col, y=row))
            tiles.append(row_tiles)
        return tiles

    def _apply_active_shape(self) -> None:
        rng = random.Random(self.seed)
        target = min(config.ACTIVE_TILE_COUNT, config.GRID_ROWS * config.GRID_COLS)
        center_x = (config.GRID_COLS - 1) / 2
        center_y = (config.GRID_ROWS - 1) / 2
        radius = math.sqrt(target / math.pi)

        active = set()
        inner = max(radius - 0.75, 0.0)
        outer = radius + 0.75
        for y in range(config.GRID_ROWS):
            for x in range(config.GRID_COLS):
                dx = x - center_x
                dy = y - center_y
                distance = math.hypot(dx, dy)
                if distance <= inner:
                    active.add((x, y))
                elif distance <= outer:
                    edge_weight = max(0.0, (outer - distance) / (outer - inner))
                    if rng.random() < edge_weight:
                        active.add((x, y))

        active = self._fill_holes(active)
        active = self._remove_spikes(active)
        active = self._largest_connected(active)

        for row in self.tiles:
            for tile in row:
                tile.active = (tile.x, tile.y) in active

        self._apply_obstacles(active)

    def _apply_obstacles(self, active: set[Tuple[int, int]]) -> None:
        rng = random.Random(self.seed + 19)
        target = rng.randint(config.OBSTACLE_TILE_MIN, config.OBSTACLE_TILE_MAX)
        clusters = rng.randint(config.OBSTACLE_CLUSTER_MIN, config.OBSTACLE_CLUSTER_MAX)
        spacing = max(0, config.OBSTACLE_CLUSTER_SPACING)
        obstacles: set[Tuple[int, int]] = set()

        active_list = [coord for coord in active]
        if not active_list:
            return

        def is_far_enough(coord: Tuple[int, int]) -> bool:
            if spacing <= 0:
                return True
            cx, cy = coord
            for ox, oy in obstacles:
                if abs(ox - cx) + abs(oy - cy) <= spacing:
                    return False
            return True

        for _ in range(clusters):
            if len(obstacles) >= target:
                break
            remaining = target - len(obstacles)
            cluster_size = min(
                remaining,
                rng.randint(config.OBSTACLE_CLUSTER_SIZE_MIN, config.OBSTACLE_CLUSTER_SIZE_MAX),
            )
            seed = None
            for _attempt in range(20):
                candidate = rng.choice(active_list)
                if candidate in obstacles:
                    continue
                if not is_far_enough(candidate):
                    continue
                seed = candidate
                break
            if seed is None:
                continue
            shape = rng.choice(["blob", "line", "circle"])
            cluster = set()

            if shape == "line":
                direction = rng.choice([(1, 0), (0, 1), (1, 1), (-1, 1)])
                cx, cy = seed
                for _ in range(cluster_size * 2):
                    if (cx, cy) in active and (cx, cy) not in obstacles and is_far_enough((cx, cy)):
                        cluster.add((cx, cy))
                    if len(cluster) >= cluster_size:
                        break
                    cx += direction[0]
                    cy += direction[1]
            elif shape == "circle":
                radius = rng.randint(1, 2)
                cx, cy = seed
                for x in range(cx - radius, cx + radius + 1):
                    for y in range(cy - radius, cy + radius + 1):
                        if (x, y) in active and (x, y) not in obstacles and is_far_enough((x, y)):
                            if math.hypot(x - cx, y - cy) <= radius + 0.25:
                                cluster.add((x, y))
                if len(cluster) > cluster_size:
                    cluster = set(rng.sample(list(cluster), cluster_size))
            else:
                frontier = [seed]
                while frontier and len(cluster) < cluster_size:
                    cx, cy = frontier.pop(0)
                    if (cx, cy) in active and (cx, cy) not in obstacles and is_far_enough((cx, cy)):
                        cluster.add((cx, cy))
                    neighbors = self._neighbors(cx, cy)
                    rng.shuffle(neighbors)
                    for nx, ny in neighbors:
                        if (
                            (nx, ny) in active
                            and (nx, ny) not in obstacles
                            and (nx, ny) not in cluster
                            and is_far_enough((nx, ny))
                        ):
                            frontier.append((nx, ny))
                        if len(cluster) >= cluster_size:
                            break

            obstacles.update(cluster)

        for x, y in obstacles:
            tile = self.get_tile(x, y)
            if tile:
                tile.obstacle = True

    def _neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        neighbors = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < config.GRID_COLS and 0 <= ny < config.GRID_ROWS:
                neighbors.append((nx, ny))
        return neighbors

    def _fill_holes(self, active: set[Tuple[int, int]]) -> set[Tuple[int, int]]:
        updated = set(active)
        for y in range(config.GRID_ROWS):
            for x in range(config.GRID_COLS):
                if (x, y) in updated:
                    continue
                neighbor_count = sum((nx, ny) in updated for nx, ny in self._neighbors(x, y))
                if neighbor_count >= 3:
                    updated.add((x, y))
        return updated

    def _remove_spikes(self, active: set[Tuple[int, int]]) -> set[Tuple[int, int]]:
        updated = set(active)
        for x, y in list(active):
            neighbor_count = sum((nx, ny) in active for nx, ny in self._neighbors(x, y))
            if neighbor_count <= 1:
                updated.discard((x, y))
        return updated

    def _largest_connected(self, active: set[Tuple[int, int]]) -> set[Tuple[int, int]]:
        remaining = set(active)
        components: List[set[Tuple[int, int]]] = []
        while remaining:
            start = remaining.pop()
            stack = [start]
            component = {start}
            while stack:
                cx, cy = stack.pop()
                for nx, ny in self._neighbors(cx, cy):
                    if (nx, ny) in remaining:
                        remaining.remove((nx, ny))
                        component.add((nx, ny))
                        stack.append((nx, ny))
            components.append(component)
        if not components:
            return set()
        return max(components, key=len)

    def get_tile(self, col: int, row: int) -> Optional[Tile]:
        if 0 <= col < config.GRID_COLS and 0 <= row < config.GRID_ROWS:
            tile = self.tiles[row][col]
            return tile if tile.active else None
        return None

    def tile_at_pixel(self, pos: Tuple[int, int]) -> Optional[Tile]:
        x, y = pos
        grid_width = config.GRID_COLS * config.TILE_SIZE
        grid_height = config.GRID_ROWS * config.TILE_SIZE
        if not (config.GRID_LEFT <= x < config.GRID_LEFT + grid_width):
            return None
        if not (config.GRID_TOP <= y < config.GRID_TOP + grid_height):
            return None
        col = (x - config.GRID_LEFT) // config.TILE_SIZE
        row = (y - config.GRID_TOP) // config.TILE_SIZE
        return self.get_tile(int(col), int(row))

    def random_active_tile(self, rng: random.Random) -> Optional[Tile]:
        active_tiles = [tile for row in self.tiles for tile in row if tile.active and not tile.obstacle]
        if not active_tiles:
            return None
        return rng.choice(active_tiles)
