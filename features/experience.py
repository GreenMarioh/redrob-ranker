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

RETRIEVAL_KEYWORDS = {
    "retrieval",
    "search",
    "ranking",
    "recommendation",
    "recommender",
    "vector",
    "embedding",
    "elasticsearch",
    "opensearch",
    "faiss",
    "pinecone",
    "weaviate",
    "qdrant",
    "milvus",
    "bm25",
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
    
    experience = score
    title = title_relevance_score(candidate)
    retrieval = retrieval_experience_score(candidate)

    return (
        0.40 * experience
        + 0.30 * title
        + 0.30 * retrieval
    )

def title_relevance_score(candidate: Candidate) -> float:
    title = candidate.profile.current_title.lower()

    if any(keyword in title for keyword in NON_TECH_KEYWORDS):
        return 0.0

    if any(keyword in title for keyword in AI_KEYWORDS):
        return 1.0

    return 0.5


def retrieval_experience_score(candidate: Candidate) -> float:
    score = 0

    for job in candidate.career_history:
        text = (
            job.title + " " + job.description
        ).lower()

        for keyword in RETRIEVAL_KEYWORDS:
            if keyword in text:
                score += 1

    return min(score / 5, 1.0)