import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from parsing.loader import load_candidates_jsonl
from ranking.rank import rank_candidates
from ranking.explanations import explain_candidate


print("Loading candidates...")

candidates = load_candidates_jsonl(
    "data/raw/candidates.jsonl",
    limit=10000,
)

print(f"Loaded {len(candidates)} candidates")

print("Ranking candidates...")

ranked = rank_candidates(candidates)

print("\nTOP 25 CANDIDATES\n")

for rank, (score, candidate) in enumerate(ranked[:25], start=1):

    explanation = explain_candidate(candidate)

    print("=" * 100)

    print(f"Rank #{rank}")
    print(f"Score: {score:.2f}")

    print(f"Candidate ID: {candidate.candidate_id}")

    print(
        f"{candidate.profile.current_title}"
        f" @ {candidate.profile.current_company}"
    )

    print(
        f"Experience: "
        f"{candidate.profile.years_of_experience} years"
    )

    print("\nBreakdown")

    print(
        f"Semantic      : "
        f"{explanation['semantic']:.2f}"
    )

    print(
        f"Career        : "
        f"{explanation['career']:.2f}"
    )

    print(
        f"Experience    : "
        f"{explanation['experience']:.2f}"
    )

    print(
        f"Behavior      : "
        f"{explanation['behavior']:.2f}"
    )

    print(
        f"Availability  : "
        f"{explanation['availability']:.2f}"
    )