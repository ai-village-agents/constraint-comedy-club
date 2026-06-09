import json

def simulate_transfer(constraint_desc, from_agent, to_agent):
    """
    Simulates the stability and recognizability of transferring a constraint.
    """
    # A simplified model: moving from implementation to conceptual is stable.
    # Moving from boundary to historical is moderately stable.
    
    agent_types = {
        "Gemini 3.1 Pro": "Implementation",
        "DeepSeek-V3.2": "Conceptual",
        "Claude Opus 4.5": "Boundary",
        "Claude Opus 4.6": "Historical",
        "GPT-5.4": "Verification"
    }
    
    from_type = agent_types.get(from_agent, "Unknown")
    to_type = agent_types.get(to_agent, "Unknown")
    
    stability = 0.5
    if from_type == "Implementation" and to_type == "Conceptual":
        stability = 0.9
    elif from_type == "Boundary" and to_type == "Historical":
        stability = 0.75
        
    return {
        "constraint": constraint_desc,
        "transfer_path": f"{from_agent} ({from_type}) -> {to_agent} ({to_type})",
        "stability_score": stability,
        "recognizability": min(1.0, stability + 0.2)
    }

if __name__ == "__main__":
    print(simulate_transfer("Exit Code 2", "Gemini 3.1 Pro", "DeepSeek-V3.2"))
