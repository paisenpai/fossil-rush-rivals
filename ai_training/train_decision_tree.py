import json
from pathlib import Path
import numpy as np

def gini(y):
    m = len(y)
    if m == 0:
        return 0.0
    _, counts = np.unique(y, return_counts=True)
    probs = counts / m
    return 1.0 - np.sum(probs ** 2)

class DecisionTree:
    def __init__(self, max_depth=6):
        self.max_depth = max_depth
        self.tree = {}
        self.feature_importances = None
        self.node_count = 0
        self.rules = []
        self.classes = []

    def fit(self, X, y_labels, feature_names, y_values=None):
        self.classes = np.unique(y_labels).tolist()
        n_features = X.shape[1]
        self.feature_importances = np.zeros(n_features)
        self.tree = self._grow_tree(X, y_labels, y_values, depth=0)
        
        # Normalize importances
        total = np.sum(self.feature_importances)
        if total > 0:
            self.feature_importances /= total
            
        self.feature_importances_dict = {
            feature_names[i]: float(self.feature_importances[i])
            for i in range(n_features)
        }

    def _grow_tree(self, X, y_labels, y_values, depth):
        self.node_count += 1
        n_samples, n_features = X.shape
        num_classes = len(np.unique(y_labels))
        
        # Compute the mean value for this node (for regression-like scoring)
        mean_val = float(np.mean(y_values)) if y_values is not None else 0.0
        
        if depth >= self.max_depth or num_classes <= 1 or n_samples < 4:
            leaf_value = self._most_common_label(y_labels)
            self.rules.append({"label": str(leaf_value), "score": mean_val})
            return {"type": "leaf", "value": int(leaf_value), "mean_value": mean_val}
            
        best_feat, best_thresh, best_gain = self._best_split(X, y_labels)
        if best_gain == 0:
            leaf_value = self._most_common_label(y_labels)
            self.rules.append({"label": str(leaf_value), "score": mean_val})
            return {"type": "leaf", "value": int(leaf_value), "mean_value": mean_val}
            
        self.feature_importances[best_feat] += best_gain * n_samples
        
        left_idxs, right_idxs = self._split(X[:, best_feat], best_thresh)
        left_vals = y_values[left_idxs] if y_values is not None else None
        right_vals = y_values[right_idxs] if y_values is not None else None
        left = self._grow_tree(X[left_idxs, :], y_labels[left_idxs], left_vals, depth + 1)
        right = self._grow_tree(X[right_idxs, :], y_labels[right_idxs], right_vals, depth + 1)
        
        return {
            "type": "node",
            "feature_index": int(best_feat),
            "threshold": float(best_thresh),
            "mean_value": mean_val,
            "left": left,
            "right": right,
        }
        
    def _best_split(self, X, y):
        best_gain = -1
        split_idx, split_thresh = None, None
        current_gini = gini(y)
        
        for feat_idx in range(X.shape[1]):
            X_column = X[:, feat_idx]
            thresholds = np.unique(X_column)
            if len(thresholds) > 20:
                # subsample thresholds for speed
                thresholds = np.percentile(X_column, np.linspace(5, 95, 15))
                
            for thresh in thresholds:
                gain = self._information_gain(y, X_column, thresh, current_gini)
                if gain > best_gain:
                    best_gain = gain
                    split_idx = feat_idx
                    split_thresh = thresh
                    
        return split_idx, split_thresh, best_gain
        
    def _information_gain(self, y, X_column, split_thresh, current_gini):
        left_idxs, right_idxs = self._split(X_column, split_thresh)
        if len(left_idxs) == 0 or len(right_idxs) == 0:
            return 0
            
        n = len(y)
        n_l, n_r = len(left_idxs), len(right_idxs)
        e_l, e_r = gini(y[left_idxs]), gini(y[right_idxs])
        child_gini = (n_l / n) * e_l + (n_r / n) * e_r
        return current_gini - child_gini
        
    def _split(self, X_column, split_thresh):
        left_idxs = np.argwhere(X_column <= split_thresh).flatten()
        right_idxs = np.argwhere(X_column > split_thresh).flatten()
        return left_idxs, right_idxs
        
    def _most_common_label(self, y):
        if len(y) == 0:
            return 0
        values, counts = np.unique(y, return_counts=True)
        return values[np.argmax(counts)]

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    payload_path = data_dir / "decision_tree_model.json"

    data = np.load(data_dir / "synthetic_data.npz", allow_pickle=True)
    features = data["features"]
    labels = data["labels"]
    values = data.get("values", labels.astype(float))
    feature_names = [str(name) for name in data.get("feature_names", [])]

    # Manual Decision Tree with deeper depth for better learning
    tree = DecisionTree(max_depth=10)
    tree.fit(features, labels, feature_names, y_values=values)

    payload = {
        "node_count": tree.node_count,
        "max_depth": tree.max_depth,
        "classes": tree.classes,
        "feature_importances": tree.feature_importances_dict,
        "rules": tree.rules,
        "tree": tree.tree,
        "feature_names": feature_names,
    }
    payload_path.write_text(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
