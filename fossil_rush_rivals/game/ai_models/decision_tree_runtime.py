from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DecisionTreeModel:
    rules: List[Dict[str, float]]
    feature_importances: Dict[str, float]
    tree: Optional[Dict] = None
    feature_names: Optional[List[str]] = None

    def _traverse(self, node: Dict, features_list: List[float]) -> float:
        """Walk the exported tree structure to get the mean_value at a leaf."""
        if node.get("type") == "leaf":
            return float(node.get("mean_value", 0.0))
        feat_idx = int(node["feature_index"])
        threshold = float(node["threshold"])
        if feat_idx < len(features_list) and features_list[feat_idx] <= threshold:
            return self._traverse(node["left"], features_list)
        else:
            return self._traverse(node["right"], features_list)

    def score(self, features: Dict[str, float]) -> float:
        # If we have the full tree structure, traverse it properly
        if self.tree and self.feature_names:
            features_list = [float(features.get(name, 0.0)) for name in self.feature_names]
            return self._traverse(self.tree, features_list)
        # Fallback: weighted sum via feature importances
        if self.feature_importances:
            total = 0.0
            for name, weight in self.feature_importances.items():
                total += float(features.get(name, 0.0)) * float(weight)
            return total
        return 0.0

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


def load_model(payload: dict) -> DecisionTreeModel:
    rules = payload.get("rules", []) if payload else []
    feature_importances = payload.get("feature_importances", {}) if payload else {}
    tree = payload.get("tree", None) if payload else None
    feature_names = payload.get("feature_names", None) if payload else None
    return DecisionTreeModel(
        rules=rules,
        feature_importances=feature_importances,
        tree=tree,
        feature_names=feature_names,
    )
