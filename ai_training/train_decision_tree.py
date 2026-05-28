import json
from pathlib import Path

import numpy as np
from sklearn.tree import DecisionTreeClassifier


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    payload_path = data_dir / "decision_tree_model.json"

    data = np.load(data_dir / "synthetic_data.npz", allow_pickle=True)
    features = data["features"]
    labels = data["labels"]
    feature_names = [str(name) for name in data.get("feature_names", [])]

    model = DecisionTreeClassifier(max_depth=3, random_state=12345)
    model.fit(features, labels)

    importances = model.feature_importances_.tolist()
    importance_map = {
        name: float(weight)
        for name, weight in zip(feature_names, importances)
        if name
    }
    payload = {
        "node_count": int(model.tree_.node_count),
        "max_depth": int(model.tree_.max_depth),
        "classes": model.classes_.tolist(),
        "feature_importances": importance_map,
        "feature_names": feature_names,
    }
    payload_path.write_text(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
