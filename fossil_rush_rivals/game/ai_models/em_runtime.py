from dataclasses import dataclass
from typing import List


@dataclass
class EmModel:
    means: List[List[float]]

    def estimate(self, features: List[float]) -> float:
        if not self.means:
            return 0.0
        best = None
        for mean in self.means:
            if len(mean) != len(features):
                continue
            distance = 0.0
            for value, target in zip(features, mean):
                diff = value - target
                distance += diff * diff
            if best is None or distance < best:
                best = distance
        if best is None:
            return 0.0
        return 1.0 / (1.0 + best)


def load_model(payload: dict) -> EmModel:
    means = payload.get("means", []) if payload else []
    return EmModel(means=means)
