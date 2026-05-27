from . import config


def resolve_emotions(player_score: int, ai_score: int) -> tuple[str, str]:
    diff = player_score - ai_score
    if diff >= 200:
        return "Elated", "Defeated"
    if diff <= -200:
        return "Defeated", "Elated"
    if diff >= 80:
        return "Focused", "Anxious"
    if diff <= -80:
        return "Anxious", "Focused"
    return "Focused", "Focused"
