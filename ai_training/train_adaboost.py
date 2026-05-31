import json
from pathlib import Path
import numpy as np

def manual_adaboost_samme(X, y, n_estimators=10):
    n_samples, n_features = X.shape
    K = len(np.unique(y))
    weights = np.ones(n_samples) / n_samples
    alphas = []
    
    # Subsample for faster training
    if n_samples > 2000:
        indices = np.random.choice(n_samples, 2000, replace=False)
        X = X[indices]
        y = y[indices]
        n_samples = len(X)
        weights = np.ones(n_samples) / n_samples

    for _ in range(n_estimators):
        best_err = float('inf')
        best_preds = None
        
        # Find best decision stump
        for feat in range(n_features):
            thresholds = np.percentile(X[:, feat], [25, 50, 75])
            for thresh in thresholds:
                for target_class in range(K):
                    preds = np.full(n_samples, -1)
                    # Simple rule: if X_feat >= thresh, predict target_class, else predict most common other class
                    preds[X[:, feat] >= thresh] = target_class
                    
                    err = np.sum(weights[preds != y])
                    if err < best_err:
                        best_err = err
                        best_preds = preds
                        
        best_err = max(best_err, 1e-10)
        
        if best_err >= 1.0 - (1.0 / K):
            # Cannot learn
            alphas.append(0.1)
            continue
            
        alpha = np.log((1.0 - best_err) / best_err) + np.log(K - 1)
        alphas.append(alpha)
        
        # Update weights
        weights *= np.exp(alpha * (best_preds != y))
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
