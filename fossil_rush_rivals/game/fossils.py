from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from . import config
from .grid import Grid, Tile


@dataclass
class FossilTemplate:
    fossil_id: str
    name: str
    set_id: Optional[str]
    offsets: Sequence[Tuple[int, int]]
    code: str


@dataclass
class Fossil:
    fossil_id: str
    name: str
    set_id: Optional[str]
    tiles: List[Tuple[int, int]]
    owner: Optional[str] = None
    discovered_tiles: List[Tuple[int, int]] = None
    code: str = ""
    rarity: str = "common"
    base_value: int = 120
    condition: float = 0.75
    authenticity: str = "uncertain"
    verified: bool = False
    broken: bool = False
    showcase_bonus: float = 0.0
    lab_focus_applied: Optional[str] = None

    def __post_init__(self) -> None:
        if self.discovered_tiles is None:
            self.discovered_tiles = []


SET_PIECES = {
    "triceratops_display": [
        ("set_trike_horn", "Triceratops Horn Core"),
        ("set_trike_frill", "Triceratops Frill Fragment"),
        ("set_trike_tooth", "Triceratops Tooth"),
    ],
    "marine_predator": [
        ("set_mosasaur_tooth", "Mosasaur Tooth"),
        ("set_mosasaur_vertebra", "Mosasaur Vertebra"),
        ("set_mosasaur_paddle", "Mosasaur Paddle Bone"),
    ],
    "ice_age_mammoth": [
        ("set_mammoth_molar", "Mammoth Molar"),
        ("set_mammoth_tusk", "Mammoth Tusk Fragment"),
        ("set_mammoth_leg", "Mammoth Leg Bone"),
    ],
}

COMMON_FOSSILS = [
    ("fossil_ammonite", "Ammonite", "common", 120),
    ("fossil_trilobite", "Trilobite", "common", 120),
    ("fossil_shark_tooth", "Shark Tooth", "uncommon", 150),
    ("fossil_fern", "Fern Impression", "common", 100),
    ("fossil_wood", "Fossilized Wood", "common", 110),
    ("fossil_brachiopod", "Brachiopod", "common", 115),
    ("fossil_crinoid", "Crinoid Stem", "common", 105),
    ("fossil_coprolite", "Coprolite", "uncommon", 140),
    ("fossil_bone_fragment", "Small Bone Fragment", "common", 90),
]

SHAPES = [
    [(0, 0)],
    [(0, 0), (1, 0)],
    [(0, 0), (0, 1)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 0), (0, 1), (0, 2)],
    [(0, 0), (1, 0), (0, 1)],
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (2, 0), (1, 1)],
    [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (2, 0), (2, 1), (1, 1)],
    [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
    [(0, 0), (1, 0), (0, 1), (1, 1), (2, 1)],
    [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
    [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (1, 2)],
    [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)],
]

FULL_SET_CHANCE = 0.30
DECOY_COUNT = 8


def build_templates(rng) -> List[FossilTemplate]:
    templates: List[FossilTemplate] = []
    common = rng.sample(COMMON_FOSSILS, k=8)
    for fossil_id, name, _rarity, _base_value in common:
        offsets = rng.choice(SHAPES)
        templates.append(
            FossilTemplate(
                fossil_id=fossil_id,
                name=name,
                set_id=None,
                offsets=offsets,
                code=_initials(name),
            )
        )

    if rng.random() < FULL_SET_CHANCE:
        set_id = rng.choice(list(SET_PIECES.keys()))
        for fossil_id, name in SET_PIECES[set_id]:
            offsets = rng.choice(SHAPES)
            templates.append(
                FossilTemplate(
                    fossil_id=fossil_id,
                    name=name,
                    set_id=set_id,
                    offsets=offsets,
                    code=_initials(name),
                )
            )
    else:
        for set_id, pieces in rng.sample(list(SET_PIECES.items()), k=2):
            fossil_id, name = rng.choice(pieces)
            offsets = rng.choice(SHAPES)
            templates.append(
                FossilTemplate(
                    fossil_id=fossil_id,
                    name=name,
                    set_id=set_id,
                    offsets=offsets,
                    code=_initials(name),
                )
            )

    return templates


