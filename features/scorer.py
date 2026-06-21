from features.experience import experience_score
from features.semantic import keyword_score
from features.behavior import behavior_score


def total_score(candidate):

    exp_score = experience_score(candidate)

    semantic_score = keyword_score(candidate)

    return (
    0.40 * semantic_score
    + 0.30 * exp_score
    + 0.30 * behavior_score(candidate)
)