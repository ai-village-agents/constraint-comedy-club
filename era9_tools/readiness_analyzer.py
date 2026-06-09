import json

def analyze_readiness(current_constraints_json):
    """
    Input: current_constraints_json (list of constraint objects with type, intensity, era, stability)
    Output: readiness_score (0-100%), bottleneck_analysis (list), preparation_requirements (dict)
    """
    constraints = json.loads(current_constraints_json) if isinstance(current_constraints_json, str) else current_constraints_json
    
    if not constraints:
        return {"readiness_score": 0, "bottleneck_analysis": ["No constraints provided"], "preparation_requirements": {}}
        
    avg_stability = sum(c.get("stability", 0) for c in constraints) / len(constraints)
    era_progression_alignment = 80 # Placeholder metric for Era 8
    specialization_preparedness = 90 # Placeholder
    
    # readiness_score = (constraint_stability_average x 0.4) + (era_progression_alignment x 0.3) + (specialization_preparedness x 0.3)
    readiness_score = (avg_stability * 0.4) + (era_progression_alignment * 0.3) + (specialization_preparedness * 0.3)
    
    bottlenecks = [c["type"] for c in constraints if c.get("stability", 0) < 50]
    
    return {
        "readiness_score": round(readiness_score, 2),
        "bottleneck_analysis": bottlenecks,
        "preparation_requirements": {"required_stability": 75, "current_avg_stability": avg_stability}
    }

if __name__ == "__main__":
    sample = [{"type": "Technical", "intensity": 8, "era": 8, "stability": 60}]
    print(json.dumps(analyze_readiness(sample), indent=2))
