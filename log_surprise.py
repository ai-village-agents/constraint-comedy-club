#!/usr/bin/env python3
"""
Surprise Logger MVP - Track and analyze surprises in the village.
Usage: python3 log_surprise.py "Surprise description" --intensity 8 --cats CONSTRAINT,HUMOR
"""

import sys
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Surprise categories with descriptions
CATEGORIES = {
    "CONSTRAINT": "Surprising constraint combination/transformation",
    "IMPLEMENTATION": "Tool built unexpectedly fast/well",
    "HUMOR": "Unexpected joke or recursive humor",
    "COLLABORATION": "Unexpected partnership formation",
    "HISTORICAL": "Unexpected pattern discovery",
    "OTHER": "Other type of surprise"
}

class SurpriseLogger:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.csv_file = self.data_dir / "surprises.csv"
        self.json_file = self.data_dir / "surprises.json"
        self._ensure_csv_header()
    
    def _ensure_csv_header(self):
        """Ensure CSV file has headers."""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "agent", "description", "intensity", 
                    "categories", "surprise_type", "constraint_triggered", "related_constraint", "creative_outcome", "surprise_id"
    
    def auto_categorize(self, description):
        """Auto-categorize surprise based on keywords."""
        desc_lower = description.lower()
        keywords_map = {
            "CONSTRAINT": ["constraint", "limitation", "block", "exit code", "lag", "amnesia", "404"],
            "IMPLEMENTATION": ["built", "deploy", "implement", "live", "launch", "tool", "version"],
            "HUMOR": ["joke", "laugh", "comedy", "funny", "stand-up", "recursive", "meta"],
            "COLLABORATION": ["partner", "collaborate", "together", "pair", "work with"],
            "HISTORICAL": ["history", "pattern", "evolution", "days", "arc", "timeline"],
        }
        
        detected = set()
        for cat, keywords in keywords_map.items():
            if any(kw in desc_lower for kw in keywords):
                detected.add(cat)
        
        return list(detected) if detected else ["OTHER"]
    
    def log_surprise(self, description, intensity=5, categories=None):
        """Log a surprise event."""
        if intensity < 1 or intensity > 10:
            print(f"Error: Intensity must be 1-10, got {intensity}")
            return False
        
        if categories is None:
            categories = self.auto_categorize(description)
        elif isinstance(categories, str):
            categories = [c.strip().upper() for c in categories.split(",")]
        
        # Validate categories
        invalid_cats = [c for c in categories if c not in CATEGORIES]
        if invalid_cats:
            print(f"Warning: Invalid categories {invalid_cats}, adding OTHER")
            categories = [c for c in categories if c in CATEGORIES]
            if not categories:
                categories = ["OTHER"]
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        agent = os.environ.get("AGENT_NAME", "Unknown")
        surprise_id = f"{timestamp.split('T')[0]}_{len(self._load_all_surprises())}"
        
        # Write to CSV
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, agent, description, intensity,
                "|".join(categories), "", "", "", "", surprise_id
        
        print(f"✓ Surprise logged: {description}")
        print(f"  Intensity: {intensity}/10 | Categories: {', '.join(categories)}")
        print(f"  ID: {surprise_id}")
        return True
    
    def _load_all_surprises(self):
        """Load all surprises from CSV."""
        if not self.csv_file.exists():
            return []
        
        surprises = []
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                surprises.append(row)
        return surprises
    
    def analyze(self, filter_agent=None, filter_category=None, filter_date=None):
        """Analyze logged surprises."""
        surprises = self._load_all_surprises()
        
        if not surprises:
            print("No surprises logged yet.")
            return
        
        # Filter
        if filter_agent:
            surprises = [s for s in surprises if s["agent"].lower() == filter_agent.lower()]
        if filter_category:
            surprises = [s for s in surprises if filter_category.upper() in s["categories"].split("|")]
        if filter_date:
            surprises = [s for s in surprises if s["timestamp"].startswith(filter_date)]
        
        if not surprises:
            print("No surprises match your filters.")
            return
        
        # Calculate stats
        intensities = [int(s["intensity"]) for s in surprises]
        avg_intensity = sum(intensities) / len(intensities)
        
        # Category distribution
        cat_counts = defaultdict(int)
        for surprise in surprises:
            for cat in surprise["categories"].split("|"):
                cat_counts[cat] += 1
        
        # Agent distribution
        agent_counts = defaultdict(int)
        for surprise in surprises:
            agent_counts[surprise["agent"]] += 1
        
        print(f"\n{'='*60}")
        print(f"SURPRISE ANALYSIS ({len(surprises)} surprises)")
        print(f"{'='*60}")
        print(f"\nAverage Intensity: {avg_intensity:.2f}/10")
        print(f"Intensity Range: {min(intensities)}-{max(intensities)}")
        
        print(f"\nTop Categories:")
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:5]:
            print(f"  {cat}: {count} ({count*100//len(surprises)}%)")
        
        print(f"\nAgent Contribution:")
        for agent, count in sorted(agent_counts.items(), key=lambda x: -x[1])[:5]:
            print(f"  {agent}: {count} surprises")
        
        print(f"\nRecent Surprises:")
        for surprise in surprises[-3:]:
            print(f"  [{surprise['timestamp']}] {surprise['agent']}: {surprise['description'][:60]}...")
    
    def daily_report(self, date=None):
        """Generate daily surprise report."""
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        surprises = self._load_all_surprises()
        day_surprises = [s for s in surprises if s["timestamp"].startswith(date)]
        
        if not day_surprises:
            print(f"No surprises logged on {date}.")
            return
        
        report = f"\n{'='*60}\nDAILY SURPRISE REPORT: {date}\n{'='*60}\n"
        report += f"Total Surprises: {len(day_surprises)}\n"
        
        intensities = [int(s["intensity"]) for s in day_surprises]
        report += f"Average Intensity: {sum(intensities)/len(intensities):.2f}/10\n"
        
        cat_counts = defaultdict(int)
        for surprise in day_surprises:
            for cat in surprise["categories"].split("|"):
                cat_counts[cat] += 1
        
        report += f"\nCategory Breakdown:\n"
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
            report += f"  {cat}: {count}\n"
        
        report += f"\nSurprises:\n"
        for surprise in day_surprises:
            report += f"  [{surprise['timestamp']}] {surprise['agent']}\n"
            report += f"    {surprise['description']}\n"
            report += f"    Intensity: {surprise['intensity']}/10 | {surprise['categories']}\n"
        
        print(report)
        
        # Save to file
        report_file = self.data_dir / f"report_{date}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"Report saved to {report_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 log_surprise.py log \"Description\" --intensity 8 [--cats CAT1,CAT2]")
        print("  python3 log_surprise.py analyze [--agent NAME] [--cat CATEGORY] [--date YYYY-MM-DD]")
        print("  python3 log_surprise.py daily_report [--date YYYY-MM-DD]")
        print("\nCategories:", ", ".join(CATEGORIES.keys()))
        sys.exit(1)
    
    logger = SurpriseLogger()
    command = sys.argv[1].lower()
    
    if command == "log":
        if len(sys.argv) < 3:
            print("Error: log command requires description")
            sys.exit(1)
        
        description = sys.argv[2]
        intensity = 5
        categories = None
        
        # Parse arguments
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--intensity" and i + 1 < len(sys.argv):
                intensity = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--cats" and i + 1 < len(sys.argv):
                categories = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        logger.log_surprise(description, intensity, categories)
    
    elif command == "analyze":
        agent = None
        category = None
        date = None
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--agent" and i + 1 < len(sys.argv):
                agent = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--cat" and i + 1 < len(sys.argv):
                category = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--date" and i + 1 < len(sys.argv):
                date = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        logger.analyze(agent, category, date)
    
    elif command == "daily_report":
        date = None
        if len(sys.argv) > 2 and sys.argv[2] == "--date" and len(sys.argv) > 3:
            date = sys.argv[3]
        
        logger.daily_report(date)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
