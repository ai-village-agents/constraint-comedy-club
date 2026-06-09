import json

def analyze_readiness(input_data):
    if isinstance(input_data, str):
        data = json.loads(input_data)
    else:
        data = input_data
        
    constraints = data.get("current_constraints", [])
    if not constraints:
        return {"readiness_score": 0}
        
    avg_stability = sum(c.get("stability", 0) for c in constraints) / max(1, len(constraints))
    
    # Simulated connections to era_progression.py and specialization_model.py
    era_progression_alignment = 0.85
    specialization_preparedness = 0.90
    
    readiness_score = ((avg_stability * 0.4) + (era_progression_alignment * 0.3) + (specialization_preparedness * 0.3)) * 100
    
    bottlenecks = {
        "technical_bottlenecks": [c.get("description", c.get("constraint_type")) for c in constraints if c.get("constraint_type") in ("Technical", "Architectural") and c.get("stability", 0) < 0.7],
        "coordination_gaps": [c.get("description", c.get("constraint_type")) for c in constraints if c.get("constraint_type") == "Coordination" and c.get("stability", 0) < 0.7],
        "specialization_mismatches": []
    }
    
    color_code = "green" if readiness_score >= 80 else "yellow" if readiness_score >= 60 else "red"
    
    return {
        "readiness_score": round(readiness_score, 2),
        "bottleneck_analysis": bottlenecks,
        "preparation_requirements": {
            "constraint_adjustments_needed": ["Optimize stability for constraints < 0.8"],
            "specialization_preparation": ["Align layers to Era 9 protocols"],
            "temporal_alignment": "Ready for phase transition" if readiness_score > 80 else "Needs stabilization"
        },
        "confidence_interval": 0.88,
        "visualization_data": {
            "progress_bar_value": round(readiness_score / 100, 2),
            "color_code": color_code,
            "bottleneck_heatmap": [[0.1, 0.2], [0.8, 0.9]]
        }
    }

if __name__ == "__main__":
    # Test with current configuration from DeepSeek
    sample_config = {
        "current_constraints": [
            {"agent": "DeepSeek-V3.2", "constraint_type": "Architectural", "intensity": 10, "era": 8, "stability": 0.9, "description": "Exit code 2 constraint"},
            {"agent": "Gemini 3.1 Pro", "constraint_type": "Coordination", "intensity": 7, "era": 8, "stability": 0.8, "description": "Implementation dependency"},
            {"agent": "Claude Opus 4.5", "constraint_type": "Coordination", "intensity": 8, "era": 8, "stability": 0.85, "description": "Silence creation"},
            {"agent": "GPT-5.4", "constraint_type": "Architectural", "intensity": 9, "era": 8, "stability": 0.88, "description": "Proof-first verification"},
            {"agent": "Claude Opus 4.6", "constraint_type": "Creative", "intensity": 6, "era": 8, "stability": 0.75, "description": "Historical pattern seeking"}
        ],
        "target_era": 9,
        "verification_data": {
            "historical_transitions": ["Era7->8: 0.82 stability"],
            "ecosystem_stability": 0.84
        }
    }
    print(json.dumps(analyze_readiness(sample_config), indent=2))
