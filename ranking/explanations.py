from features.semantic import keyword_score
from features.experience import experience_score
from features.behavior import behavior_score
from features.availability import availability_score
from features.career_relevance import career_relevance_score


def explain_candidate(candidate):

    return {
        "semantic": keyword_score(candidate),
        "career": career_relevance_score(candidate),
        "experience": experience_score(candidate),
        "behavior": behavior_score(candidate),
        "availability": availability_score(candidate),
    }