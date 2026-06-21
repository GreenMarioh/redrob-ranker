import sys

sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from parsing.loader import load_candidates_jsonl
from features.scorer import total_score
from ranking.explanations import explain_candidate


candidates = load_candidates_jsonl(
    "data/raw/candidates.jsonl",
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

print("\nTOP 5 CANDIDATES (DETAILED)\n")

for rank, (score, candidate) in enumerate(ranked[:5], start=1):

    print("\n" + "=" * 100)

    print(f"RANK #{rank}")
    print(f"Score: {score:.2f}")
    print(f"Candidate ID: {candidate.candidate_id}")

    print(f"\nTitle: {candidate.profile.current_title}")
    print(f"Company: {candidate.profile.current_company}")
    print(f"Experience: {candidate.profile.years_of_experience} years")

    explanation = explain_candidate(candidate)

    print("\nSCORE BREAKDOWN")
    print("-" * 50)

    print(f"Semantic      : {explanation['semantic']:.2f}")
    print(f"Career        : {explanation['career']:.2f}")
    print(f"Experience    : {explanation['experience']:.2f}")
    print(f"Behavior      : {explanation['behavior']:.2f}")
    print(f"Availability  : {explanation['availability']:.2f}")

    print("\nSUMMARY")
    print("-" * 50)
    print(candidate.profile.summary)

    print("\nTOP CAREER ENTRIES")
    print("-" * 50)

    for idx, job in enumerate(candidate.career_history[:2], start=1):
        print(f"\nJob #{idx}")
        print(f"Company: {job.company}")
        print(f"Title: {job.title}")

        description = job.description

        if len(description) > 600:
            description = description[:600] + "..."

        print("Description:")
        print(description)

    print("\nTOP SKILLS")
    print("-" * 50)

    for skill in candidate.skills[:10]:
        print(
            f"{skill.name} "
            f"(endorsements={skill.endorsements}, "
            f"duration={skill.duration_months}m)"
        )

    print("\nREDROB SIGNALS")
    print("-" * 50)

    signals = candidate.redrob_signals

    print(f"Open To Work: {signals.open_to_work_flag}")
    print(f"Github Activity: {signals.github_activity_score}")
    print(f"Recruiter Response: {signals.recruiter_response_rate}")
    print(f"Interview Completion: {signals.interview_completion_rate}")
    print(f"Notice Period: {signals.notice_period_days} days")
    print(f"Saved By Recruiters: {signals.saved_by_recruiters_30d}")