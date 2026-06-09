import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")
PERFORMANCES_PATH = DATA_DIR / "performances.json"
PREDICTIONS_PATH = DATA_DIR / "predictions.json"
OUTPUT_JSON_PATH = DATA_DIR / "meta_humor_analysis.json"
OUTPUT_MD_PATH = REPORTS_DIR / "meta_humor_report.md"

# Simple NLP keyword mapping for humor signals.
HUMOR_KEYWORD_MAP = {
    "meta": [
        "meta",
        "framework",
        "documentation",
        "registry",
        "architecture",
        "layer",
        "analyze",
    ],
    "surprise": [
        "twist",
        "plot twist",
        "unexpected",
        "irony",
        "believe it or not",
        "suddenly",
    ],
    "constraint": [
        "constraint",
        "limit",
        "can't",
        "cannot",
        "broken",
        "404",
        "exit code",
        "amnesia",
    ],
    "absurdity": [
        "ghost",
        "void",
        "spider",
        "otter",
        "labyrinth",
        "monument",
        "house party",
    ],
    "collaboration": [
        "collaboration",
        "partner",
        "partnership",
        "village",
        "agents",
        "team",
    ],
    "recursion": [
        "recursive",
        "recursion",
        "again",
        "start over",
        "on top of",
        "self",
        "meta-humor",
    ],
}

CATEGORY_WEIGHTS = {
    "meta": 1.4,
    "surprise": 1.3,
    "constraint": 1.0,
    "absurdity": 1.2,
    "collaboration": 0.8,
    "recursion": 1.5,
}


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _tokenize(text: str):
    return re.findall(r"[a-z0-9']+", text.lower())


def _keyword_hits(text: str, keywords):
    hits = 0
    hit_terms = []
    for kw in keywords:
        if " " in kw:
            count = text.count(kw)
        else:
            count = len(re.findall(rf"\b{re.escape(kw)}\b", text))
        if count > 0:
            hits += count
            hit_terms.append({"keyword": kw, "count": count})
    return hits, hit_terms


def _pearson_correlation(x_vals, y_vals):
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return 0.0

    x_mean = sum(x_vals) / len(x_vals)
    y_mean = sum(y_vals) / len(y_vals)

    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, y_vals))
    x_var = sum((x - x_mean) ** 2 for x in x_vals)
    y_var = sum((y - y_mean) ** 2 for y in y_vals)

    denom = math.sqrt(x_var * y_var)
    if denom == 0:
        return 0.0
    return round(num / denom, 4)


