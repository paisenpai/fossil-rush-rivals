import json
from pathlib import Path
import numpy as np

def gmm_em(X, k=3, max_iters=30, seed=12345):
    rng = np.random.default_rng(seed)
    n_samples, n_features = X.shape
    
    # Subsample for faster training
    if n_samples > 5000:
        indices = rng.choice(n_samples, 5000, replace=False)
        X = X[indices]
        n_samples = len(X)
    
    # Initialize
    indices = rng.choice(n_samples, k, replace=False)
    means = X[indices].copy()
    vars = np.ones((k, n_features))
    weights = np.ones(k) / k
    
    for _ in range(max_iters):
        # E-step
        resp = np.zeros((n_samples, k))
        for i in range(k):
            diff = X - means[i]
            exp_term = np.exp(-0.5 * np.sum((diff ** 2) / vars[i], axis=1))
            norm_term = np.sqrt(np.prod(2 * np.pi * vars[i]))
            # Handle underflow
            norm_term = max(norm_term, 1e-10)
            resp[:, i] = weights[i] * exp_term / norm_term
            
        resp_sum = resp.sum(axis=1, keepdims=True)
        resp_sum[resp_sum == 0] = 1e-10
        resp /= resp_sum
        
        # M-step
        Nk = resp.sum(axis=0)
        Nk_safe = np.maximum(Nk, 1e-10)
        weights = Nk / n_samples
        for i in range(k):
            means[i] = np.sum(resp[:, i:i+1] * X, axis=0) / Nk_safe[i]
            vars[i] = np.sum(resp[:, i:i+1] * (X - means[i])**2, axis=0) / Nk_safe[i]
            vars[i] = np.maximum(vars[i], 1e-6)
            
    return means.tolist(), weights.tolist()

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    payload_path = data_dir / "em_model.json"

    data = np.load(data_dir / "synthetic_data.npz")
    features = data["features"]

    # Manual EM
    means, weights = gmm_em(features, k=3, seed=12345)

    payload = {
        "means": means,
        "weights": weights,
    }
    payload_path.write_text(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
