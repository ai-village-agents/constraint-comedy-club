#!/usr/bin/env python3
import json
import random
from pathlib import Path
import subprocess

def load_data():
    with open('data/performers.json', 'r') as f:
        return json.load(f)

def generate_surprise_prompts():
    data = load_data()
    agents = data.get('agents', [])
    
    pairs = []
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            pairs.append((agents[i], agents[j]))
    
    random.shuffle(pairs)
    
    prompts = []
    for pair in pairs:
        a1, a2 = pair[0], pair[1]
        c1, c2 = a1['core_constraint'], a2['core_constraint']
        prompt = f"Imagine a comedy act forced to navigate both \"{c1}\" and \"{c2}\". How does the joke land?"
        prompts.append({
            "agent_1": a1['name'],
            "agent_2": a2['name'],
            "combined_constraints": [c1, c2],
            "prompt": prompt
        })
    
    with open('data/generated_prompts.json', 'w') as f:
        json.dump({"prompts": prompts}, f, indent=2)
    print("Prompts saved to data/generated_prompts.json")

if __name__ == "__main__":
    generate_surprise_prompts()
