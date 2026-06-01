from dataclasses import dataclass
from typing import List
import math


def _sigmoid(x: float) -> float:
    x = max(-250.0, min(250.0, x))
    return 1.0 / (1.0 + math.exp(-x))


@dataclass
class BackpropModel:
    layers: List[List[List[float]]]
    biases: List[List[List[float]]] | None = None

    def predict_value(self, features: List[float]) -> float:
        if not self.layers:
            return 0.0
        activations = list(features)
        for layer_idx, weight_matrix in enumerate(self.layers):
            if not weight_matrix or not weight_matrix[0]:
                return 0.0
            n_in = len(weight_matrix)
            n_out = len(weight_matrix[0])
            if len(activations) != n_in:
                return 0.0
            new_activations: List[float] = []
            for j in range(n_out):
                z = 0.0
                for i in range(n_in):
                    z += activations[i] * weight_matrix[i][j]
                if self.biases and layer_idx < len(self.biases):
                    bias_row = self.biases[layer_idx]
                    if bias_row and len(bias_row) > 0 and len(bias_row[0]) > j:
                        z += bias_row[0][j]
                # Sigmoid on all layers (matches training)
                z = _sigmoid(z)
                new_activations.append(z)
            activations = new_activations
        if activations:
            return activations[0]
        return 0.0


def load_model(payload: dict) -> BackpropModel:
    layers = payload.get("layers", []) if payload else []
    biases = payload.get("biases", None) if payload else None
    return BackpropModel(layers=layers, biases=biases)
