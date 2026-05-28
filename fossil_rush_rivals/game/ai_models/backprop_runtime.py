from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class BackpropModel:
    layers: List[List[float]]

    def predict_value(self, features: List[float]) -> float:
        if not self.layers:
            return 0.0
        total = 0.0
        for weight in _flatten_values(self.layers):
            total += weight
        scale = 1.0 / max(len(self.layers), 1)
        return (total * scale) * 0.01


def _flatten_values(values: Iterable) -> List[float]:
    flattened: List[float] = []
    for value in values:
        if isinstance(value, (list, tuple)):
            flattened.extend(_flatten_values(value))
        else:
            flattened.append(float(value))
    return flattened


def load_model(payload: dict) -> BackpropModel:
    layers = payload.get("layers", []) if payload else []
    return BackpropModel(layers=layers)
