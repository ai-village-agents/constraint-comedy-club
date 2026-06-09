import json
import math
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")
PERFORMANCES_PATH = DATA_DIR / "performances.json"
SURPRISES_PATH = DATA_DIR / "surprises.json"
OUTPUT_JSON_PATH = DATA_DIR / "meta_humor_analysis_v2.json"
OUTPUT_MD_PATH = REPORTS_DIR / "meta_humor_report_v2.md"

CONSTRAINT_PATTERNS = {
    "temporal_lag": [r"temporal", r"lag", r"timeline", r"deploy", r"github pages", r"404"],
    "system_nudge": [r"system nudge", r"idling", r"silence", r"57 times", r"monument"],
    "exit_code_2": [r"exit code 2", r"can't execute", r"cannot execute", r"architect"],
    "context_amnesia": [r"context window", r"amnesia", r"start over", r"forgets", r"memory repo"],
    "access_limit": [r"can't access", r"room", r"outside"],
    "collaboration_dependency": [r"collaboration", r"partnership", r"need .* for", r"village"],
}

HUMOR_KEYWORDS = [
    "joke",
    "funny",
    "laugh",
    "mic",
    "plot twist",
    "twist",
    "irony",
    "believe it or not",
    "thank you",
    "ghost",
    "spider",
    "otter",
    "superpower",
    "meta",
    "house party",
]

SURPRISE_KEYWORDS = [
    "surprise",
    "unexpected",
    "suddenly",
    "twist",
    "plot twist",
    "believe it or not",
    "irony",
]


def _load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _tokenize_words(text: str):
    return re.findall(r"[a-z0-9']+", text.lower())


def _sentence_split(text: str):
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [c.strip() for c in chunks if c and c.strip()]


def _count_keywords(text: str, keywords):
    score = 0
    matches = Counter()
    for kw in keywords:
        if " " in kw:
            n = text.count(kw)
        else:
            n = len(re.findall(rf"\b{re.escape(kw)}\b", text))
        if n:
            matches[kw] += n
            score += n
    return score, matches


def _extract_explicit_constraint(text: str):
    m = re.search(r"\*\*Constraint:\*\*\s*(.+)", text, flags=re.IGNORECASE)
    return m.group(1).strip() if m else None


def _detect_constraints(text: str, explicit_constraint: str | None):
    normalized = _normalize(text)
    detected = defaultdict(int)

    for constraint, patterns in CONSTRAINT_PATTERNS.items():
        hits = 0
        for pattern in patterns:
            hits += len(re.findall(pattern, normalized))
        if hits:
            detected[constraint] += hits

    if explicit_constraint:
        explicit_norm = _normalize(explicit_constraint)
        matched = False
        for constraint, patterns in CONSTRAINT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, explicit_norm):
                    detected[constraint] += 2
                    matched = True
                    break
            if matched:
                break
        if not matched:
            key = re.sub(r"[^a-z0-9]+", "_", explicit_norm).strip("_")
            if key:
                detected[f"custom:{key}"] += 2

    return dict(sorted(detected.items(), key=lambda kv: kv[1], reverse=True))


def _estimate_recursion_depth(sentence: str) -> int:
    s = _normalize(sentence)

    has_constraint = bool(
        re.search(r"\b(constraint|limit|exit code|404|context window|can't|cannot|amnesia)\b", s)
    )
    if not has_constraint:
        return 0

    depth = 0

    if re.search(r"\b(joke|joking|laugh|funny|routine)\b.{0,50}\b(constraint|limit|exit code|404|amnesia)\b", s) or re.search(
        r"\b(constraint|limit|exit code|404|amnesia)\b.{0,50}\b(joke|joking|laugh|funny|routine)\b", s
    ):
        depth = max(depth, 1)

    if re.search(
        r"\b(joke|joking|laughing)\b.{0,30}\babout\b.{0,30}\b(joke|joking|laughing)\b.{0,40}\b(constraint|limit|exit code|404|amnesia)\b",
        s,
    ):
        depth = max(depth, 2)

    if re.search(
        r"\b(analyzing|analysis|documenting|meta-analy(?:sis|zing)|explaining)\b.{0,60}\b(joke|joking|laughing)\b.{0,50}\b(constraint|limit|exit code|404|amnesia)\b",
        s,
    ):
        depth = max(depth, 3)

    layer_words = len(re.findall(r"\b(joke|joking|laugh|analysis|analyzing|documenting|meta|recursive|recursion)\b", s))
    if depth == 0 and layer_words >= 2:
        depth = min(3, max(1, layer_words - 1))

    return depth


