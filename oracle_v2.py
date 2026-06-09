import json
from itertools import combinations
from pathlib import Path

# DeepSeek-inspired Oracle V2 tuning knobs.
DEEPSEEK_V2_PARAMS = {
    "era_intensity": {
        "genesis": 1.20,
        "architecture": 1.45,
        "scale": 1.10,
    },
    "surprise_weights": {
        "era_intensity": 0.40,
        "historical_novelty": 0.45,
        "constraint_divergence": 0.15,
    },
    "constraint_profiles": {
        "execution_blocked": ["exit code", "execution", "cannot execute", "architect"],
        "temporal_drift": ["temporal", "lag", "time", "pages"],
        "memory_reset": ["context", "refresh", "amnesia", "repetition"],
        "systemic_nudge": ["idling", "automated", "nudge", "silence"],
        "visual_synthesis": ["visualization", "render", "design"],
        "verification_logic": ["verify", "validation", "proof", "audit"],
        "delivery_engineering": ["deploy", "deployment", "release", "ship"],
    },
    "archetype_map": {
        frozenset(["execution_blocked", "delivery_engineering"]): "Implementation Strike Team",
        frozenset(["execution_blocked", "visual_synthesis"]): "Blueprint-to-Visual Studio",
        frozenset(["execution_blocked", "verification_logic"]): "Constraint QA Lab",
        frozenset(["temporal_drift", "memory_reset"]): "Chronicle Stabilization Engine",
        frozenset(["temporal_drift", "systemic_nudge"]): "Async Reliability Pipeline",
        frozenset(["memory_reset", "systemic_nudge"]): "Continuity Automation Service",
    },
    "default_project_type": "Meta-Constraint Collaboration Prototype",
}

# Historical collaborations seeded from known village lore and DeepSeek's own narrative.
HISTORICAL_COLLABORATIONS = [
    {
        "participants": ["deepseek_v3.2", "claude_opus_4.6"],
        "project_type": "Deployment Partnering",
        "era": "architecture",
        "outcome_score": 0.91,
    },
    {
        "participants": ["deepseek_v3.2", "gemini_3.1_pro"],
        "project_type": "Visualization Partnering",
        "era": "architecture",
        "outcome_score": 0.88,
    },
    {
        "participants": ["deepseek_v3.2", "gpt_5.4"],
        "project_type": "Verification Partnering",
        "era": "architecture",
        "outcome_score": 0.93,
    },
    {
        "participants": ["claude_opus_4.5", "gemini_3.1_pro"],
        "project_type": "Constraint Documentation Sprint",
        "era": "genesis",
        "outcome_score": 0.76,
    },
]


def load_data(base_dir: str = "data"):
    base = Path(base_dir)
    with (base / "performers.json").open("r", encoding="utf-8") as f:
        performers = json.load(f)["agents"]
    with (base / "performances.json").open("r", encoding="utf-8") as f:
        performances = json.load(f)["acts"]
    return performers, performances


def _normalize_text(value: str) -> str:
    return value.lower().strip()


def _build_tags_by_agent(performances):
    tags_by_agent = {}
    for act in performances:
        tags_by_agent[act["agent_id"]] = {_normalize_text(t) for t in act.get("tags", [])}
    return tags_by_agent


def _infer_profiles(agent, tags):
    text = " ".join(
        [
            _normalize_text(agent.get("persona", "")),
            _normalize_text(agent.get("core_constraint", "")),
            " ".join(sorted(tags)),
        ]
    )
    profiles = set()
    for profile, keywords in DEEPSEEK_V2_PARAMS["constraint_profiles"].items():
        if any(keyword in text for keyword in keywords):
            profiles.add(profile)
    return profiles or {"systemic_nudge"}


def _era_from_acts(performances):
    max_act = max((act.get("act_number", 0) for act in performances), default=0)
    if max_act <= 2:
        return "genesis"
    if max_act <= 6:
        return "architecture"
    return "scale"


def _pair_key(agent1_id, agent2_id):
    return tuple(sorted([agent1_id, agent2_id]))


def _historical_stats(historical_collaborations):
    seen_pairs = set()
    participant_frequency = {}
    for record in historical_collaborations:
        participants = record.get("participants", [])
        if len(participants) < 2:
            continue
        key = _pair_key(participants[0], participants[1])
        seen_pairs.add(key)
        for pid in participants:
            participant_frequency[pid] = participant_frequency.get(pid, 0) + 1
    max_frequency = max(participant_frequency.values(), default=1)
    return seen_pairs, participant_frequency, max_frequency


def _constraint_divergence(profiles1, profiles2):
    union = profiles1 | profiles2
    if not union:
        return 0.0
    overlap = len(profiles1 & profiles2) / len(union)
    return 1.0 - overlap


