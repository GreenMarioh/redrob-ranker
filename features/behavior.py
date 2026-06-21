from parsing.schema import Candidate


def behavior_score(candidate: Candidate) -> float:

    signals = candidate.redrob_signals

    score = 0.0

    score += signals.recruiter_response_rate

    score += signals.interview_completion_rate

    score += min(
        signals.github_activity_score / 100,
        1.0
    )

    score += min(
        signals.saved_by_recruiters_30d / 20,
        1.0
    )

    return score / 4