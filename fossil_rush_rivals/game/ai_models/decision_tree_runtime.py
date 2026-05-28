from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DecisionTreeModel:
    rules: List[Dict[str, float]]
    feature_importances: Dict[str, float]

    def classify(self, features: Dict[str, float]) -> str:
        if not self.rules and not self.feature_importances:
            return "unknown"
        best_label = "unknown"
        best_score = None
        for rule in self.rules:
            label = str(rule.get("label", "unknown"))
            score = float(rule.get("score", 0.0))
            if best_score is None or score > best_score:
                best_score = score
                best_label = label
        return best_label

    def score(self, features: Dict[str, float]) -> float:
        if self.feature_importances:
            total = 0.0
            for name, weight in self.feature_importances.items():
                total += float(features.get(name, 0.0)) * float(weight)
            return total
        if not self.rules:
            return 0.0
        best_score = 0.0
        for rule in self.rules:
            score = float(rule.get("score", 0.0))
            if score > best_score:
                best_score = score
        return best_score


def load_model(payload: dict) -> DecisionTreeModel:
    rules = payload.get("rules", []) if payload else []
    feature_importances = payload.get("feature_importances", {}) if payload else {}
    return DecisionTreeModel(rules=rules, feature_importances=feature_importances)
