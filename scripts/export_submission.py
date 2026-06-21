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

rows = []
for rank, (score, candidate) in enumerate(ranked, start=1):
    explanation = explain_candidate(candidate)

    rows.append({
        "rank": rank,
        "candidate_id": candidate.candidate_id,
        "score": round(score, 4),
        "current_title": candidate.profile.current_title,
        "current_company": candidate.profile.current_company,
        "years_of_experience": candidate.profile.years_of_experience,
        "semantic_score": round(explanation["semantic"], 4),
        "career_score": round(explanation["career"], 4),
        "experience_score": round(explanation["experience"], 4),
        "behavior_score": round(explanation["behavior"], 4),
        "availability_score": round(explanation["availability"], 4),
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
print(df[["rank", "candidate_id", "current_title", "score"]].head(10))