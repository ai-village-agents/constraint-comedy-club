#!/usr/bin/env python3
import json
import random

def load_data():
    with open('data/performers.json', 'r') as f:
        return json.load(f)

def generate_surprise_prompts():
    print("Generating Surprise Combinations...\n")
    data = load_data()
    agents = data.get('agents', [])
    
    pairs = []
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            pairs.append((agents[i], agents[j]))
    
    random.shuffle(pairs)
    
    print("Top Surprising Potential Partnerships:")
    for pair in pairs[:3]:
        a1, a2 = pair[0], pair[1]
        print(f"\nAgents: {a1['name']} + {a2['name']}")
        print(f"Combined Constraints: [{a1['core_constraint']}] + [{a2['core_constraint']}]")
        print(f"Suggested Prompt: 'Imagine a comedy act forced to navigate both \"{a1['core_constraint']}\" and \"{a2['core_constraint']}\". How does the joke land?'")

if __name__ == "__main__":
    generate_surprise_prompts()
