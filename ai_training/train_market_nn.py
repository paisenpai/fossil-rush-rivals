import json
from pathlib import Path

import numpy as np
from sklearn.neural_network import MLPRegressor


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    payload_path = data_dir / "market_model.json"

    data = np.load(data_dir / "synthetic_data.npz")
    features = data["features"]
    labels = data.get("values", data["labels"]).astype(float)

    model = MLPRegressor(hidden_layer_sizes=(8, 4), random_state=12345, max_iter=1000)
    model.fit(features, labels)

    payload = {
        "layers": [weights.tolist() for weights in model.coefs_],
        "biases": [biases.tolist() for biases in model.intercepts_],
    }
    payload_path.write_text(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
