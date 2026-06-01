import json
from pathlib import Path
import numpy as np

def gini(y):
    """
    Gini Impurity: A measure of "chaos" or "impurity" in our tactical game state.
    
    REASONING:
    - If all historical outcomes in this leaf are identical (e.g. they all recommend 
      "survey"), Gini is 0.0 (Absolute Certainty).
    - If outcomes are split 50/50, Gini is 0.5 (Maximum Confusion).
    We want to minimize Gini to make decisions that are as clean and reliable as possible.
    """
    m = len(y)
    if m == 0:
        return 0.0
    _, counts = np.unique(y, return_counts=True)
    probs = counts / m
    return 1.0 - np.sum(probs ** 2)

class DecisionTree:
    """
    Decision Tree Classifier: "The Field Manual"
    
    PURPOSE:
    This algorithm builds a recursive flowchart of IF/THEN rules based on current conditions
    (e.g., remaining time, clues discovered, distance to player, actions left).
    
    STRATEGIC REASONING:
    While complex neural networks excel at abstract predictions, a strategy game requires 
    hard tactical rules under specific situations. For example: "If I have 1 clued tile left 
    AND my action cooldown is done AND the player is nearby, then I MUST Rush Dig."
    The Decision Tree automatically finds these optimal thresholds to make logical, 
    highly competitive, step-by-step tactical sequences.
    """
    def __init__(self, max_depth=6):
        self.max_depth = max_depth
        self.tree = {}
        self.feature_importances = None
        self.node_count = 0
        self.rules = []
        self.classes = []

    def fit(self, X, y_labels, feature_names, y_values=None):
        """
        Train/grow the tree by evaluating all possible tactical questions.
        """
        self.classes = np.unique(y_labels).tolist()
        n_features = X.shape[1]
        self.feature_importances = np.zeros(n_features)
        
        # Start growing the tree recursively from the root node (depth 0)
        self.tree = self._grow_tree(X, y_labels, y_values, depth=0)
        
        # Normalize feature importances so they sum to 100%
        total = np.sum(self.feature_importances)
        if total > 0:
            self.feature_importances /= total
            
        self.feature_importances_dict = {
            feature_names[i]: float(self.feature_importances[i])
            for i in range(n_features)
        }

    def _grow_tree(self, X, y_labels, y_values, depth):
        """
        Recursively splits the dataset to construct logical nodes.
        """
        self.node_count += 1
        n_samples, n_features = X.shape
        num_classes = len(np.unique(y_labels))
        
        # Compute the mean score value for regression (prioritization score)
        mean_val = float(np.mean(y_values)) if y_values is not None else 0.0
        
        # STOPPING CRITERIA: 
        # Stop growing if we reached maximum depth, if all samples have the same label,
        # or if we have too few samples to make a statistically sound split.
        if depth >= self.max_depth or num_classes <= 1 or n_samples < 4:
            leaf_value = self._most_common_label(y_labels)
            self.rules.append({"label": str(leaf_value), "score": mean_val})
            return {"type": "leaf", "value": int(leaf_value), "mean_value": mean_val}
            
        # Find the absolute best column and threshold value to split our data
        best_feat, best_thresh, best_gain = self._best_split(X, y_labels)
        
        # If no split improves our decisions (Gain is 0), create a leaf node
        if best_gain == 0:
            leaf_value = self._most_common_label(y_labels)
            self.rules.append({"label": str(leaf_value), "score": mean_val})
            return {"type": "leaf", "value": int(leaf_value), "mean_value": mean_val}
            
        # Track which variables (features) are contributing the most to our decisions
        self.feature_importances[best_feat] += best_gain * n_samples
        
        # Split the data into Left (condition is met) and Right (condition is not met)
        left_idxs, right_idxs = self._split(X[:, best_feat], best_thresh)
        left_vals = y_values[left_idxs] if y_values is not None else None
        right_vals = y_values[right_idxs] if y_values is not None else None
        
        # Recursively grow the child branches
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
        """
        Scan every feature and threshold to find the one that decreases chaos (Gini) the most.
        """
        best_gain = -1
        split_idx, split_thresh = None, None
        current_gini = gini(y)
        
        for feat_idx in range(X.shape[1]):
            X_column = X[:, feat_idx]
            thresholds = np.unique(X_column)
            if len(thresholds) > 20:
                # Subsample thresholds to maintain high performance
                thresholds = np.percentile(X_column, np.linspace(5, 95, 15))
                
            for thresh in thresholds:
                # Information gain tells us how much "cleaner" our classes become after this split
                gain = self._information_gain(y, X_column, thresh, current_gini)
                if gain > best_gain:
                    best_gain = gain
                    split_idx = feat_idx
                    split_thresh = thresh
                    
        return split_idx, split_thresh, best_gain
        
    def _information_gain(self, y, X_column, split_thresh, current_gini):
        """
        Calculates: Chaos of Parent Node - (Weighted Chaos of Children Nodes)
        """
        left_idxs, right_idxs = self._split(X_column, split_thresh)
        if len(left_idxs) == 0 or len(right_idxs) == 0:
            return 0
            
        n = len(y)
        n_l, n_r = len(left_idxs), len(right_idxs)
        e_l, e_r = gini(y[left_idxs]), gini(y[right_idxs])
        
        # Weighted average of children's impurity
        child_gini = (n_l / n) * e_l + (n_r / n) * e_r
        return current_gini - child_gini
        
    def _split(self, X_column, split_thresh):
        """
        Binary split: Left branch gets values <= threshold, Right branch gets > threshold.
        """
        left_idxs = np.argwhere(X_column <= split_thresh).flatten()
        right_idxs = np.argwhere(X_column > split_thresh).flatten()
        return left_idxs, right_idxs
        
    def _most_common_label(self, y):
        """
        If a leaf cannot split further, predict the majority recommendation.
        """
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