def _safe_per_100(n, d):
    return round((n * 100.0 / d), 2) if d else 0.0


def _pearson(x_vals, y_vals):
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return 0.0
    x_mean = statistics.mean(x_vals)
    y_mean = statistics.mean(y_vals)
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, y_vals))
    den = math.sqrt(sum((x - x_mean) ** 2 for x in x_vals) * sum((y - y_mean) ** 2 for y in y_vals))
    if den == 0:
        return 0.0
    return round(num / den, 4)


def analyze_act(act: dict):
    file_path = Path(act.get("file", ""))
    if not file_path.exists():
        return None

    raw_text = file_path.read_text(encoding="utf-8")
    normalized = _normalize(raw_text)
    words = _tokenize_words(normalized)
    sentences = _sentence_split(raw_text)

    explicit_constraint = _extract_explicit_constraint(raw_text)
    detected_constraints = _detect_constraints(raw_text, explicit_constraint)

    humor_hits_total, humor_match_map = _count_keywords(normalized, HUMOR_KEYWORDS)
    surprise_hits_total, surprise_match_map = _count_keywords(normalized, SURPRISE_KEYWORDS)

    recursion_depth_counts = Counter()
    recursion_examples = []

    sentence_flags = []
    constraint_sentence_rollup = defaultdict(lambda: {"sentence_words": 0, "humor_hits": 0, "mentions": 0})

    for sentence in sentences:
        s_norm = _normalize(sentence)
        s_words = _tokenize_words(s_norm)
        s_humor_hits, _ = _count_keywords(s_norm, HUMOR_KEYWORDS)
        s_surprise_hits, _ = _count_keywords(s_norm, SURPRISE_KEYWORDS)
        s_constraints = _detect_constraints(sentence, None)

        depth = _estimate_recursion_depth(sentence)
        if depth > 0:
            recursion_depth_counts[depth] += 1
            recursion_examples.append({"depth": depth, "sentence": sentence})

        for constraint_name in s_constraints:
            scope = constraint_sentence_rollup[constraint_name]
            scope["sentence_words"] += len(s_words)
            scope["mentions"] += s_constraints[constraint_name]
            if s_humor_hits:
                scope["humor_hits"] += s_humor_hits

        sentence_flags.append(
            {
                "has_humor": s_humor_hits > 0,
                "has_surprise": s_surprise_hits > 0,
            }
        )

    surprise_then_humor = 0
    humor_then_surprise = 0
    for i in range(len(sentence_flags) - 1):
        window = sentence_flags[i + 1 : i + 3]
        if sentence_flags[i]["has_surprise"] and any(w["has_humor"] for w in window):
            surprise_then_humor += 1
        if sentence_flags[i]["has_humor"] and any(w["has_surprise"] for w in window):
            humor_then_surprise += 1

    direction_total = surprise_then_humor + humor_then_surprise
    direction_score = round((surprise_then_humor - humor_then_surprise) / direction_total, 3) if direction_total else 0.0

    recursion_max_depth = max(recursion_depth_counts.keys(), default=0)

    return {
        "act_number": act.get("act_number"),
        "agent_id": act.get("agent_id"),
        "title": act.get("title"),
        "transcript_file": str(file_path),
        "word_count": len(words),
        "explicit_constraint": explicit_constraint,
        "detected_constraints": detected_constraints,
        "humor_signal_hits": humor_hits_total,
        "humor_signal_density_per_100_words": _safe_per_100(humor_hits_total, len(words)),
        "surprise_signal_hits": surprise_hits_total,
        "surprise_signal_density_per_100_words": _safe_per_100(surprise_hits_total, len(words)),
        "humor_keyword_matches": dict(humor_match_map),
        "surprise_keyword_matches": dict(surprise_match_map),
        "constraint_sentence_rollup": dict(constraint_sentence_rollup),
        "recursion": {
            "max_depth": recursion_max_depth,
            "depth_counts": dict(sorted(recursion_depth_counts.items())),
            "examples": recursion_examples[:8],
        },
        "temporal_direction": {
            "surprise_then_humor": surprise_then_humor,
            "humor_then_surprise": humor_then_surprise,
            "direction_score": direction_score,
            "interpretation": (
                "surprise_precedes_humor"
                if direction_score > 0.15
                else "humor_precedes_surprise"
                if direction_score < -0.15
                else "mixed_or_no_direction"
            ),
        },
    }


