from dataclasses import dataclass
from typing import List, Optional, Tuple

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
    owner: Optional[str] = None
    claimed_by: Optional[str] = None
    claim_turns_left: int = 0
    survey_hint: Optional[str] = None

    def label(self) -> str:
        if self.state == "hidden":
            if self.claimed_by:
                return "X"
            return "?"
        if self.state == "surveyed":
            if self.claimed_by:
                return "X"
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
        center_x = config.GRID_COLS // 2
        center_y = config.GRID_ROWS // 2
        active = {(center_x, center_y)}

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        while len(active) < target:
            x, y = rng.choice(list(active))
            dx, dy = rng.choice(directions)
            nx, ny = x + dx, y + dy
            if 0 <= nx < config.GRID_COLS and 0 <= ny < config.GRID_ROWS:
                active.add((nx, ny))

        active = self._fill_holes(active)
        active = self._remove_spikes(active)
        active = self._largest_connected(active)

        for row in self.tiles:
            for tile in row:
                tile.active = (tile.x, tile.y) in active

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
