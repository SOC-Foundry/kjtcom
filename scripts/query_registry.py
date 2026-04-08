#!/usr/bin/env python3
"""Query the kjtcom script registry (ADR-022).
Usage:
  python3 scripts/query_registry.py "topic"
  python3 scripts/query_registry.py --pipeline bourdain
  python3 scripts/query_registry.py --writes-checkpoint
  python3 scripts/query_registry.py --linked-gotcha G53
"""
import os, json, sys, argparse

REGISTRY_PATH = "data/script_registry.json"

def load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return None
    with open(REGISTRY_PATH) as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Query kjtcom script registry")
    parser.add_argument("query", nargs="?", help="Topic or keyword to search for in path/purpose")
    parser.add_argument("--pipeline", help="Filter by pipeline (e.g. bourdain, calgold)")
    parser.add_argument("--writes-checkpoint", action="store_true", help="Filter for scripts that write checkpoints")
    parser.add_argument("--linked-gotcha", help="Filter by linked gotcha ID (e.g. G53)")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON for found entries")
    args = parser.parse_args()

    reg = load_registry()
    if not reg:
        print(f"Error: Registry not found at {REGISTRY_PATH}")
        sys.exit(1)

    results = []
    scripts = reg.get("scripts", [])

    for s in scripts:
        match = True
        
        if args.query:
            q = args.query.lower()
            if q not in s["path"].lower() and q not in s["purpose"].lower():
                match = False
        
        if args.pipeline and s.get("pipeline") != args.pipeline:
            match = False
            
        if args.writes_checkpoint:
            if not any("checkpoint" in o.lower() for o in s.get("outputs", [])):
                match = False
                
        if args.linked_gotcha:
            if args.linked_gotcha not in s.get("linked_gotchas", []):
                match = False

        if match:
            results.append(s)

    if not results:
        print("No scripts matching query found.")
        sys.exit(0)

    if args.raw:
        print(json.dumps(results, indent=2))
    else:
        print(f"Found {len(results)} scripts:")
        print("-" * 60)
        for s in results:
            print(f"Path:    {s['path']}")
            print(f"Purpose: {s['purpose']}")
            if s.get('pipeline') != 'none':
                print(f"Pipeline: {s['pipeline']}")
            if s.get('inputs'):
                print(f"Inputs:  {', '.join(s['inputs'])}")
            if s.get('outputs'):
                print(f"Outputs: {', '.join(s['outputs'])}")
            print("-" * 60)

if __name__ == "__main__":
    main()
