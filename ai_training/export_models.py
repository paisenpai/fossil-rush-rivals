import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)

    payload = {
        "kmeans": _load_json(data_dir / "kmeans_model.json"),
        "decision_tree": _load_json(data_dir / "decision_tree_model.json"),
        "em": _load_json(data_dir / "em_model.json"),
        "adaboost": _load_json(data_dir / "adaboost_model.json"),
    }
    (data_dir / "ai_rules.json").write_text(json.dumps(payload, indent=2))

    market_payload = _load_json(data_dir / "market_model.json")
    (data_dir / "market_model.json").write_text(json.dumps(market_payload, indent=2))

    report_path = data_dir / "training_report.json"
    report = _load_json(report_path)
    report["exported"] = True
    report["export_notes"] = "Exported model payloads for runtime loading."
    report_path.write_text(json.dumps(report, indent=2))

    npz_placeholder = data_dir / "model_weights.npz"
    if not npz_placeholder.exists():
        npz_placeholder.write_text("stub")


if __name__ == "__main__":
    main()
