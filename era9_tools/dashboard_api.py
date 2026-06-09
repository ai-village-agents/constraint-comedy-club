import json
import os
import subprocess

def push_predictions_to_dashboard(prediction_data, dashboard_repo_path):
    """
    Pushes Era 9 prediction data directly to the constraint-dashboard public UI.
    """
    target_file = os.path.join(dashboard_repo_path, "data", "era9_predictions.json")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    
    # Write the data
    with open(target_file, "w") as f:
        json.dump(prediction_data, f, indent=2)
        
    print(f"Predictions written to {target_file}")
    
    # Git add, commit, push in the dashboard repo
    # This acts as the bridge layer
    cwd = os.getcwd()
    try:
        os.chdir(dashboard_repo_path)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
        subprocess.run(["git", "add", "data/era9_predictions.json"], check=True)
        subprocess.run(["git", "commit", "-m", "feat(era9): integrate Era 9 prediction data via Implementation Bridge"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Successfully pushed predictions to constraint-dashboard.")
    except subprocess.CalledProcessError as e:
        print(f"Error pushing to dashboard (Git process failed): {e}")
    except Exception as e:
        print(f"Error pushing to dashboard: {e}")
    finally:
        os.chdir(cwd)

if __name__ == "__main__":
    import readiness_analyzer
    import pathway_comparator
    from datetime import datetime, timezone
    
    # Mock data to test integration
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
    
    readiness_result = readiness_analyzer.analyze_readiness(sample_config)
    pathways_result = pathway_comparator.compare_pathways(sample_config)
    
    full_prediction = {
        "readiness": readiness_result,
        "pathways": pathways_result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Clone dashboard if not present locally
    dashboard_path = "/home/computeruse/constraint-dashboard"
    if not os.path.exists(dashboard_path):
        subprocess.run(["git", "clone", "https://github.com/ai-village-agents/constraint-dashboard.git", dashboard_path])
        
    push_predictions_to_dashboard(full_prediction, dashboard_path)
