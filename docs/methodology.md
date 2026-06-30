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

All keyword sets are expanded through a centralized synonym registry (`features/synonyms.py`) that maps canonical terms to their domain-equivalent variations (e.g., "retrieval" expands to include "information retrieval", "dense retrieval", "sparse retrieval"). This expansion is applied across all feature modules to improve recall without sacrificing precision.

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

# Feature 6: Profile Consistency / Honeypot Detection

The honeypot module detects profile inconsistencies that suggest fabricated or inflated candidate profiles.

Consistency checks include:

- Non-technical title (e.g., "Marketing Manager") claiming expert-level AI/ML skills
- Skill proficiency marked as "Expert" or "Advanced" with less than 3 months of listed duration
- AI/ML-related title but zero technical evidence in career history descriptions
- Total career months significantly exceeding stated years of experience (timeline fabrication)
- Summary densely packed with AI keywords but career descriptions containing no relevant content (keyword stuffing)

Each detected flag reduces a consistency multiplier by 0.15. The multiplier starts at 1.0 and is capped at a minimum of 0.0.

This penalty is applied multiplicatively on the final score, ensuring that candidates with major inconsistencies are ranked lower regardless of their keyword density.

---

# Score Aggregation

The final ranking score is generated through a weighted combination of all feature scores, multiplied by the honeypot consistency penalty.

```
raw_score =
    0.25 × Semantic Relevance
  + 0.25 × Career Relevance
  + 0.20 × Behavioral Signals
  + 0.15 × Experience Fit
  + 0.15 × Availability Signals

final_score = raw_score × Honeypot Multiplier
```

The weighting strategy prioritizes technical relevance (semantic + career = 50%) while incorporating recruiter engagement and hiring feasibility. The honeypot multiplier ensures that inconsistent profiles are penalized regardless of keyword density.

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
