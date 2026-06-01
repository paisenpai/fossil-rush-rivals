from typing import Dict, List

from . import config
from .fossils import Fossil


def list_owned_fossils(fossils: Dict[str, Fossil], owner: str) -> List[Fossil]:
	return [fossil for fossil in fossils.values() if fossil.owner == owner]


def apply_lab_focus(fossil: Fossil, focus: str, rng) -> str:
	owner_label = config.PLAYER_LABEL if fossil.owner == "player" else config.AI_LABEL
	damage_note = "Damaged" if fossil.condition < 1.0 else "Intact"
	if fossil.broken:
		return f"{owner_label}: {fossil.name} is too shattered to process."
	if config.AI_DEBUG_LOG:
		print(f"Debug: {owner_label} lab focus {focus} on {fossil.name}.")
	fossil.lab_focus_applied = focus
	if focus == config.LAB_AUTHENTICATE:
		if rng.random() <= config.LAB_AUTHENTICATE_SUCCESS:
			fossil.verified = True
			fossil.authenticity = "verified"
			return f"{owner_label}: {fossil.name} was authenticated. ({damage_note})"
		return f"{owner_label}: Authentication failed for {fossil.name}. ({damage_note})"
	if focus == config.LAB_RESTORE:
		if rng.random() <= config.LAB_RESTORE_SUCCESS:
			fossil.condition = 1.0
			fossil.broken = False
			damage_note = "Damaged" if fossil.condition < 1.0 else "Intact"
			return f"{owner_label}: {fossil.name} was restored. ({damage_note})"
		return f"{owner_label}: Restore failed for {fossil.name}. ({damage_note})"
	if focus == config.LAB_SHOWCASE:
		bonus = rng.uniform(0.15, 0.25)
		fossil.showcase_bonus = min(0.25, fossil.showcase_bonus + bonus)
		return f"{owner_label}: {fossil.name} received showcase prep. ({damage_note})"
	return ""


def choose_ai_focus_for_fossil(fossil: Fossil, rng, market_trend: str) -> str:
	if fossil.condition < 0.7:
		return config.LAB_RESTORE
	trend = market_trend or ""
	if trend == "Fraud Panic":
		if fossil.authenticity != "verified":
			return config.LAB_AUTHENTICATE
		if fossil.condition < 0.85:
			return config.LAB_RESTORE
		return config.LAB_SHOWCASE
	if trend == "Research Grant":
		if fossil.authenticity != "verified":
			return config.LAB_AUTHENTICATE
		if fossil.condition < 0.85:
			return config.LAB_RESTORE
		return config.LAB_SHOWCASE
	if trend == "Collector Craze":
		if fossil.verified:
			return config.LAB_SHOWCASE
		if fossil.condition >= 0.8:
			return config.LAB_AUTHENTICATE
		return config.LAB_RESTORE
	if fossil.verified and fossil.condition >= 0.8:
		return config.LAB_SHOWCASE
	if fossil.authenticity != "verified":
		return config.LAB_AUTHENTICATE
	if fossil.condition < 0.85:
		return config.LAB_RESTORE
	return config.LAB_SHOWCASE
