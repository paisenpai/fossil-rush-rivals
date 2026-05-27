from typing import Dict, List, Optional, Tuple

from . import config
from .fossils import Fossil


def list_lab_choices() -> List[str]:
    return config.LAB_CHOICES


def list_owned_fossils(fossils: Dict[str, Fossil], owner: str) -> List[Fossil]:
    return [fossil for fossil in fossils.values() if fossil.owner == owner]


def eligible_targets(fossils: Dict[str, Fossil], owner: str, focus: str) -> List[Fossil]:
    owned = list_owned_fossils(fossils, owner)
    if focus == config.LAB_AUTHENTICATE:
        return owned
    if focus == config.LAB_RESTORE:
        return [f for f in owned if f.condition < 0.85]
    if focus == config.LAB_SHOWCASE:
        return owned
    return []


def apply_lab_focus(fossil: Fossil, focus: str, rng) -> str:
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


def choose_ai_focus(fossils: Dict[str, Fossil], rng, market_trend: str) -> Tuple[str, Optional[Fossil]]:
    owned = list_owned_fossils(fossils, "ai")
    if not owned:
        return config.LAB_AUTHENTICATE, None

    damaged = [f for f in owned if f.condition < 0.7]
    if damaged:
        return config.LAB_RESTORE, max(damaged, key=lambda f: f.base_value)

    uncertain = [f for f in owned if f.authenticity != "verified"]
    if uncertain:
        return config.LAB_AUTHENTICATE, max(uncertain, key=lambda f: f.base_value)

    return config.LAB_SHOWCASE, max(owned, key=lambda f: f.base_value)


def choose_ai_focus_for_fossil(fossil: Fossil, rng, market_trend: str) -> str:
    if fossil.condition < 0.7:
        return config.LAB_RESTORE
    if fossil.authenticity != "verified":
        return config.LAB_AUTHENTICATE
    return config.LAB_SHOWCASE


def lab_choice_label(choice: str) -> str:
    return choice
