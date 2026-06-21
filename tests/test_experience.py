import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from parsing.loader import load_sample_candidates
from features.experience import experience_score, retrieval_experience_score


candidates = load_sample_candidates(
    "data/raw/sample_candidates.json"
)

for candidate in candidates[:10]:
    print("=" * 80)
    print(candidate.profile.current_title)

    if candidate.career_history:
        print(candidate.career_history[0].description[:500])