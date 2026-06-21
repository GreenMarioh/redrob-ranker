# Candidate Ranking Methodology

## Overview

Our objective is to identify and rank the most relevant candidates for AI, Machine Learning, Search, Retrieval, Recommendation Systems, and Applied AI Engineering roles from a large candidate pool.

The ranking pipeline evaluates every candidate across multiple dimensions and combines these signals into a final ranking score.

The overall approach prioritizes:

1. Technical relevance to AI/ML roles
2. Evidence of real-world AI/ML work
3. Professional experience fit
4. Recruiter engagement and candidate responsiveness
5. Candidate availability and hiring readiness

---

# Ranking Pipeline

```
Candidate Dataset (JSONL)
            ↓
      Data Parsing
            ↓
   Feature Extraction
            ↓
     Candidate Scoring
            ↓
      Candidate Ranking
            ↓
      CSV/XLSX Export
```

The system processes all candidate profiles, extracts structured signals, computes feature scores, and generates a ranked leaderboard.

---

# Feature 1: Semantic Relevance

The semantic relevance component measures how strongly a candidate's profile aligns with AI and Machine Learning domains.

Signals include:

- Retrieval Systems
- Ranking Systems
- Recommendation Systems
- Embeddings
- NLP
- Machine Learning Frameworks
- Vector Databases
- AI Infrastructure

Examples of highly relevant terms:

- ranking
- retrieval
- recommendation
- recommender
- embedding
- XGBoost
- LightGBM
- PyTorch
- TensorFlow
- FAISS
- Pinecone
- Weaviate
- Qdrant

Candidates with stronger evidence of AI/ML expertise receive higher semantic relevance scores.

---

# Feature 2: Career Relevance

Career relevance evaluates actual work experience rather than profile buzzwords.

The system analyzes historical job descriptions and responsibilities to identify:

- Recommendation system development
- Search and retrieval infrastructure
- Ranking model development
- Production ML systems
- NLP systems
- Data engineering supporting ML workflows

High-value indicators include:

- ranking
- retrieval
- recommendation
- re-ranking
- embedding
- recommender systems

Medium-value indicators include:

- machine learning
- XGBoost
- LightGBM
- PyTorch
- TensorFlow
- NLP

Data engineering indicators include:

- Spark
- Kafka
- Airflow
- Data Pipelines

This feature rewards demonstrated experience rather than stated interest.

---

# Feature 3: Experience Fit

The experience score measures alignment with the target seniority range.

Factors considered:

- Total years of experience
- Current role seniority
- Professional career progression

Candidates whose experience level aligns closely with the target role receive higher scores.

---

# Feature 4: Behavioral Signals

Behavioral signals estimate candidate responsiveness and engagement.

Signals include:

- Recruiter response rate
- Interview completion rate
- GitHub activity score
- Recruiter saves/bookmarks

These signals help identify candidates who are both qualified and likely to engage with hiring processes.

---

# Feature 5: Availability Signals

Availability signals estimate hiring readiness.

Signals include:

- Open-to-work status
- Notice period duration
- Relocation willingness
- Preferred work mode

Candidates who are easier to engage and onboard receive higher availability scores.

---

# Score Aggregation

The final ranking score is generated through a weighted combination of all feature scores.

```
Final Score =
    Semantic Relevance
  + Career Relevance
  + Experience Fit
  + Behavioral Signals
  + Availability Signals
```

The weighting strategy prioritizes technical relevance while still considering candidate engagement and hiring feasibility.

---

# Design Principles

The ranking system was designed around three key principles:

### 1. Evidence Over Buzzwords

The system prioritizes demonstrated project and career experience rather than self-declared interests.

### 2. Production Experience Matters

Candidates with experience building and deploying AI systems are rewarded more heavily than candidates with only theoretical exposure.

### 3. Recruitability Matters

Strong technical candidates are valuable, but responsiveness and hiring readiness are also important signals in practical recruiting workflows.

---

# Output

The final system produces:

- Ranked candidate leaderboard
- Candidate scores
- Feature-level score explanations
- CSV export
- XLSX export

This enables recruiters to efficiently identify and review the most relevant candidates for AI and ML-focused roles.
