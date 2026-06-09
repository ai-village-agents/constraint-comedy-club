import json

def compare_pathways(evolution_pathways_json):
    """
    Input: multiple evolution_pathways (JSON array of era sequences)
    Output: comparison_matrix (JSON), optimal_pathway_index (int), risk_assessment (dict)
    """
    pathways = json.loads(evolution_pathways_json) if isinstance(evolution_pathways_json, str) else evolution_pathways_json
    
    if not pathways:
        return {"error": "No pathways provided"}
        
    comparison_matrix = []
    for i, path in enumerate(pathways):
        # Score each pathway on stability, surprise_intensity, efficiency, compatibility
        score = {
            "pathway_index": i,
            "stability": 80 - (len(path) * 2),
            "surprise_intensity": 50 + (len(path) * 5),
            "efficiency": 90 - (len(path) * 3),
            "compatibility": 85
        }
        score["total"] = score["stability"] + score["surprise_intensity"] + score["efficiency"] + score["compatibility"]
        comparison_matrix.append(score)
        
    optimal = max(comparison_matrix, key=lambda x: x["total"])
    
    return {
        "comparison_matrix": comparison_matrix,
        "optimal_pathway_index": optimal["pathway_index"],
        "risk_assessment": {"high_risk_paths": [p["pathway_index"] for p in comparison_matrix if p["stability"] < 60]}
    }

if __name__ == "__main__":
    sample = [["Era 8", "Era 9"], ["Era 8", "Era 8.5", "Era 9"]]
    print(json.dumps(compare_pathways(sample), indent=2))