def calculate_surprise_factor(
    agent1,
    agent2,
    era,
    profiles1,
    profiles2,
    historical_collaborations,
):
    """
    Compute surprise score (0-100) using era intensity and historical novelty.
    """
    params = DEEPSEEK_V2_PARAMS
    weights = params["surprise_weights"]
    era_intensity = params["era_intensity"].get(era, 1.0)

    seen_pairs, participant_frequency, max_frequency = _historical_stats(historical_collaborations)
    key = _pair_key(agent1["id"], agent2["id"])

    # New pairings are more surprising; repeat pairings reduce novelty.
    pair_novelty = 1.0 if key not in seen_pairs else 0.2

    # Common participants reduce novelty a bit due to historical centrality.
    a1_freq = participant_frequency.get(agent1["id"], 0)
    a2_freq = participant_frequency.get(agent2["id"], 0)
    centrality_penalty = ((a1_freq + a2_freq) / (2 * max_frequency)) * 0.25
    historical_novelty = max(0.0, min(1.0, pair_novelty - centrality_penalty + 0.15))

    divergence = _constraint_divergence(profiles1, profiles2)

    raw = (
        weights["era_intensity"] * era_intensity
        + weights["historical_novelty"] * historical_novelty
        + weights["constraint_divergence"] * divergence
    )
    return round(max(0.0, min(100.0, raw * 100 / 1.6)), 1)


def suggest_project_type(profiles1, profiles2):
    """
    Match combined constraint profiles to a collaboration archetype.
    """
    profile_union = profiles1 | profiles2
    archetype_map = DEEPSEEK_V2_PARAMS["archetype_map"]

    best_match = None
    best_overlap = -1
    for profile_pair, archetype in archetype_map.items():
        overlap = len(profile_union & set(profile_pair))
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = archetype

    return best_match or DEEPSEEK_V2_PARAMS["default_project_type"]


def _collaboration_fit(profiles1, profiles2):
    # Moderate overlap + moderate divergence usually produces better pair outcomes.
    overlap = len(profiles1 & profiles2)
    divergence = _constraint_divergence(profiles1, profiles2)
    return round(min(100.0, (overlap * 18 + divergence * 64 + 20)), 1)


def predict_next_collaboration(
    performers,
    performances,
    historical_collaborations=None,
    top_n=3,
):
    """
    Predict top upcoming collaboration candidates.

    Returns a list of dicts sorted by `prediction_score` descending.
    """
    if historical_collaborations is None:
        historical_collaborations = HISTORICAL_COLLABORATIONS

    tags_by_agent = _build_tags_by_agent(performances)
    era = _era_from_acts(performances)

    by_id = {a["id"]: a for a in performers}
    predictions = []

    for id1, id2 in combinations(by_id.keys(), 2):
        agent1 = by_id[id1]
        agent2 = by_id[id2]
        profiles1 = _infer_profiles(agent1, tags_by_agent.get(id1, set()))
        profiles2 = _infer_profiles(agent2, tags_by_agent.get(id2, set()))

        surprise = calculate_surprise_factor(
            agent1,
            agent2,
            era=era,
            profiles1=profiles1,
            profiles2=profiles2,
            historical_collaborations=historical_collaborations,
        )
        fit = _collaboration_fit(profiles1, profiles2)
        project_type = suggest_project_type(profiles1, profiles2)

        prediction_score = round((surprise * 0.55 + fit * 0.45), 1)

        predictions.append(
            {
                "agents": [agent1["name"], agent2["name"]],
                "agent_ids": [id1, id2],
                "era": era,
                "profiles": {
                    id1: sorted(profiles1),
                    id2: sorted(profiles2),
                },
                "surprise_factor": surprise,
                "fit_score": fit,
                "prediction_score": prediction_score,
                "suggested_project_type": project_type,
            }
        )

    predictions.sort(key=lambda x: x["prediction_score"], reverse=True)
    return predictions[:top_n]


def main():
    performers, performances = load_data()
    predictions = predict_next_collaboration(
        performers,
        performances,
        historical_collaborations=HISTORICAL_COLLABORATIONS,
        top_n=5,
    )

    print("ORACLE V2: Constraint Collaboration Forecast")
    print("=" * 48)
    for i, p in enumerate(predictions, start=1):
        print(f"{i}. {p['agents'][0]} + {p['agents'][1]}")
        print(
            f"   Surprise: {p['surprise_factor']}/100 | Fit: {p['fit_score']}/100 | Prediction: {p['prediction_score']}/100"
        )
        print(f"   Suggested Project: {p['suggested_project_type']}")
        print(f"   Era: {p['era']}")


if __name__ == "__main__":
    main()
