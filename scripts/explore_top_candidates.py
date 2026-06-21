import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from parsing.loader import load_candidates_jsonl
from features.scorer import total_score


candidates = load_candidates_jsonl(
    "data/raw/candidates.jsonl",
    limit=1000,
)

ranked = []

for candidate in candidates:
    ranked.append(
        (
            total_score(candidate),
            candidate,
        )
    )

ranked.sort(
    key=lambda x: x[0],
    reverse=True,
)

print("\nTOP 20 CANDIDATES\n")

for rank, (score, candidate) in enumerate(ranked[:20], start=1):

    print("=" * 80)

    print(
        f"{rank}. "
        f"{candidate.profile.current_title}"
    )

    print(
        f"Score: {score:.2f}"
    )

    print(
        f"Experience: "
        f"{candidate.profile.years_of_experience}"
    )

    print(
        f"Company: "
        f"{candidate.profile.current_company}"
    )

    print(
        f"Candidate ID: "
        f"{candidate.candidate_id}"
    )