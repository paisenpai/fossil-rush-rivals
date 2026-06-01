import json
from pathlib import Path
import numpy as np

def gmm_em(X, k=3, max_iters=30, seed=12345):
    """
    Expectation-Maximization (EM) Algorithm: "Skeleton Radar"
    
    PURPOSE:
    This algorithm trains a Gaussian Mixture Model (GMM) using Expectation-Maximization
    to determine the orientation, size, and likelihood contours of underground fossil bones.
    
    STRATEGIC REASONING:
    Unlike K-Means (which draws circular boundaries), EM models elliptical shapes 
    with varying orientation and uncertainty (using mean and variance). In paleontology, 
    skeletons are elongated and directional (e.g. spine, limbs). EM maps these 
    elliptical "probability fields" to help the AI deduce where the rest of the 
    skeleton lies once it uncovers a single bone.
    """
    rng = np.random.default_rng(seed)
    n_samples, n_features = X.shape
    
    # 1. INITIALIZATION:
    # Set up our initial assumptions about where the fossil skeletons are.
    indices = rng.choice(n_samples, k, replace=False)
    means = X[indices].copy()         # Initial bone center coordinates
    vars = np.ones((k, n_features))   # Initial bone length/width uncertainty variance
    weights = np.ones(k) / k          # Initial probability weight for each skeleton model
    
    # 2. OPTIMIZATION LOOP: E-step and M-step
    for iteration in range(max_iters):
        # --- EXPECTATION STEP (E-Step) ---
        # "Measure probability of finding a bone here."
        # For every coordinate on our historical map, we calculate the probability that it 
        # belongs to each of our 'k' different dinosaur skeletons.
        resp = np.zeros((n_samples, k))
        for i in range(k):
            diff = X - means[i]
            # Gaussian exponential probability term (calculates distance weighted by variance)
            exp_term = np.exp(-0.5 * np.sum((diff ** 2) / vars[i], axis=1))
            # Normalization term to scale probability values between 0.0 and 1.0
            norm_term = np.sqrt(np.prod(2 * np.pi * vars[i]))
            
            # Handle underflow (avoid dividing by zero if variance is tiny)
            norm_term = max(norm_term, 1e-10)
            
            # Responsibility score: how much this skeleton claims responsibility for this point
            resp[:, i] = weights[i] * exp_term / norm_term
            
        # Normalize the responsibility scores so they sum to 1.0 across all clusters
        resp_sum = resp.sum(axis=1, keepdims=True)
        resp_sum[resp_sum == 0] = 1e-10
        resp /= resp_sum
        
        # --- MAXIMIZATION STEP (M-Step) ---
        # "Recalculate the dimensions & direction of the skeletons."
        # We adjust our means and variances to maximize the fit based on the responsibilities.
        Nk = resp.sum(axis=0)
        Nk_safe = np.maximum(Nk, 1e-10)
        weights = Nk / n_samples  # Update relative importance of each skeleton cluster
        
        for i in range(k):
            # Move the center of the skeleton to the weighted average coordinates of its points
            means[i] = np.sum(resp[:, i:i+1] * X, axis=0) / Nk_safe[i]
            
            # Stretch or shrink the variance (shape/size) of the skeleton based on distance dispersion
            vars[i] = np.sum(resp[:, i:i+1] * (X - means[i])**2, axis=0) / Nk_safe[i]
            # Enforce a minimum variance to prevent the probability ellipses from shrinking into a single line
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
