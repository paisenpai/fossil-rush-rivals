import json
from pathlib import Path

import numpy as np
from sklearn.mixture import GaussianMixture


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    payload_path = data_dir / "em_model.json"

    data = np.load(data_dir / "synthetic_data.npz")
    features = data["features"]

    model = GaussianMixture(n_components=3, covariance_type="diag", random_state=12345)
    model.fit(features)

    payload = {
        "means": model.means_.tolist(),
        "weights": model.weights_.tolist(),
    }
    payload_path.write_text(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