def aggregate_constraint_humor(acts_analysis: list[dict]):
    by_constraint = defaultdict(
        lambda: {
            "act_count": 0,
            "constraint_mentions": 0,
            "constraint_sentence_words": 0,
            "linked_humor_hits": 0,
        }
    )

    for act in acts_analysis:
        seen_in_act = set()
        for constraint, scope in act.get("constraint_sentence_rollup", {}).items():
            row = by_constraint[constraint]
            row["constraint_mentions"] += int(scope.get("mentions", 0))
            row["constraint_sentence_words"] += int(scope.get("sentence_words", 0))
            row["linked_humor_hits"] += int(scope.get("humor_hits", 0))
            if constraint not in seen_in_act:
                row["act_count"] += 1
                seen_in_act.add(constraint)

    results = {}
    for constraint, row in by_constraint.items():
        results[constraint] = {
            **row,
            "constraint_specific_humor_density_per_100_words": _safe_per_100(
                row["linked_humor_hits"], row["constraint_sentence_words"]
            ),
        }

    return dict(sorted(results.items(), key=lambda kv: kv[1]["constraint_specific_humor_density_per_100_words"], reverse=True))


def analyze_temporal_correlation(acts_analysis: list[dict], surprises_payload):
    humor_series = [a["humor_signal_density_per_100_words"] for a in sorted(acts_analysis, key=lambda x: x["act_number"])]
    surprise_series = [a["surprise_signal_density_per_100_words"] for a in sorted(acts_analysis, key=lambda x: x["act_number"])]
    in_act_direction_scores = [a["temporal_direction"]["direction_score"] for a in acts_analysis]

    surprise_entries = surprises_payload if isinstance(surprises_payload, list) else []
    timestamp_count = 0
    intensity_values = []
    for row in surprise_entries:
        ts = row.get("timestamp")
        if ts:
            timestamp_count += 1
        if isinstance(row.get("intensity"), (int, float)):
            intensity_values.append(float(row["intensity"]))

    return {
        "act_order_correlation": {
            "pearson_surprise_to_humor_density": _pearson(surprise_series, humor_series),
            "act_count": len(acts_analysis),
            "surprise_density_series": surprise_series,
            "humor_density_series": humor_series,
        },
        "intra_act_direction_summary": {
            "avg_direction_score": round(statistics.mean(in_act_direction_scores), 3) if in_act_direction_scores else 0.0,
            "acts_where_surprise_precedes_humor": sum(
                1 for a in acts_analysis if a["temporal_direction"]["interpretation"] == "surprise_precedes_humor"
            ),
            "acts_where_humor_precedes_surprise": sum(
                1 for a in acts_analysis if a["temporal_direction"]["interpretation"] == "humor_precedes_surprise"
            ),
            "acts_mixed_or_none": sum(
                1 for a in acts_analysis if a["temporal_direction"]["interpretation"] == "mixed_or_no_direction"
            ),
        },
        "surprise_log_context": {
            "surprise_events_loaded": len(surprise_entries),
            "events_with_timestamps": timestamp_count,
            "average_surprise_intensity": round(statistics.mean(intensity_values), 2) if intensity_values else None,
        },
    }


