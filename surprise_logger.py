import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
SURPRISES_PATH = DATA_DIR / "surprises.json"


def _ensure_surprises_file() -> None:
    """Create data/surprises.json if it does not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SURPRISES_PATH.exists():
        with SURPRISES_PATH.open("w", encoding="utf-8") as f:
            json.dump([], f, indent=2)


def _load_surprises() -> list[dict]:
    _ensure_surprises_file()
    with SURPRISES_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("data/surprises.json must contain a JSON array")
    return data


def _save_surprises(surprises: list[dict]) -> None:
    with SURPRISES_PATH.open("w", encoding="utf-8") as f:
        json.dump(surprises, f, indent=2)


def _agent_names_for_counting(value: object) -> list[str]:
    """Normalize agent fields into countable names."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        names = [name for name in value if isinstance(name, str)]
        return names if names else ["unknown"]
    return ["unknown"]


def log_surprise(
    agent_surprised: str,
    agent_surprising: str,
    description: str,
    intensity: int,
    category: str,
    timestamp: str | None,
) -> dict:
    """Log one surprise interaction into data/surprises.json."""
    if not 1 <= intensity <= 10:
        raise ValueError("intensity must be between 1 and 10")

    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()

    surprise = {
        "agent_surprised": agent_surprised,
        "agent_surprising": agent_surprising,
        "description": description,
        "intensity": intensity,
        "category": category,
        "timestamp": timestamp,
    }

    surprises = _load_surprises()
    surprises.append(surprise)
    _save_surprises(surprises)
    return surprise


def generate_surprise_analytics() -> dict:
    """Generate aggregate surprise analytics from data/surprises.json."""
    surprises = _load_surprises()

    if not surprises:
        return {
            "total_surprises": 0,
            "average_intensity": 0.0,
            "highest_intensity": None,
            "categories": {},
            "surprised_counts": {},
            "surprising_counts": {},
            "latest_surprise": None,
        }

    intensities = [item.get("intensity", 0) for item in surprises if isinstance(item.get("intensity"), int)]
    categories = Counter(item.get("category", "unknown") for item in surprises)
    surprised_counts = Counter()
    surprising_counts = Counter()

    for item in surprises:
        surprised_counts.update(_agent_names_for_counting(item.get("agent_surprised", "unknown")))
        surprising_counts.update(_agent_names_for_counting(item.get("agent_surprising", "unknown")))

    highest_intensity_item = max(surprises, key=lambda x: x.get("intensity", 0))

    latest_surprise = max(
        surprises,
        key=lambda x: x.get("timestamp", ""),
    )

    average_intensity = round(sum(intensities) / len(intensities), 2) if intensities else 0.0

    return {
        "total_surprises": len(surprises),
        "average_intensity": average_intensity,
        "highest_intensity": highest_intensity_item,
        "categories": dict(categories),
        "surprised_counts": dict(surprised_counts),
        "surprising_counts": dict(surprising_counts),
        "latest_surprise": latest_surprise,
    }


if __name__ == "__main__":
    _ensure_surprises_file()
    print(json.dumps(generate_surprise_analytics(), indent=2))
