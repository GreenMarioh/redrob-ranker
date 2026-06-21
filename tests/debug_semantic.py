import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from features.semantic import explain_keyword_score
from parsing.loader import load_candidates_jsonl
from features.semantic import keyword_score


TARGET_ID = "CAND_0000883"  # Change this

candidates = load_candidates_jsonl(
    "data/raw/candidates.jsonl",
    limit=1000,
)

target = None

for candidate in candidates:
    if candidate.candidate_id == TARGET_ID:
        target = candidate
        break

if target is None:
    print("Candidate not found")
    exit()

print("\nSemantic Score")
print("-" * 40)
print(keyword_score(target))

print("=" * 80)
print(f"ID: {target.candidate_id}")
print(f"Title: {target.profile.current_title}")
print(f"Company: {target.profile.current_company}")

print("\nSUMMARY")
print("-" * 40)
print(target.profile.summary)

print("\nKEYWORD HITS")
print("-" * 40)

for keyword, count, weight in explain_keyword_score(target):
    print(
        f"{keyword:<20} "
        f"count={count:<3} "
        f"weight={weight:<2} "
        f"contribution={count * weight}"
    )

print("\nCAREER HISTORY")
print("-" * 40)

for job in target.career_history[:2]:
    print(f"\n{job.title} @ {job.company}")
    print(job.description[:600])