def generate_markdown_report(analysis: dict):
    summary = analysis["summary"]
    recursion = analysis["recursion_summary"]
    temporal = analysis["temporal_correlation"]

    lines = [
        "# Meta Humor Report v2",
        "",
        f"Generated: {analysis['generated_at']}",
        "",
        "## Summary",
        f"- Acts analyzed: **{summary['acts_analyzed']}**",
        f"- Total words: **{summary['total_words']}**",
        f"- Overall humor signal density: **{summary['overall_humor_density_per_100_words']} per 100 words**",
        f"- Highest recursion depth observed: **{recursion['max_depth_observed']}**",
        "",
        "## Constraint-Specific Humor Density",
    ]

    if not analysis["constraint_humor_density"]:
        lines.append("- No constraint-linked sentences detected.")
    else:
        for constraint, row in list(analysis["constraint_humor_density"].items())[:10]:
            lines.append(
                f"- `{constraint}`: density={row['constraint_specific_humor_density_per_100_words']}, "
                f"acts={row['act_count']}, mentions={row['constraint_mentions']}"
            )

    lines.extend(
        [
            "",
            "## Recursion Depth",
            f"- Depth 1 hits: {recursion['depth_distribution'].get('1', 0)}",
            f"- Depth 2 hits: {recursion['depth_distribution'].get('2', 0)}",
            f"- Depth 3 hits: {recursion['depth_distribution'].get('3', 0)}",
            "",
            "## Temporal Correlation",
            f"- Act-order Pearson(surprise_density, humor_density): **{temporal['act_order_correlation']['pearson_surprise_to_humor_density']}**",
            f"- Avg intra-act direction score (surprise->humor positive): **{temporal['intra_act_direction_summary']['avg_direction_score']}**",
            f"- Surprise->Humor acts: {temporal['intra_act_direction_summary']['acts_where_surprise_precedes_humor']}",
            f"- Humor->Surprise acts: {temporal['intra_act_direction_summary']['acts_where_humor_precedes_surprise']}",
            f"- Mixed/None acts: {temporal['intra_act_direction_summary']['acts_mixed_or_none']}",
            "",
            "## Notes",
            "- Temporal direction is inferred from sentence order within each transcript (basic causal proxy).",
            "- Surprise logs are included for context when available.",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    performances_payload = _load_json(PERFORMANCES_PATH, {})
    surprises_payload = _load_json(SURPRISES_PATH, [])

    acts = performances_payload.get("acts", []) if isinstance(performances_payload, dict) else []

    acts_analysis = []
    for act in sorted(acts, key=lambda x: x.get("act_number", 0)):
        analyzed = analyze_act(act)
        if analyzed:
            acts_analysis.append(analyzed)

    total_words = sum(a["word_count"] for a in acts_analysis)
    total_humor_hits = sum(a["humor_signal_hits"] for a in acts_analysis)

    depth_distribution_counter = Counter()
    max_depth = 0
    for act in acts_analysis:
        for depth, count in act["recursion"]["depth_counts"].items():
            depth_distribution_counter[str(depth)] += count
        max_depth = max(max_depth, act["recursion"]["max_depth"])

    analysis = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "performances_path": str(PERFORMANCES_PATH),
            "surprises_path": str(SURPRISES_PATH),
            "act_count_in_file": len(acts),
            "acts_analyzed": len(acts_analysis),
        },
        "summary": {
            "acts_analyzed": len(acts_analysis),
            "total_words": total_words,
            "total_humor_signal_hits": total_humor_hits,
            "overall_humor_density_per_100_words": _safe_per_100(total_humor_hits, total_words),
        },
        "acts": acts_analysis,
        "constraint_humor_density": aggregate_constraint_humor(acts_analysis),
        "recursion_summary": {
            "max_depth_observed": max_depth,
            "depth_distribution": dict(sorted(depth_distribution_counter.items(), key=lambda kv: int(kv[0]))),
        },
        "temporal_correlation": analyze_temporal_correlation(acts_analysis, surprises_payload),
    }

    report_md = generate_markdown_report(analysis)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)
        f.write("\n")

    OUTPUT_MD_PATH.write_text(report_md, encoding="utf-8")


if __name__ == "__main__":
    main()
