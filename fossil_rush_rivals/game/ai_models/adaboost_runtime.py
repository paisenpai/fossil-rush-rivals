from dataclasses import dataclass
from typing import List


@dataclass
class AdaBoostModel:
    weights: List[float]

    def adjust_score(self, score: float) -> float:
        if not self.weights:
            return score
        total = sum(self.weights)
        factor = 1.0 + (total / max(len(self.weights), 1)) * 0.05
        return score * factor


def load_model(payload: dict) -> AdaBoostModel:
    weights = payload.get("weights", []) if payload else []
    return AdaBoostModel(weights=weights)
