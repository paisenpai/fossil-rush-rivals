from typing import Dict, List, Tuple

from . import config
from .emotion import resolve_emotions
from .fossils import Fossil, SET_PIECES


MARKET_TRENDS = [
    "Museum Night",
    "Collector Craze",
    "Research Grant",
    "Fraud Panic",
]

RARITY_MULTIPLIER = {
    "common": 1.0,
    "uncommon": 1.25,
    "rare": 1.6,
}

AUTH_MULTIPLIER = {
    "verified": 1.0,
    "uncertain": 0.7,
    "suspicious": 0.45,
    "fake": 0.0,
}

TREND_MULTIPLIER = {
    "Museum Night": 1.1,
    "Collector Craze": 1.15,
    "Research Grant": 1.05,
    "Fraud Panic": 0.85,
}

SET_BONUS = {
    "triceratops_display": (700, 300),
    "marine_predator": (650, 275),
    "ice_age_mammoth": (650, 275),
}


def _set_ids() -> List[str]:
    return list(SET_PIECES.keys())


def _set_completed(fossils: Dict[str, Fossil], set_id: str, owner: str) -> bool:
    pieces = SET_PIECES.get(set_id, [])
    if not pieces:
        return False
    for fossil_id, _name in pieces:
        fossil = fossils.get(fossil_id)
        if not fossil or fossil.owner != owner:
            return False
    return True


def _condition_multiplier(condition: float) -> float:
    if condition >= 0.9:
        return 1.0
    if condition >= 0.75:
        return 0.85
    return 0.6


def _auth_value(authenticity: str, verified: bool) -> str:
    if verified:
        return "verified"
    return authenticity


def fossil_value(fossil: Fossil, trend: str) -> int:
    rarity_mult = RARITY_MULTIPLIER.get(fossil.rarity, 1.0)
    condition_mult = _condition_multiplier(fossil.condition)
    authenticity = _auth_value(fossil.authenticity, fossil.verified)
    auth_mult = AUTH_MULTIPLIER.get(authenticity, 0.7)
    trend_mult = TREND_MULTIPLIER.get(trend, 1.0)
    bonus_value = int(fossil.base_value * fossil.showcase_bonus)
    value = fossil.base_value * rarity_mult * condition_mult * auth_mult * trend_mult
    return int(value + bonus_value)


def build_market_events(
    fossils: Dict[str, Fossil],
    trend: str,
) -> List[dict]:
    events: List[dict] = []
    events.append({"text": f"Auctioneer introduces {trend}.", "player": 0, "ai": 0})

    player_fossils = [f for f in fossils.values() if f.owner == "player"]
    ai_fossils = [f for f in fossils.values() if f.owner == "ai"]

    if not player_fossils:
        events.append({"text": "Player found no fossils to auction.", "player": 0, "ai": 0})
    if not ai_fossils:
        events.append({"text": "Rival found no fossils to auction.", "player": 0, "ai": 0})

    for fossil in player_fossils:
        value = fossil_value(fossil, trend)
        events.append(
            {
                "text": f"Player {fossil.name} valued at +{value}.",
                "player": value,
                "ai": 0,
            }
        )

    for fossil in ai_fossils:
        value = fossil_value(fossil, trend)
        events.append(
            {
                "text": f"Rival {fossil.name} valued at +{value}.",
                "player": 0,
                "ai": value,
            }
        )

    for set_id in _set_ids():
        for owner in ("player", "ai"):
            if _set_completed(fossils, set_id, owner):
                pieces = SET_PIECES[set_id]
                all_verified = True
                for fossil_id, _name in pieces:
                    fossil = fossils.get(fossil_id)
                    if not fossil or not fossil.verified:
                        all_verified = False
                        break
                full_bonus, reduced_bonus = SET_BONUS.get(set_id, (500, 200))
                bonus = full_bonus if all_verified else reduced_bonus
                who = "Player" if owner == "player" else "Rival"
                events.append(
                    {
                        "text": f"{who} set bonus applied: +{bonus}.",
                        "player": bonus if owner == "player" else 0,
                        "ai": bonus if owner == "ai" else 0,
                    }
                )
                if not all_verified:
                    penalty = 200
                    events.append(
                        {
                            "text": f"Suspicion penalty reduces {who} bonus by {penalty}.",
                            "player": -penalty if owner == "player" else 0,
                            "ai": -penalty if owner == "ai" else 0,
                        }
                    )

    events.append({"text": "Final scores are revealed.", "player": 0, "ai": 0})
    return events


def update_emotions(player_score: int, ai_score: int) -> Tuple[str, str]:
    return resolve_emotions(player_score, ai_score)
