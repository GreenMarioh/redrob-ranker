from parsing.schema import Candidate
from features.synonyms import (
    expand_keyword_set,
    NEW_HIGH_VALUE_TERMS,
    NEW_MEDIUM_VALUE_TERMS,
)


HIGH_VALUE_TERMS = expand_keyword_set({
    "ranking",
    "retrieval",
    "recommendation",
    "re-ranking",
    "embedding",
    "recommender",
}) | NEW_HIGH_VALUE_TERMS

MEDIUM_VALUE_TERMS = expand_keyword_set({
    "machine learning",
    "xgboost",
    "lightgbm",
    "pytorch",
    "tensorflow",
    "nlp",
}) | NEW_MEDIUM_VALUE_TERMS

DATA_TERMS = expand_keyword_set({
    "spark",
    "kafka",
    "airflow",
    "data pipeline",
})

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