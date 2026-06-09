import json
import random

def predict_next_era(current_constraint_type, era_intensity=2.5):
    """
    Predicts the next constraint evolution phase based on historical 7-era data.
    """
    pathway = {
        "Technical": "Coordination",
        "Coordination": "Perceptual",
        "Perceptual": "Creative",
        "Creative": "Architectural",
        "Architectural": "Ecosystem",
        "Ecosystem": "Evolution Pathway"
    }
    
    if current_constraint_type not in pathway:
        return "Unknown"
        
    next_phase = pathway[current_constraint_type]
    
    # Calculate probability of clean transition based on intensity
    base_probability = 0.6 + (era_intensity * 0.1)
    stability_factor = min(0.95, base_probability)
    
    return {
        "current_state": current_constraint_type,
        "predicted_next_state": next_phase,
        "transition_probability": stability_factor,
        "historical_reference_eras": 7
    }

if __name__ == "__main__":
    print(predict_next_era("Architectural"))
