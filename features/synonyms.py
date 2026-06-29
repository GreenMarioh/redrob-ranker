"""
Centralized technical synonym registry for keyword expansion.

This module provides a domain-specific synonym map and utility functions
to expand keyword sets/dicts used across all feature modules. Unlike a
general-purpose thesaurus, these synonyms are curated for AI/ML/Search
engineering roles and map technical terms to their domain-equivalent
variations.

Usage:
    from features.synonyms import expand_keyword_set, expand_keyword_dict

    KEYWORDS = expand_keyword_dict({"retrieval": 8, "ranking": 8})
    TERMS = expand_keyword_set({"retrieval", "ranking"})
"""


# ---------------------------------------------------------------------------
# Master Synonym Map
#
# Maps each canonical keyword to a set of domain-equivalent terms.
# Synonyms are bidirectional within a group — if "retrieval" maps to
# "dense retrieval", then searching for "dense retrieval" will also
# surface candidates who mention it.
# ---------------------------------------------------------------------------

SYNONYM_MAP: dict[str, set[str]] = {

    # ── Retrieval / Search ───────────────────────────────────────────────
    "retrieval": {
        "information retrieval",
        "dense retrieval",
        "sparse retrieval",
    },
    "ranking": {
        "learning to rank",
        "l2r",
        "reranking",
    },
    "recommendation": {
        "collaborative filtering",
        "content-based filtering",
        "recommender system",
        "rec sys",
        "matrix factorization",
    },
    "recommender": {
        "collaborative filtering",
        "content-based filtering",
        "recommender system",
        "rec sys",
        "matrix factorization",
    },

    # ── Search Infrastructure ────────────────────────────────────────────
    "elasticsearch": {
        "solr",
        "lucene",
    },
    "faiss": {
        "annoy",
        "scann",
        "hnsw",
        "approximate nearest neighbor",
    },
    "bm25": {
        "tf-idf",
        "tfidf",
    },

    # ── ML Frameworks ────────────────────────────────────────────────────
    "xgboost": {
        "gradient boosting",
        "gradient-boosted",
        "gbm",
    },
    "lightgbm": {
        "gradient boosting",
        "gradient-boosted",
        "gbm",
    },
    "pytorch": {
        "torch",
    },
    "tensorflow": {
        "keras",
    },

    # ── NLP ──────────────────────────────────────────────────────────────
    "nlp": {
        "natural language processing",
        "text mining",
        "text classification",
        "named entity recognition",
        "ner",
    },

    # ── Embeddings ───────────────────────────────────────────────────────
    "embedding": {
        "word2vec",
        "glove",
        "sentence embedding",
        "dense vector",
    },

    # ── Data Infra ───────────────────────────────────────────────────────
    "spark": {
        "pyspark",
    },
    "data pipeline": {
        "etl",
        "data ingestion",
    },
    "feature pipeline": {
        "feature engineering",
    },
}


# ---------------------------------------------------------------------------
# New keyword categories (not synonyms of existing terms)
#
# These are used by semantic.py to add entirely new keyword groups
# that the original system didn't track at all.
# ---------------------------------------------------------------------------

NEW_KEYWORD_CATEGORIES: dict[str, int] = {
    # Deep Learning / Neural Networks (weight 4 — framework-level relevance)
    "deep learning": 4,
    "neural network": 4,
    "transformer": 4,

    # LLM-specific (weight 3 — relevant but not core to retrieval/ranking)
    "bert": 3,
    "gpt": 3,
    "llm": 3,
    "llms": 3,
    "fine-tuning": 3,
    "huggingface": 3,
    "hugging face": 3,
    "rag": 3,
    "retrieval augmented generation": 3,
    "predictive modeling": 3,

    # Vector Search (weight 6 — directly relevant infrastructure)
    "vector search": 6,
    "vector database": 6,
    "similarity search": 6,
    "semantic search": 6,

    # MLOps (weight 3 — supporting infrastructure)
    "mlflow": 3,
    "mlops": 3,
    "model serving": 3,
    "feature store": 3,
    "sagemaker": 3,

    # General ML (weight 3 — lower signal)
    "scikit-learn": 3,
    "sklearn": 3,
}

# New terms to add to career_relevance HIGH_VALUE_TERMS
NEW_HIGH_VALUE_TERMS: set[str] = {
    "semantic search",
    "vector search",
    "information retrieval",
    "dense retrieval",
    "learning to rank",
    "collaborative filtering",
    "content-based filtering",
}

# New terms to add to career_relevance MEDIUM_VALUE_TERMS
NEW_MEDIUM_VALUE_TERMS: set[str] = {
    "deep learning",
    "neural network",
    "transformer",
    "bert",
    "scikit-learn",
    "sklearn",
}

# New terms for experience RETRIEVAL_KEYWORDS
NEW_RETRIEVAL_KEYWORDS: set[str] = {
    "information retrieval",
    "dense retrieval",
    "semantic search",
    "learning to rank",
    "l2r",
    "reranking",
    "similarity search",
    "vector search",
    "approximate nearest neighbor",
    "solr",
    "lucene",
    "annoy",
    "scann",
    "hnsw",
}

# New terms for experience AI_KEYWORDS
NEW_AI_KEYWORDS: set[str] = {
    "deep learning",
    "neural network",
    "nlp",
    "natural language processing",
    "data science",
    "applied scientist",
}

# New terms for honeypot EXPERT_SKILL_KEYWORDS
NEW_EXPERT_SKILL_KEYWORDS: set[str] = {
    "deep learning",
    "neural network",
    "transformer",
    "bert",
    "scikit-learn",
    "sklearn",
    "solr",
    "lucene",
    "annoy",
    "scann",
    "hnsw",
    "sagemaker",
    "mlflow",
    "semantic search",
    "vector search",
    "similarity search",
}


# ---------------------------------------------------------------------------
# Expansion utilities
# ---------------------------------------------------------------------------

def expand_keyword_set(keywords: set) -> set:
    """
    Expand a set of keywords by adding all mapped synonyms.

    Example:
        expand_keyword_set({"retrieval", "ranking"})
        # → {"retrieval", "ranking", "information retrieval", "dense retrieval",
        #    "sparse retrieval", "learning to rank", "l2r", "reranking"}
    """
    expanded = set(keywords)

    for keyword in keywords:
        if keyword in SYNONYM_MAP:
            expanded.update(SYNONYM_MAP[keyword])

    return expanded


def expand_keyword_dict(keywords: dict[str, int]) -> dict[str, int]:
    """
    Expand a {keyword: weight} dict by adding synonyms that inherit
    the parent keyword's weight.

    Existing entries are never overridden — if a synonym already has
    a weight, the explicit weight takes priority.

    Example:
        expand_keyword_dict({"retrieval": 8})
        # → {"retrieval": 8, "information retrieval": 8,
        #    "dense retrieval": 8, "sparse retrieval": 8}
    """
    expanded = dict(keywords)

    for keyword, weight in keywords.items():
        if keyword in SYNONYM_MAP:
            for synonym in SYNONYM_MAP[keyword]:
                if synonym not in expanded:
                    expanded[synonym] = weight

    return expanded