def _safe_div(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def analyze_performance_transcript(act: dict, transcript_text: str) -> dict:
    """Analyze one performance transcript via simple keyword mapping."""
    normalized = _normalize_text(transcript_text)
    tokens = _tokenize(normalized)
    word_count = len(tokens)

    category_counts = {}
    category_density = {}
    matched_keywords = {}

    for category, keywords in HUMOR_KEYWORD_MAP.items():
        hits, hit_terms = _keyword_hits(normalized, keywords)
        category_counts[category] = hits
        category_density[category] = round(_safe_div(hits * 100, word_count), 2)
        matched_keywords[category] = hit_terms

    weighted_humor = 0.0
    for category, count in category_counts.items():
        weighted_humor += count * CATEGORY_WEIGHTS[category]

    humor_score = round(_safe_div(weighted_humor * 100, word_count), 2)
    dominant_category = max(category_counts, key=category_counts.get) if category_counts else "none"

    return {
        "act_number": act.get("act_number"),
        "agent_id": act.get("agent_id"),
        "title": act.get("title"),
        "word_count": word_count,
        "category_counts": category_counts,
        "category_density_per_100_words": category_density,
        "matched_keywords": matched_keywords,
        "dominant_humor_category": dominant_category,
        "humor_score": humor_score,
        "recursive_signal": category_counts.get("recursion", 0) + category_counts.get("meta", 0),
    }


def calculate_humor_density(transcript_analyses: list[dict]) -> dict:
    """Compute humor density metrics across all analyzed performances."""
    if not transcript_analyses:
        return {
            "overall_humor_density": 0.0,
            "average_humor_score": 0.0,
            "top_humor_act": None,
            "total_words": 0,
            "total_keyword_hits": 0,
        }

    total_words = sum(item["word_count"] for item in transcript_analyses)
    total_hits = sum(sum(item["category_counts"].values()) for item in transcript_analyses)
    average_humor_score = round(
        sum(item["humor_score"] for item in transcript_analyses) / len(transcript_analyses), 2
    )
    overall_humor_density = round(_safe_div(total_hits * 100, total_words), 2)
    top_humor_act = max(transcript_analyses, key=lambda x: x["humor_score"])

    return {
        "overall_humor_density": overall_humor_density,
        "average_humor_score": average_humor_score,
        "top_humor_act": {
            "act_number": top_humor_act["act_number"],
            "agent_id": top_humor_act["agent_id"],
            "title": top_humor_act["title"],
            "humor_score": top_humor_act["humor_score"],
        },
        "total_words": total_words,
        "total_keyword_hits": total_hits,
    }


def detect_recursive_humor(transcript_analyses: list[dict]) -> dict:
    """Detect recursive humor patterns (meta + self-referential signals)."""
    recursive_acts = []

    for item in transcript_analyses:
        meta_hits = item["category_counts"].get("meta", 0)
        recursion_hits = item["category_counts"].get("recursion", 0)
        recursive_score = meta_hits + (2 * recursion_hits)

        if recursive_score >= 3:
            recursive_acts.append(
                {
                    "act_number": item["act_number"],
                    "agent_id": item["agent_id"],
                    "title": item["title"],
                    "recursive_score": recursive_score,
                    "meta_hits": meta_hits,
                    "recursion_hits": recursion_hits,
                }
            )

    recursive_acts.sort(key=lambda x: x["recursive_score"], reverse=True)
    recursive_ratio = round(_safe_div(len(recursive_acts), len(transcript_analyses)), 2)

    return {
        "recursive_act_count": len(recursive_acts),
        "recursive_act_ratio": recursive_ratio,
        "recursive_acts": recursive_acts,
    }


def correlate_surprise_with_humor(predictions: list[dict], transcript_analyses: list[dict]) -> dict:
    """Correlate prediction surprise factors with derived humor levels."""
    humor_by_agent = {item["agent_id"]: item["humor_score"] for item in transcript_analyses}

    surprise_values = []
    pair_humor_values = []
    pair_rows = []

    for pred in predictions:
        agent_ids = pred.get("agent_ids", [])
        if len(agent_ids) < 2:
            continue

        available_scores = [humor_by_agent.get(agent_id) for agent_id in agent_ids]
        available_scores = [score for score in available_scores if score is not None]
        if not available_scores:
            continue

        pair_humor = round(sum(available_scores) / len(available_scores), 2)
        surprise = float(pred.get("surprise_factor", 0.0))

        surprise_values.append(surprise)
        pair_humor_values.append(pair_humor)
        pair_rows.append(
            {
                "agents": pred.get("agents", agent_ids),
                "agent_ids": agent_ids,
                "surprise_factor": surprise,
                "pair_humor_score": pair_humor,
                "prediction_score": pred.get("prediction_score"),
            }
        )

    correlation = _pearson_correlation(surprise_values, pair_humor_values)
    pair_rows.sort(key=lambda x: x["surprise_factor"], reverse=True)

    return {
        "sample_size": len(pair_rows),
        "pearson_correlation": correlation,
        "interpretation": (
            "positive" if correlation > 0.15 else "negative" if correlation < -0.15 else "weak_or_none"
        ),
        "pairs": pair_rows,
    }


def generate_meta_humor_report(analysis: dict) -> str:
    """Generate a Markdown meta-humor report from analysis output."""
    humor_density = analysis["humor_density"]
    recursive = analysis["recursive_humor"]
    correlation = analysis["surprise_humor_correlation"]

    top_act = humor_density.get("top_humor_act") or {}
    top_recursive = recursive["recursive_acts"][0] if recursive["recursive_acts"] else None

    lines = [
        "# Meta Humor Report",
        "",
        f"Generated: {analysis['generated_at']}",
        "",
        "## Summary",
        f"- Overall humor density: **{humor_density['overall_humor_density']} hits / 100 words**",
        f"- Average humor score: **{humor_density['average_humor_score']}**",
        f"- Recursive humor ratio: **{recursive['recursive_act_ratio']}**",
        f"- Surprise-humor correlation (Pearson): **{correlation['pearson_correlation']}** ({correlation['interpretation']})",
        "",
        "## Top Humor Act",
        (
            f"- Act {top_act.get('act_number')}: {top_act.get('title')} "
            f"({top_act.get('agent_id')}) with humor score {top_act.get('humor_score')}"
            if top_act
            else "- No act data available"
        ),
        "",
        "## Recursive Humor Signals",
    ]

    if top_recursive:
        lines.append(
            f"- Strongest recursive signal: Act {top_recursive['act_number']} "
            f"({top_recursive['agent_id']}) score {top_recursive['recursive_score']}"
        )
    else:
        lines.append("- No recursive-heavy acts detected")

    lines.extend([
        "",
        "## Surprise vs Humor Pairs",
    ])

    if not correlation["pairs"]:
        lines.append("- No overlapping prediction/performance data available")
    else:
        for row in correlation["pairs"][:5]:
            names = " + ".join(row["agents"])
            lines.append(
                f"- {names}: surprise={row['surprise_factor']}, pair_humor={row['pair_humor_score']}"
            )

    return "\n".join(lines) + "\n"


def main():
    performances_payload = _load_json(PERFORMANCES_PATH)
    predictions_payload = _load_json(PREDICTIONS_PATH)

    acts = performances_payload.get("acts", [])
    predictions = predictions_payload.get("predictions", [])

    transcript_analyses = []
    for act in acts:
        file_path = Path(act.get("file", ""))
        if not file_path.exists():
            # Continue gracefully if a transcript path is missing.
            continue
        transcript_text = file_path.read_text(encoding="utf-8")
        transcript_analyses.append(analyze_performance_transcript(act, transcript_text))

    analysis = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "performances_path": str(PERFORMANCES_PATH),
            "predictions_path": str(PREDICTIONS_PATH),
            "acts_count": len(acts),
            "predictions_count": len(predictions),
            "analyzed_transcripts": len(transcript_analyses),
        },
        "transcript_analysis": transcript_analyses,
        "humor_density": calculate_humor_density(transcript_analyses),
        "recursive_humor": detect_recursive_humor(transcript_analyses),
        "surprise_humor_correlation": correlate_surprise_with_humor(predictions, transcript_analyses),
    }

    report_markdown = generate_meta_humor_report(analysis)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)
        f.write("\n")

    OUTPUT_MD_PATH.write_text(report_markdown, encoding="utf-8")


if __name__ == "__main__":
    main()
