import json
import os

def update_dashboard_data(readiness_data, comparison_data, output_file="/home/computeruse/constraint-dashboard/data/era9_predictions.json"):
    """
    Format output from the Era 9 tools into a single JSON for the dashboard to consume.
    """
    dashboard_payload = {
        "readiness": readiness_data,
        "pathways": comparison_data,
        "timestamp": "2026-06-09T19:24:00Z"
    }
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(dashboard_payload, f, indent=2)
        
    return dashboard_payload

if __name__ == "__main__":
    print("API stub created")
