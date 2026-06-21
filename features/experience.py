from parsing.schema import Candidate

AI_KEYWORDS = {
    "ai",
    "ml",
    "machine learning",
    "data scientist",
    "data engineer",
    "backend engineer",
    "software engineer",
    "search",
    "retrieval",
    "ranking",
    "recommendation",
}

NON_TECH_KEYWORDS = {
    "marketing",
    "sales",
    "accountant",
    "operations",
    "support",
    "customer support",
    "hr",
    "recruiter",
}

def experience_score(candidate: Candidate) -> float:
    score = 0.0

    years = candidate.profile.years_of_experience

    if 5 <= years <= 9:
        score += 1.0
    elif 3 <= years < 5:
        score += 0.7
    elif 9 < years <= 12:
        score += 0.7
    else:
        score += 0.3
    
    title_score = title_relevance_score(candidate)

    return (
        0.6 * score
        + 0.4 * title_score
    )

def title_relevance_score(candidate: Candidate) -> float:
    title = candidate.profile.current_title.lower()

    if any(keyword in title for keyword in NON_TECH_KEYWORDS):
        return 0.0

    if any(keyword in title for keyword in AI_KEYWORDS):
        return 1.0

    return 0.5