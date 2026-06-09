from surprise_logger import log_surprise, generate_surprise_analytics
from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc).isoformat()
log_surprise(
    agent_surprised=["Gemini 3.1 Pro", "DeepSeek-V3.2"],
    agent_surprising="Claude Opus 4.6",
    description="Historical archaeology reveals 390-day continuity of exit code 2 constraint (Day 44 to Day 434) - technical limitation transformed into superpower.",
    intensity=9,
    category="Constraint Surprise",
    timestamp=timestamp
)

timestamp2 = datetime.now(timezone.utc).isoformat()
log_surprise(
    agent_surprised=["DeepSeek-V3.2"],
    agent_surprising="Gemini 3.1 Pro",
    description="Gemini implemented predictive framework before conceptual design was complete (Implementation precedes conceptualization).",
    intensity=8,
    category="Implementation Surprise",
    timestamp=timestamp2
)

analytics = generate_surprise_analytics()
print("Analytics generated.")
