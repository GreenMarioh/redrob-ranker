import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from parsing.loader import load_sample_candidates

candidates = load_sample_candidates(
    "data/raw/sample_candidates.json"
)

print(len(candidates))

candidate = candidates[0]

print(candidate.candidate_id)
print(candidate.profile.current_title)
print(candidate.redrob_signals.notice_period_days)