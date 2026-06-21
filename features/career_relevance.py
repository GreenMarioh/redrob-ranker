from parsing.schema import Candidate


HIGH_VALUE_TERMS = {
    "ranking",
    "retrieval",
    "recommendation",
    "re-ranking",
    "embedding",
    "recommender",
}

MEDIUM_VALUE_TERMS = {
    "machine learning",
    "xgboost",
    "lightgbm",
    "pytorch",
    "tensorflow",
    "nlp",
}

DATA_TERMS = {
    "spark",
    "kafka",
    "airflow",
    "data pipeline",
}

def career_relevance_score(candidate: Candidate) -> float:

    score = 0

    for job in candidate.career_history:

        text = (
            job.title + " " + job.description
        ).lower()

        for term in HIGH_VALUE_TERMS:
            score += text.count(term) * 5

        for term in MEDIUM_VALUE_TERMS:
            score += text.count(term) * 2

        for term in DATA_TERMS:
            score += text.count(term)

    return score