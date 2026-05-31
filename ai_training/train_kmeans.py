import json
from pathlib import Path
import numpy as np

def run_kmeans(X, k=4, max_iters=100, seed=12345):
    rng = np.random.default_rng(seed)
    n_samples, n_features = X.shape
    indices = rng.choice(n_samples, k, replace=False)
    centers = X[indices].copy()
    
    for _ in range(max_iters):
        # Calculate distances from each point to each center
        # X shape: (n_samples, n_features)
        # centers shape: (k, n_features)
        distances = np.linalg.norm(X[:, np.newaxis] - centers, axis=2)
        labels = np.argmin(distances, axis=1)
        
        new_centers = np.zeros_like(centers)
        for i in range(k):
            points = X[labels == i]
            if len(points) > 0:
                new_centers[i] = points.mean(axis=0)
            else:
                new_centers[i] = centers[i]  # keep old center if empty
                
        if np.allclose(centers, new_centers):
            break
        centers = new_centers
        
    return centers

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    payload_path = data_dir / "kmeans_model.json"

    data = np.load(data_dir / "synthetic_data.npz")
    features = data["features"]

    # Manual K-Means
    centers = run_kmeans(features, k=4, seed=12345)

    payload = {
        "centers": centers.tolist(),
        "n_clusters": 4,
    }
    payload_path.write_text(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
