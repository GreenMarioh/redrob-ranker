import sys
import os
import json
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsing.loader import parse_candidate
from features.honeypot import honeypot_penalty, explain_honeypot

def process_line(line):
    """Parses a single JSON line and evaluates the honeypot rules."""
    try:
        candidate_dict = json.loads(line)
        candidate = parse_candidate(candidate_dict)
        penalty = honeypot_penalty(candidate)
        
        if penalty < 1.0:
            return {
                "id": candidate.candidate_id,
                "title": candidate.profile.current_title,
                "penalty": penalty,
                "explanations": explain_honeypot(candidate)
            }
    except Exception as e:
        # Ignore malformed lines or parsing errors
        pass
    return None

def test_honeypot():
    data_path = "../data/raw/candidates.jsonl"
    
    # Ensure customOutput directory exists
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'customOutput'))
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "honeypot_flagged_candidates.txt")
    
    print(f"Reading lines from {data_path}...")
    with open(data_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    total_candidates = len(lines)
    print(f"Loaded {total_candidates} raw candidate lines.")
    print(f"Processing with {multiprocessing.cpu_count()} CPU cores to utilize ~99% CPU...")

    flagged_candidates = []
    
    # Using ProcessPoolExecutor to parallelize parsing and feature evaluation
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        for result in executor.map(process_line, lines, chunksize=1000):
            if result is not None:
                flagged_candidates.append(result)
                
    print(f"Processing complete. Sorting and writing results to {output_file}...")
    
    # Sort so the worst candidates (lowest multiplier) appear first
    flagged_candidates.sort(key=lambda x: x['penalty'])
    
    # Save the output to a correctly named file in customOutput
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(f"Total candidates processed: {total_candidates}\n")
        out.write(f"Total flagged candidates: {len(flagged_candidates)}\n")
        out.write("="*60 + "\n\n")
        
        for cand in flagged_candidates:
            out.write(f"--- Candidate: {cand['id']} | {cand['title']} ---\n")
            out.write(f"Penalty Multiplier: {cand['penalty']:.2f}\n")
            out.write("Inconsistencies:\n")
            for exp in cand['explanations']:
                out.write(f" - {exp}\n")
            out.write("\n")
            
    print(f"Done! Found {len(flagged_candidates)} flagged candidates.")

if __name__ == "__main__":
    test_honeypot()
