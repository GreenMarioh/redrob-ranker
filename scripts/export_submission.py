import sys
from pathlib import Path
import pandas as pd

# Fixes the broken `__file__` reference to make path resolution bulletproof
sys.path.append(str(Path(__file__).resolve().parent.parent))

from parsing.loader import load_candidates_jsonl
from ranking.rank import rank_candidates
from ranking.explanations import explain_candidate

print("Loading candidates...")
candidates = load_candidates_jsonl("data/raw/candidates.jsonl")
print(f"Loaded {len(candidates)} candidates")

print("Ranking candidates...")
ranked = rank_candidates(candidates)

from features.semantic import KEYWORDS

rows = []
for rank, (score, candidate) in enumerate(ranked, start=1):
    explanation = explain_candidate(candidate)
    
    # Calculate AI core skills by matching candidate skills with our known keywords
    ai_skills_count = sum(1 for s in candidate.skills if s.name.lower() in KEYWORDS)
    
    title = candidate.profile.current_title
    years = candidate.profile.years_of_experience
    resp_rate = candidate.redrob_signals.recruiter_response_rate
    
    reasoning = f"{title} with {years:.1f} yrs; {ai_skills_count} AI core skills; response rate {resp_rate:.2f}."

    rows.append({
        "candidate_id": candidate.candidate_id,
        "rank": rank,
        "score": round(score, 4),
        "reasoning": reasoning
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