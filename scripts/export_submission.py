import sys
import json
import concurrent.futures
from pathlib import Path
import pandas as pd

# Fixes the broken `__file__` reference to make path resolution bulletproof
sys.path.append(str(Path(__file__).resolve().parent.parent))

from parsing.loader import parse_candidate
from features.scorer import total_score
from features.semantic import KEYWORDS

def process_candidate_line(line: str):
    """Worker function for multiprocessing."""
    try:
        candidate_dict = json.loads(line)
        candidate = parse_candidate(candidate_dict)
        
        score = total_score(candidate)
        
        # Calculate AI core skills by matching candidate skills with our known keywords
        ai_skills_count = sum(1 for s in candidate.skills if s.name.lower() in KEYWORDS)
        title = candidate.profile.current_title
        years = candidate.profile.years_of_experience
        resp_rate = candidate.redrob_signals.recruiter_response_rate
        
        reasoning = f"{title} with {years:.1f} yrs; {ai_skills_count} AI core skills; response rate {resp_rate:.2f}."
        
        return {
            "candidate_id": candidate.candidate_id,
            "score": score,
            "reasoning": reasoning
        }
    except Exception:
        return None

def main():
    print("Loading and ranking candidates in parallel...")
    data_path = Path("data/raw/candidates.jsonl")
    
    with open(data_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    print(f"Loaded {len(lines)} lines")
    
    results = []
    # Process lines in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # chunksize=1000 provides a good balance between IPC overhead and parallelism
        for result in executor.map(process_candidate_line, lines, chunksize=1000):
            if result is not None:
                results.append(result)
                
    print(f"Successfully processed {len(results)} candidates")
    
    # Sort results by score (descending)
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Collect raw scores for normalization
    raw_scores = [r["score"] for r in results]
    min_score = min(raw_scores) if raw_scores else 0.0
    max_score = max(raw_scores) if raw_scores else 1.0
    score_range = max_score - min_score
    
    rows = []
    TOP_K = 100
    
    for rank, res in enumerate(results[:TOP_K], start=1):
        score = res["score"]
        # Normalize score to [0, 1] using min-max normalization
        normalized_score = (score - min_score) / score_range if score_range > 0 else 1.0
        
        rows.append({
            "candidate_id": res["candidate_id"],
            "rank": rank,
            "score": round(normalized_score, 4),
            "reasoning": res["reasoning"]
        })
        
    df = pd.DataFrame(rows)
    
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    csv_path = output_dir / "ranked_candidates.csv"
    xlsx_path = output_dir / "ranked_candidates.xlsx"
    
    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)
    
    print(f"CSV saved to: {csv_path}")
    print(f"XLSX saved to: {xlsx_path}")
    
    print("\nTop 10 Preview\n")
    print(df.head(10))

if __name__ == "__main__":
    main()
