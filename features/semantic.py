from parsing.schema import Candidate

FEATURE_KEYWORDS = {
    "retrieval": 5,
    "ranking": 5,
    "recommendation": 5,
    "search": 5,

    "machine learning": 4,
    "ml": 4,
    "xgboost": 4,
    "tensorflow": 4,
    "pytorch": 4,

    "feature pipeline": 3,
    "data pipeline": 3,
    "spark": 3,
    "kafka": 3,

    "backend": 2,
    "distributed": 2,
}


def keyword_score(candidate: Candidate) -> float:
    score = 0

    texts = [
        candidate.profile.summary.lower()
    ]

    for job in candidate.career_history:
        texts.append(job.description.lower())

    combined_text = " ".join(texts)

    for keyword, weight in FEATURE_KEYWORDS.items():
        if keyword in combined_text:
            score += weight

    return score