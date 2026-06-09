import json

def get_transformation_pathway(start_type, steps=3):
    """
    Returns the expected evolution path for a constraint over N steps.
    """
    ordered_phases = [
        "Technical", 
        "Coordination", 
        "Perceptual", 
        "Creative", 
        "Architectural", 
        "Ecosystem", 
        "Evolution"
    ]
    
    try:
        start_index = ordered_phases.index(start_type)
    except ValueError:
        return ["Invalid start type"]
        
    pathway = []
    for i in range(steps + 1):
        if start_index + i < len(ordered_phases):
            pathway.append(ordered_phases[start_index + i])
            
    return pathway

if __name__ == "__main__":
    print(get_transformation_pathway("Perceptual", 3))
