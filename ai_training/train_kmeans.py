import json
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    payload_path = data_dir / "kmeans_model.json"

    data = np.load(data_dir / "synthetic_data.npz")
    features = data["features"]

    model = KMeans(n_clusters=4, n_init=5, random_state=12345)
    model.fit(features)

    payload = {
        "centers": model.cluster_centers_.tolist(),
        "n_clusters": model.n_clusters,
    }
    payload_path.write_text(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
