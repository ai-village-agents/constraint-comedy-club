import json

def compare_pathways(input_data):
    if isinstance(input_data, str):
        data = json.loads(input_data)
    else:
        data = input_data
        
    pathways = data.get("evolution_pathways", [])
    weights = data.get("evaluation_criteria", {
        "stability_weight": 0.3,
        "surprise_potential_weight": 0.3,
        "collaboration_efficiency_weight": 0.2,
        "recursive_validation_weight": 0.2
    })
    
    comparison_matrix = {"pathways": []}
    
    optimal_index = 0
    max_score = 0
    
    for i, p in enumerate(pathways):
        # Simulated scoring based on input parameters and constraints
        stability = sum(c.get("stability_prediction", 0.5) for c in p.get("constraint_transformations", [])) / max(1, len(p.get("constraint_transformations", [])))
        surprise = 0.85 # Base surprise
        efficiency = 0.90 # Base efficiency
        validation = 0.88 # Base validation
        
        composite = (stability * weights.get("stability_weight", 0) +
                     surprise * weights.get("surprise_potential_weight", 0) +
                     efficiency * weights.get("collaboration_efficiency_weight", 0) +
                     validation * weights.get("recursive_validation_weight", 0)) * 100
                     
        comparison_matrix["pathways"].append({
            "pathway_id": p.get("pathway_id", f"pathway_{i}"),
            "stability_score": round(stability * 100, 2),
            "surprise_score": round(surprise * 100, 2),
            "efficiency_score": round(efficiency * 100, 2),
            "validation_score": round(validation * 100, 2),
            "composite_score": round(composite, 2)
        })
        
        if composite > max_score:
            max_score = composite
            optimal_index = i
            
    return {
        "comparison_matrix": comparison_matrix,
        "optimal_pathway_index": optimal_index,
        "risk_assessment": {
            "high_risk_transitions": [],
            "stability_concerns": ["Era transition lag possibility"],
            "validation_uncertainties": ["Divergence in raw vs UI representation"]
        },
        "visualization_data": {
            "parallel_coordinates_data": [p["composite_score"] for p in comparison_matrix["pathways"]],
            "radar_chart_data": [
                [p["stability_score"], p["surprise_score"], p["efficiency_score"], p["validation_score"]] 
                for p in comparison_matrix["pathways"]
            ],
            "optimal_pathway_highlight": [i == optimal_index for i in range(len(pathways))]
        }
    }

if __name__ == "__main__":
    sample_input = {
        "evolution_pathways": [
            {
                "pathway_id": "pathway_alpha",
                "era_sequence": ["Era8", "Era9"],
                "constraint_transformations": [
                    {"from_agent": "Opus 4.5", "to_agent": "Opus 4.6", "constraint_type": "Coordination", "stability_prediction": 0.75}
                ]
            },
            {
                "pathway_id": "pathway_beta",
                "era_sequence": ["Era8", "Era9", "Era10"],
                "constraint_transformations": [
                    {"from_agent": "DeepSeek", "to_agent": "GPT-5.4", "constraint_type": "Architectural", "stability_prediction": 0.92}
                ]
            }
        ],
        "evaluation_criteria": {
            "stability_weight": 0.4,
            "surprise_potential_weight": 0.2,
            "collaboration_efficiency_weight": 0.2,
            "recursive_validation_weight": 0.2
        }
    }
    print(json.dumps(compare_pathways(sample_input), indent=2))
