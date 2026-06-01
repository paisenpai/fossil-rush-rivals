import json
from pathlib import Path
import numpy as np

def manual_adaboost_samme(X, y, n_estimators=10):
    """
    AdaBoost Classifier (SAMME Algorithm): "The Team Leader"
    
    PURPOSE:
    This algorithm trains an ensemble of 10 weak classifiers ("Decision Stumps" or single-level trees)
    sequentially, combining them into a powerful final decision-making committee.
    
    STRATEGIC REASONING:
    In complex matches, no single strategy works 100% of the time. AdaBoost solves this 
    by building a "committee" of specialized, simple rules (weak estimators). When one estimator 
    makes a mistake (e.g. incorrectly predicting the opponent's moves), the next estimator is 
    forced to pay special attention to those exact mistakes. Finally, the "Team Leader" aggregates 
    all estimators' weighted votes (alphas) to choose the ultimate best tactical action.
    """
    n_samples, n_features = X.shape
    K = len(np.unique(y))
    
    # 1. INITIALIZATION:
    # Give all training samples equal weight at the start.
    weights = np.ones(n_samples) / n_samples
    alphas = []  # Weights (voting power) of each decision stump

    # 2. ENSEMBLE LEARNING LOOP:
    for estimator_idx in range(n_estimators):
        best_err = float('inf')
        best_preds = None
        
        # --- FIND BEST DECISION STUMP ---
        # Scan through every single feature and threshold to find a simple rule (stump)
        # that minimizes the weighted classification error.
        for feat in range(n_features):
            thresholds = np.percentile(X[:, feat], [25, 50, 75])
            for thresh in thresholds:
                for target_class in range(K):
                    preds = np.full(n_samples, -1)
                    # If feature value is above the threshold, predict the target class;
                    # otherwise, predict the most common other class.
                    preds[X[:, feat] >= thresh] = target_class
                    
                    # Compute the sum of weights for all misclassified samples
                    err = np.sum(weights[preds != y])
                    if err < best_err:
                        best_err = err
                        best_preds = preds
                        
        # Prevent division by zero errors by adding a tiny offset
        best_err = max(best_err, 1e-10)
        
        # If the weak classifier is worse than random guessing, cap it
        if best_err >= 1.0 - (1.0 / K):
            alphas.append(0.1)
            continue
            
        # --- COMPUTE ESTIMATOR WEIGHT (ALPHA) ---
        # SAMME formula: calculates the voting power of this stump.
        # High accuracy = large alpha (lots of votes). Low accuracy = small alpha.
        alpha = np.log((1.0 - best_err) / best_err) + np.log(K - 1)
        alphas.append(alpha)
        
        # --- UPDATE SAMPLE WEIGHTS ---
        # Exponentially INCREASE the weights of samples that were misclassified,
        # forcing the NEXT decision stump in the loop to focus on correcting these errors!
        weights *= np.exp(alpha * (best_preds != y))
        # Re-normalize weights so they sum back up to 1.0
        weights /= np.sum(weights)
        
    return alphas

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    payload_path = data_dir / "adaboost_model.json"

    data = np.load(data_dir / "synthetic_data.npz")
    features = data["features"]
    labels = data["labels"]

    # Manual AdaBoost
    alphas = manual_adaboost_samme(features, labels, n_estimators=10)

    payload = {
        "n_estimators": 10,
        "classes": np.unique(labels).tolist(),
        "weights": alphas,
    }
    payload_path.write_text(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
