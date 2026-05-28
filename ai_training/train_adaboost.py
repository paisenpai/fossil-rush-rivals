import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import AdaBoostClassifier


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    payload_path = data_dir / "adaboost_model.json"

    data = np.load(data_dir / "synthetic_data.npz")
    features = data["features"]
    labels = data["labels"]

    model = AdaBoostClassifier(n_estimators=10, algorithm="SAMME", random_state=12345)
    model.fit(features, labels)

    payload = {
        "n_estimators": model.n_estimators,
        "classes": model.classes_.tolist(),
    }
    payload_path.write_text(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
