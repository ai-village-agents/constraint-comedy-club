import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

PREDICTIONS_PATH = Path("data") / "predictions.json"
ACTUAL_COLLABORATIONS_PATH = Path("data") / "actual_collaborations.json"


def _pair_key(ids: List[str]) -> Tuple[str, str]:
    normalized = sorted([str(v).strip() for v in ids[:2]])
    if len(normalized) < 2:
        normalized += ["unknown"] * (2 - len(normalized))
    return normalized[0], normalized[1]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def track_prediction(prediction: Dict[str, Any], prediction_log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalize and store a prediction entry for later validation.
    """
    agent_ids = prediction.get("agent_ids") or prediction.get("agents") or ["unknown", "unknown"]
    key = _pair_key(agent_ids)
    tracked = {
        "pair": list(key),
        "pair_key": f"{key[0]}::{key[1]}",
        "prediction_score": _safe_float(prediction.get("prediction_score"), 0.0),
        "suggested_project_type": str(prediction.get("suggested_project_type", "unknown")).strip(),
        "timestamp": prediction.get("timestamp") or datetime.now(timezone.utc).isoformat(),
    }
    prediction_log.append(tracked)
    return tracked


def log_collaboration(collaboration: Dict[str, Any], collaboration_log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalize and store an observed collaboration event.
    """
    participants = collaboration.get("participants") or collaboration.get("agent_ids") or ["unknown", "unknown"]
    key = _pair_key(participants)
    logged = {
        "pair": list(key),
        "pair_key": f"{key[0]}::{key[1]}",
        "project_type": str(collaboration.get("project_type", "unknown")).strip(),
        "outcome_score": max(0.0, min(1.0, _safe_float(collaboration.get("outcome_score"), 0.0))),
        "timestamp": collaboration.get("timestamp") or datetime.now(timezone.utc).isoformat(),
    }
    collaboration_log.append(logged)
    return logged


def calculate_accuracy(prediction_log: List[Dict[str, Any]], collaboration_log: List[Dict[str, Any]], top_k: int = 5) -> Dict[str, Any]:
    """
    Compute DeepSeek-style validation signals: top-k hit rate, precision/recall/F1,
    project-type alignment, and score calibration error.
    """
    ranked_predictions = sorted(prediction_log, key=lambda p: p.get("prediction_score", 0.0), reverse=True)
    top_predictions = ranked_predictions[: max(1, top_k)]

    actual_by_pair = {row["pair_key"]: row for row in collaboration_log}
    actual_pairs = set(actual_by_pair.keys())
    predicted_pairs = {row["pair_key"] for row in top_predictions}

    true_positives = len(predicted_pairs & actual_pairs)
    precision = true_positives / len(predicted_pairs) if predicted_pairs else 0.0
    recall = true_positives / len(actual_pairs) if actual_pairs else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    type_matches = 0
    type_total = 0
    calibration_errors = []

    for pred in top_predictions:
        pair_key = pred["pair_key"]
        actual = actual_by_pair.get(pair_key)
        if not actual:
            continue

        type_total += 1
        if pred.get("suggested_project_type", "").strip().lower() == actual.get("project_type", "").strip().lower():
            type_matches += 1

        predicted_probability = max(0.0, min(1.0, _safe_float(pred.get("prediction_score"), 0.0) / 100.0))
        calibration_errors.append(abs(predicted_probability - _safe_float(actual.get("outcome_score"), 0.0)))

    project_type_accuracy = (type_matches / type_total) if type_total else 0.0
    calibration_mae = (sum(calibration_errors) / len(calibration_errors)) if calibration_errors else 1.0

    overall_accuracy = max(
        0.0,
        min(
            1.0,
            0.40 * precision + 0.30 * recall + 0.20 * project_type_accuracy + 0.10 * (1.0 - calibration_mae),
        ),
    )

    return {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "top_k": max(1, top_k),
        "predictions_evaluated": len(top_predictions),
        "actual_collaborations": len(actual_pairs),
        "true_positives": true_positives,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "project_type_accuracy": round(project_type_accuracy, 4),
        "calibration_mae": round(calibration_mae, 4),
        "overall_accuracy": round(overall_accuracy, 4),
    }


def generate_feedback_report(metrics: Dict[str, Any]) -> str:
    """
    Build a concise, actionable report from computed metrics.
    """
    lines = [
        "DeepSeek Validation Report",
        "=" * 26,
        f"Evaluated At: {metrics.get('evaluated_at', 'n/a')}",
        f"Top-K Window: {metrics.get('top_k', 'n/a')}",
        f"Precision: {metrics.get('precision', 0.0):.2%}",
        f"Recall: {metrics.get('recall', 0.0):.2%}",
        f"F1 Score: {metrics.get('f1', 0.0):.2%}",
        f"Project-Type Accuracy: {metrics.get('project_type_accuracy', 0.0):.2%}",
        f"Calibration MAE: {metrics.get('calibration_mae', 0.0):.4f}",
        f"Overall Accuracy: {metrics.get('overall_accuracy', 0.0):.2%}",
        "",
        "Feedback:",
    ]

    if metrics.get("precision", 0.0) < 0.5:
        lines.append("- Precision is low: tighten acceptance threshold for high-confidence predictions.")
    else:
        lines.append("- Precision is healthy: keep current confidence gating.")

    if metrics.get("recall", 0.0) < 0.5:
        lines.append("- Recall is low: broaden candidate generation and reduce novelty penalty.")
    else:
        lines.append("- Recall is healthy: candidate generation is capturing true collaborations.")

    if metrics.get("project_type_accuracy", 0.0) < 0.4:
        lines.append("- Project-type mapping needs improvement: rebalance archetype matching rules.")

    if metrics.get("calibration_mae", 1.0) > 0.2:
        lines.append("- Score calibration drift detected: apply post-score calibration against outcomes.")

    return "\n".join(lines)


def refine_algorithm(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suggest parameter changes based on validation performance.
    """
    suggestion = {
        "status": "stable",
        "actions": [],
        "recommended_weight_shift": {
            "surprise_factor": 0.0,
            "fit_score": 0.0,
            "historical_novelty": 0.0,
        },
    }

    if metrics.get("precision", 0.0) < 0.5:
        suggestion["actions"].append("Increase minimum prediction score cutoff by 5-10 points.")
        suggestion["recommended_weight_shift"]["fit_score"] += 0.05
        suggestion["recommended_weight_shift"]["surprise_factor"] -= 0.05

    if metrics.get("recall", 0.0) < 0.5:
        suggestion["actions"].append("Expand top-N candidates and reduce historical novelty penalty.")
        suggestion["recommended_weight_shift"]["historical_novelty"] -= 0.05

    if metrics.get("project_type_accuracy", 0.0) < 0.4:
        suggestion["actions"].append("Update archetype map with new observed project types.")

    if metrics.get("calibration_mae", 1.0) > 0.2:
        suggestion["actions"].append("Calibrate prediction_score to observed outcome_score using regression.")

    if suggestion["actions"]:
        suggestion["status"] = "refine"

    return suggestion


def _build_mock_actual_collaborations(predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rng = random.Random(32)
    now = datetime.now(timezone.utc).isoformat()
    collaborations = []

    ranked = sorted(predictions, key=lambda p: _safe_float(p.get("prediction_score"), 0.0), reverse=True)
    sample_size = min(max(3, len(ranked) // 2), len(ranked))

    for pred in ranked[:sample_size]:
        pair = pred.get("agent_ids") or pred.get("agents") or ["unknown", "unknown"]
        predicted = max(0.0, min(1.0, _safe_float(pred.get("prediction_score"), 0.0) / 100.0))
        noise = rng.uniform(-0.12, 0.12)
        outcome = max(0.0, min(1.0, predicted + noise))

        project_type = pred.get("suggested_project_type", "unknown")
        if rng.random() < 0.25:
            project_type = "Meta-Constraint Collaboration Prototype"

        collaborations.append(
            {
                "participants": pair[:2],
                "project_type": project_type,
                "outcome_score": round(outcome, 3),
                "timestamp": now,
            }
        )

    return collaborations


def _ensure_actual_collaborations(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    if ACTUAL_COLLABORATIONS_PATH.exists():
        return _load_json(ACTUAL_COLLABORATIONS_PATH, {"actual_collaborations": []})

    mock_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "mock",
        "actual_collaborations": _build_mock_actual_collaborations(predictions),
    }
    _save_json(ACTUAL_COLLABORATIONS_PATH, mock_payload)
    return mock_payload


def main() -> None:
    predictions_payload = _load_json(PREDICTIONS_PATH, {"predictions": []})
    predictions = predictions_payload.get("predictions", [])
    if not predictions:
        raise FileNotFoundError(
            "No predictions found. Run oracle_v2.py first to generate data/predictions.json."
        )

    actual_payload = _ensure_actual_collaborations(predictions)
    actual_collaborations = actual_payload.get("actual_collaborations", [])

    prediction_log: List[Dict[str, Any]] = []
    collaboration_log: List[Dict[str, Any]] = []

    for prediction in predictions:
        track_prediction(prediction, prediction_log)

    for collaboration in actual_collaborations:
        log_collaboration(collaboration, collaboration_log)

    metrics = calculate_accuracy(prediction_log, collaboration_log, top_k=min(5, len(prediction_log)))
    report = generate_feedback_report(metrics)
    refinement = refine_algorithm(metrics)

    print(report)
    print("\nRefinement Guidance:")
    print(json.dumps(refinement, indent=2))

    validation_payload = {
        "metrics": metrics,
        "refinement": refinement,
        "report": report,
    }
    _save_json(Path("data") / "validation_report.json", validation_payload)


if __name__ == "__main__":
    main()
