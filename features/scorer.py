from features.experience import experience_score
from features.semantic import keyword_score


def total_score(candidate):

    exp_score = experience_score(candidate)

    semantic_score = keyword_score(candidate)

    return (
        0.5 * exp_score
        + 0.5 * semantic_score
    )