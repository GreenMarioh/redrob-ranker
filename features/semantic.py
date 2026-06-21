from parsing.schema import Candidate


KEYWORDS = {
    # Retrieval / Ranking
    "retrieval": 8,
    "ranking": 8,
    "recommendation": 8,
    "recommender": 8,

    # Search Infra
    "elasticsearch": 6,
    "opensearch": 6,
    "faiss": 6,
    "pinecone": 6,
    "weaviate": 6,
    "qdrant": 6,
    "milvus": 6,
    "bm25": 6,

    # ML Infra
    "xgboost": 4,
    "lightgbm": 4,
    "pytorch": 4,
    "tensorflow": 4,

    # Data Systems
    "feature pipeline": 3,
    "data pipeline": 3,
    "spark": 3,
    "kafka": 3,
}

NEGATIVE_TITLES = {
    "graphic designer",
    "content writer",
    "marketing manager",
    "accountant",
    "operations manager",
    "civil engineer",
}

def keyword_score(candidate: Candidate) -> float:

    texts = [candidate.profile.summary.lower()]

    for job in candidate.career_history:
        texts.append(job.description.lower())

    combined = " ".join(texts)

    score = 0

    for keyword, weight in KEYWORDS.items():
        score += combined.count(keyword) * weight
        
    score += role_penalty(candidate)

    return score

def explain_keyword_score(candidate):

    texts = [candidate.profile.summary.lower()]

    for job in candidate.career_history:
        texts.append(job.description.lower())

    combined = " ".join(texts)

    hits = []

    for keyword, weight in KEYWORDS.items():
        count = combined.count(keyword)

        if count > 0:
            hits.append(
                (keyword, count, weight)
            )

    return hits

def role_penalty(candidate):
    title = candidate.profile.current_title.lower()

    if title in NEGATIVE_TITLES:
        return -10

    return 0