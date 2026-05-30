from typing import Dict, List

from . import config
from .fossils import Fossil


def list_owned_fossils(fossils: Dict[str, Fossil], owner: str) -> List[Fossil]:
    return [fossil for fossil in fossils.values() if fossil.owner == owner]


def apply_lab_focus(fossil: Fossil, focus: str, rng) -> str:
    if fossil.broken:
        return f"{fossil.name} is too shattered to process."
    if config.AI_DEBUG_LOG:
        owner_label = config.PLAYER_LABEL if fossil.owner == "player" else config.AI_LABEL
        print(f"Debug: {owner_label} lab focus {focus} on {fossil.name}.")
    fossil.lab_focus_applied = focus
    if focus == config.LAB_AUTHENTICATE:
        if rng.random() <= config.LAB_AUTHENTICATE_SUCCESS:
            fossil.verified = True
            fossil.authenticity = "verified"
            return f"{fossil.name} was authenticated."
        return f"Authentication failed for {fossil.name}."
    if focus == config.LAB_RESTORE:
        if rng.random() <= config.LAB_RESTORE_SUCCESS:
            boost = rng.uniform(0.2, 0.35)
            fossil.condition = min(1.0, fossil.condition + boost)
            return f"{fossil.name} was restored."
        return f"Restore failed for {fossil.name}."
    if focus == config.LAB_SHOWCASE:
        bonus = rng.uniform(0.15, 0.25)
        fossil.showcase_bonus = min(0.25, fossil.showcase_bonus + bonus)
        return f"{fossil.name} received showcase prep."
    return ""


def choose_ai_focus_for_fossil(fossil: Fossil, rng, market_trend: str) -> str:
    if fossil.condition < 0.7:
        return config.LAB_RESTORE
    if fossil.authenticity != "verified":
        return config.LAB_AUTHENTICATE
    return config.LAB_SHOWCASE