def place_fossils(grid: Grid, rng) -> Dict[str, Fossil]:
    fossils: Dict[str, Fossil] = {}
    occupied = set()
    templates = build_templates(rng)

    template_stats: Dict[str, Tuple[str, int]] = {
        fossil_id: (rarity, base_value) for fossil_id, _name, rarity, base_value in COMMON_FOSSILS
    }

    for template in templates:
        placed = False
        for _ in range(60):
            base_x = rng.randint(0, len(grid.tiles[0]) - 1)
            base_y = rng.randint(0, len(grid.tiles) - 1)
            coords = []
            valid = True
            for dx, dy in template.offsets:
                x = base_x + dx
                y = base_y + dy
                if not (0 <= x < len(grid.tiles[0]) and 0 <= y < len(grid.tiles)):
                    valid = False
                    break
                if (x, y) in occupied:
                    valid = False
                    break
                tile = grid.get_tile(x, y)
                if tile is None or tile.obstacle:
                    valid = False
                    break
                coords.append((x, y))
            if not valid:
                continue
            core = coords[0]
            for x, y in coords:
                occupied.add((x, y))
                tile = grid.get_tile(x, y)
                if tile:
                    tile.content_type = "fossil"
                    tile.fossil_id = template.fossil_id
                    tile.fossil_code = template.code
                    tile.dig_required = 1
                    tile.fossil_variant = "core" if (x, y) == core else "fragment"
            fossils[template.fossil_id] = Fossil(
                fossil_id=template.fossil_id,
                name=template.name,
                set_id=template.set_id,
                tiles=coords,
                code=template.code,
                rarity=template_stats.get(template.fossil_id, ("rare", 220))[0],
                base_value=template_stats.get(template.fossil_id, ("rare", 220))[1],
                condition=rng.uniform(0.6, 1.0),
            )
            placed = True
            break
        if not placed:
            continue

    _place_decoys(grid, rng, occupied)
    return fossils


def _place_decoys(grid: Grid, rng, occupied: set[tuple[int, int]]) -> None:
    empty_tiles: List[Tile] = []
    for row in grid.tiles:
        for tile in row:
            if not tile.active:
                continue
            if tile.obstacle:
                continue
            if (tile.x, tile.y) not in occupied:
                empty_tiles.append(tile)

    decoy_count = min(DECOY_COUNT, len(empty_tiles))
    for tile in rng.sample(empty_tiles, decoy_count):
        tile.content_type = "decoy"
        tile.dig_required = 2


def reveal_fossil(fossils: Dict[str, Fossil], tile: Tile, owner: str) -> Optional[str]:
    fossil_id = tile.fossil_id
    if not fossil_id:
        return None
    fossil = fossils.get(fossil_id)
    if not fossil:
        return None
    first_claim = fossil.owner is None
    if fossil.owner is None:
        fossil.owner = owner
    coord = (tile.x, tile.y)
    if coord not in fossil.discovered_tiles:
        fossil.discovered_tiles.append(coord)
        if config.AI_DEBUG_LOG:
            owner_label = config.PLAYER_LABEL if fossil.owner == "player" else config.AI_LABEL
            claim_note = " (claim)" if first_claim else ""
            print(
                "Debug: discovered {code} {name} at {x},{y} owned by {owner}{note}.".format(
                    code=fossil.code,
                    name=fossil.name,
                    x=tile.x + 1,
                    y=tile.y + 1,
                    owner=owner_label,
                    note=claim_note,
                )
            )
    return fossil.name


def _initials(name: str) -> str:
    parts = [part for part in name.replace("-", " ").split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return "".join(part[0].upper() for part in parts[:3])
