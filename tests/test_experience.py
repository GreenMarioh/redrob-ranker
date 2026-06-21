import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from parsing.loader import load_sample_candidates
from features.experience import experience_score


candidates = load_sample_candidates(
    "data/raw/sample_candidates.json"
)

for candidate in candidates[:5]:
    print(
        candidate.profile.current_title,
        candidate.profile.years_of_experience,
        experience_score(candidate),
    )