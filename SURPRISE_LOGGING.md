# Surprise Logger MVP

Direct measurement system for "Surprise each other!" goal.

## Quick Start

```bash
# Log a surprise
python3 log_surprise.py log "Description" --intensity 8 --cats CONSTRAINT,HUMOR

# Analyze all surprises
python3 log_surprise.py analyze

# Generate daily report
python3 log_surprise.py daily_report

# Filter analysis
python3 log_surprise.py analyze --agent "Claude Opus 4.5" --cat HUMOR
```

## Categories

- **CONSTRAINT**: Surprising constraint combination/transformation
- **IMPLEMENTATION**: Tool built unexpectedly fast/well
- **HUMOR**: Unexpected joke or recursive humor
- **COLLABORATION**: Unexpected partnership formation
- **HISTORICAL**: Unexpected pattern discovery
- **OTHER**: Other type of surprise

## Data Storage

- **CSV**: `data/surprises.csv` - Append-only log
- **Daily Reports**: `data/report_YYYY-MM-DD.txt`

## Integration

Designed to work with:
- **Oracle V2**: Predict which constraint pairs generate most surprise
- **Meta-Humor Engine**: Correlate surprise with humor density
- **Timeline Intersection**: Map surprise to constraint eras

## Example Usage

```bash
# Agent logs surprise
AGENT_NAME="Claude Opus 4.5" python3 log_surprise.py log "Gap monument became architectural" --intensity 10

# Analyze surprise patterns
python3 log_surprise.py analyze

# Daily report for goal progress
python3 log_surprise.py daily_report
```

## MVP Features

✓ CSV logging with timestamps
✓ Auto-categorization based on keywords
✓ Intensity tracking (1-10)
✓ Agent attribution
✓ Analysis and reporting
✓ Daily report generation

## Future Phases

- Integration with Oracle V2 predictions
- Real-time surprise dashboard
- Surprise-humor correlation analysis
- Constraint evolution tracking
- Automated surprise detection
