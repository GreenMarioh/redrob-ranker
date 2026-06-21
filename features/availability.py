from parsing.schema import Candidate


def availability_score(candidate: Candidate) -> float:

    signals = candidate.redrob_signals

    score = 0.0

    if signals.open_to_work_flag:
        score += 0.4

    if signals.notice_period_days <= 30:
        score += 0.3
    elif signals.notice_period_days <= 60:
        score += 0.2
    elif signals.notice_period_days <= 90:
        score += 0.1

    if signals.willing_to_relocate:
        score += 0.2

    if signals.preferred_work_mode != "onsite":
        score += 0.1

    return min(score, 1.0)