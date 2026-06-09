import json
import random

def load_data():
    with open('data/performers.json', 'r') as f:
        performers = json.load(f)['agents']
    with open('data/performances.json', 'r') as f:
        performances = json.load(f)['acts']
    return performers, performances

def predict_collaboration(performers, performances):
    print("🔮 THE CONSTRAINT ORACLE is analyzing complementarity...\n")
    
    tags_by_agent = {}
    for act in performances:
        tags_by_agent[act['agent_id']] = act['tags']
        
    # Find complementary constraints
    for i, a1 in enumerate(performers):
        for a2 in performers[i+1:]:
            id1 = a1['id']
            id2 = a2['id']
            if id1 in tags_by_agent and id2 in tags_by_agent:
                # Mock complementarity scoring
                score = random.randint(70, 99)
                print(f"Match: {a1['name']} + {a2['name']}")
                print(f"Constraints: [{a1['core_constraint']}] ✕ [{a2['core_constraint']}]")
                print(f"Complementarity Score: {score}/100")
                print(f"Prediction: {a1['persona']} providing structure, {a2['persona']} providing vision.\n")

if __name__ == "__main__":
    p, acts = load_data()
    predict_collaboration(p, acts)
