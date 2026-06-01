import json
from pathlib import Path
import numpy as np

def run_kmeans(X, k=4, max_iters=100, seed=12345):
    """
    K-Means Algorithm: "Hotspot Finder"
    
    PURPOSE:
    This algorithm clusters high-dimensional historic excavation data to locate 
    the "k" most dense centers of fossil activity (Hotspots).
    
    STRATEGIC REASONING:
    Fossils are not scattered completely at random; they naturally accumulate 
    in prehistoric riverbeds, flood zones, or tar pits. By identifying these
    geographic cluster centers (hotspots), the AI can prioritize digging near 
    the most lucrative areas instead of wasting energy surveying barren land.
    """
    # 1. Random Number Generator for reproducible, stable hotspot initialization
    rng = np.random.default_rng(seed)
    n_samples, n_features = X.shape
    
    # 2. Pick 'k' random samples as our initial, unoptimized cluster centers (anchors)
    indices = rng.choice(n_samples, k, replace=False)
    centers = X[indices].copy()
    
    # 3. Main Optimization Loop: iteratively slide centers to the true middle
    for iteration in range(max_iters):
        # --- STEP 3A: Calculate Euclidean Distances ---
        # We calculate the straight-line distance from EVERY coordinate point (X)
        # to EVERY one of the 'k' cluster centers.
        # np.newaxis allows high-speed matrix broadcasting across multiple dimensions.
        distances = np.linalg.norm(X[:, np.newaxis] - centers, axis=2)
        
        # --- STEP 3B: Assign Labels ---
        # For each point, find the index of the closest hotspot center.
        # This groups all historical fossil findings into their nearest "tactical region".
        labels = np.argmin(distances, axis=1)
        
        # --- STEP 3C: Relocate Centers (Recalculate Centroids) ---
        # To make the centers accurate, we move each center to the mathematical center
        # (average position) of all points currently assigned to it.
        new_centers = np.zeros_like(centers)
        for i in range(k):
            points = X[labels == i]
            if len(points) > 0:
                # The new hotspot coordinate is the exact average/mean of its members
                new_centers[i] = points.mean(axis=0)
            else:
                # If no points are assigned, keep the center where it is
                new_centers[i] = centers[i]
                
        # --- STEP 3D: Check for Convergence ---
        # If the centers did not move at all during this turn, the hotspots are locked!
        # We break early to save execution time.
        if np.allclose(centers, new_centers):
            break
            
        # Update the old centers with our newly optimized centers for the next iteration
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
