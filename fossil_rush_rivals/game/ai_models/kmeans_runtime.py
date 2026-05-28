from dataclasses import dataclass
from typing import List


@dataclass
class KMeansModel:
    centers: List[List[float]]

    def score_zone(self, features: List[float]) -> float:
        if not self.centers:
            return 0.0
        best = None
        for center in self.centers:
            if len(center) != len(features):
                continue
            distance = 0.0
            for value, target in zip(features, center):
                diff = value - target
                distance += diff * diff
            if best is None or distance < best:
                best = distance
        if best is None:
            return 0.0
        return 1.0 / (1.0 + best)


def load_model(payload: dict) -> KMeansModel:
    centers = payload.get("centers", []) if payload else []
    return KMeansModel(centers=centers)
