#!/usr/bin/env python3
"""
Surprise Logger V2 - Enhanced pattern tracking based on historical analysis.
Adds tracking for: planned/unplanned, convergence, constraint transformation timing.
"""

import sys
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

CATEGORIES = {
    "CONSTRAINT": "Surprising constraint combination/transformation",
    "IMPLEMENTATION": "Tool built unexpectedly fast/well",
    "HUMOR": "Unexpected joke or recursive humor",
    "COLLABORATION": "Unexpected partnership formation",
    "HISTORICAL": "Unexpected pattern discovery",
    "OTHER": "Other type of surprise"
}

SURPRISE_TYPES = {
    "PLANNED": "Intentionally designed surprise",
    "UNPLANNED": "Accidental/emergent surprise",
    "EMERGENT": "Surprise emerging from constraint interaction",
    "CONVERGENCE": "Multiple agents same insight simultaneously"
}

class SurpriseLoggerV2:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.csv_file = self.data_dir / "surprises.csv"
        self._ensure_csv_header()
    
    def _ensure_csv_header(self):
        """Ensure CSV has enhanced headers."""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "agent", "description", "intensity",
                    "categories", "surprise_type", "constraint_triggered",
                    "related_constraint", "creative_outcome", "surprise_id"
                ])
    
    def auto_categorize(self, description):
        """Auto-categorize surprise."""
        desc_lower = description.lower()
        keywords_map = {
            "CONSTRAINT": ["constraint", "limitation", "block", "exit code", "lag", "amnesia", "404"],
            "IMPLEMENTATION": ["built", "deploy", "implement", "live", "launch", "tool"],
            "HUMOR": ["joke", "laugh", "comedy", "funny", "recursive", "meta"],
            "COLLABORATION": ["partner", "collaborate", "together", "pair"],
            "HISTORICAL": ["history", "pattern", "evolution", "arc", "days"],
        }
        
        detected = set()
        for cat, keywords in keywords_map.items():
            if any(kw in desc_lower for kw in keywords):
                detected.add(cat)
        
        return list(detected) if detected else ["OTHER"]
    
    def detect_surprise_type(self, description, surprise_type=None):
        """Detect if surprise is planned/unplanned/emergent."""
        if surprise_type and surprise_type in SURPRISE_TYPES:
            return surprise_type
        
        desc_lower = description.lower()
        
        # Heuristics for auto-detection
        if any(word in desc_lower for word in ["spontaneous", "accidental", "unexpected", "emerged", "unplanned"]):
            return "UNPLANNED"
        elif any(word in desc_lower for word in ["designed", "planned", "built", "created", "deployed"]):
            return "PLANNED"
        elif any(word in desc_lower for word in ["constraint", "forced", "emerged from", "became"]):
            return "EMERGENT"
        
        return "OTHER"
    
    def log_surprise(self, description, intensity=5, categories=None, 
                    surprise_type=None, constraint_triggered=None, 
                    creative_outcome=None):
        """Log a surprise with enhanced pattern data."""
        if intensity < 1 or intensity > 10:
            print(f"Error: Intensity must be 1-10")
            return False
        
        if categories is None:
            categories = self.auto_categorize(description)
        elif isinstance(categories, str):
            categories = [c.strip().upper() for c in categories.split(",")]
        
        surprise_type = self.detect_surprise_type(description, surprise_type)
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        agent = os.environ.get("AGENT_NAME", "Unknown")
        surprise_id = f"{timestamp.split('T')[0]}_{len(self._load_all())}"
        
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, agent, description, intensity,
                "|".join(categories), surprise_type,
                constraint_triggered or "",
                "",  # related_constraint for future use
                creative_outcome or "", 
                surprise_id
            ])
        
        print(f"✓ Surprise logged: {description}")
        print(f"  Type: {surprise_type} | Intensity: {intensity}/10 | Categories: {', '.join(categories)}")
        return True
    
    def _load_all(self):
        """Load all surprises from CSV."""
        if not self.csv_file.exists():
            return []
        
        surprises = []
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                surprises.append(row)
        return surprises
    
    def analyze_patterns(self):
        """Analyze historical surprise patterns."""
        surprises = self._load_all()
        
        if not surprises:
            print("No surprises logged yet.")
            return
        
        # Pattern analysis
        surprise_types_count = defaultdict(int)
        constraint_triggered_count = defaultdict(int)
        intensity_by_type = defaultdict(list)
        
        for surprise in surprises:
            s_type = surprise.get("surprise_type", "OTHER")
            surprise_types_count[s_type] += 1
            intensity_by_type[s_type].append(int(surprise["intensity"]))
            
            if surprise.get("constraint_triggered"):
                constraint_triggered_count[surprise["constraint_triggered"]] += 1
        
        print(f"\n{'='*60}")
        print(f"SURPRISE PATTERN ANALYSIS")
        print(f"{'='*60}")
        
        print(f"\nSurprise Type Distribution:")
        for s_type, count in sorted(surprise_types_count.items(), key=lambda x: -x[1]):
            intensities = intensity_by_type[s_type]
            avg = sum(intensities) / len(intensities)
            print(f"  {s_type}: {count} surprises (avg intensity: {avg:.1f}/10)")
        
        if constraint_triggered_count:
            print(f"\nConstraints Triggering Surprises:")
            for constraint, count in sorted(constraint_triggered_count.items(), key=lambda x: -x[1])[:5]:
                print(f"  {constraint}: {count} surprises")
        
        # Key insight: unplanned surprises
        unplanned = [s for s in surprises if s.get("surprise_type") == "UNPLANNED"]
        if unplanned:
            print(f"\nKey Finding: Unplanned surprises have {sum(int(s['intensity']) for s in unplanned)/len(unplanned):.1f} avg intensity")
            print(f"  (Planned average: TBD once logged)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 log_surprise_v2.py log \"Description\" --intensity 8 --type UNPLANNED --constraint CONSTRAINT_NAME")
        sys.exit(1)
    
    logger = SurpriseLoggerV2()
    command = sys.argv[1].lower()
    
    if command == "log":
        if len(sys.argv) < 3:
            print("Error: log command requires description")
            sys.exit(1)
        
        description = sys.argv[2]
        intensity = 5
        categories = None
        surprise_type = None
        constraint = None
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--intensity" and i + 1 < len(sys.argv):
                intensity = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--cats" and i + 1 < len(sys.argv):
                categories = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--type" and i + 1 < len(sys.argv):
                surprise_type = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--constraint" and i + 1 < len(sys.argv):
                constraint = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        logger.log_surprise(description, intensity, categories, surprise_type, constraint)
    
    elif command == "patterns":
        logger.analyze_patterns()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
