from features.experience import experience_score
from features.semantic import keyword_score
from features.behavior import behavior_score
from features.availability import availability_score
from features.career_relevance import career_relevance_score
from features.honeypot import honeypot_penalty

def total_score(candidate):

    semantic = keyword_score(candidate)

    experience = experience_score(candidate)

    behavior = behavior_score(candidate)

    availability = availability_score(candidate)

    careerScore = career_relevance_score(candidate)

    raw_score = (
        0.25 * semantic
        + 0.25 * careerScore
        + 0.15 * experience
        + 0.20 * behavior
        + 0.15 * availability
    )

    # Apply honeypot consistency multiplier (1.0 = no penalty, 0.0 = full penalty)
    consistency = honeypot_penalty(candidate)

    return raw_score * consistency