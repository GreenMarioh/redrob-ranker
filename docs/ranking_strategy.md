# Ranking Strategy

## Objective

Rank the top 100 candidates from a pool of 100,000 candidates for the role:

**Senior AI Engineer – Founding Team (Redrob AI)**

The goal is not keyword matching.

The goal is identifying candidates who demonstrate:

- Applied AI/ML experience
- Retrieval/Search/Ranking exposure
- Product engineering mindset
- Strong availability and engagement signals
- High likelihood of being successfully hired

---

# Dataset Structure

Each candidate contains:

```text
candidate_id
profile
career_history
education
skills
certifications
languages
redrob_signals
```

---

# Feature Importance Assessment

## Tier 1 Features (Highest Importance)

### Profile

Relevant fields:

- summary
- current_title
- current_company
- years_of_experience

Used to estimate:

- seniority
- AI relevance
- product experience
- role alignment

---

### Career History

Most important field in the dataset.

Relevant fields:

- company
- title
- description
- duration

Career descriptions contain the strongest evidence of:

- retrieval systems
- ranking systems
- recommendation systems
- search infrastructure
- production ML

Examples:

- Built recommendation systems
- Implemented retrieval pipelines
- Designed ranking infrastructure
- Developed search systems

These signals should outweigh simple keyword matching.

---

### Skills

Useful but potentially noisy.

Skills should support evidence found elsewhere.

Examples:

Good:

- Retrieval
- Search
- Ranking
- Recommendation Systems
- Elasticsearch
- OpenSearch
- Pinecone
- Weaviate
- Qdrant
- Milvus
- FAISS
- BM25
- Python

Examples of weak standalone evidence:

- Prompt Engineering
- ChatGPT
- LangChain

Skills alone should never determine ranking.

---

### Redrob Signals

Behavioral signals are critical.

Important fields:

- open_to_work_flag
- recruiter_response_rate
- last_active_date
- github_activity_score
- notice_period_days
- interview_completion_rate
- saved_by_recruiters_30d

These estimate:

- candidate availability
- candidate quality
- hiring likelihood

---

# Tier 2 Features

## Education

Useful for tie-breaking.

Potential indicators:

- Computer Science
- AI
- ML
- Data Science

Should not outweigh professional experience.

---

## Certifications

Useful but low importance.

Examples:

- AWS
- Kubernetes
- MLOps
- Cloud certifications

Used as supplementary evidence only.

---

# Tier 3 Features

## Languages

Minimal ranking value.

Expected to contribute little to candidate quality assessment.

---

# Implemented Ranking Components

## 1. Semantic Fit Score (Weight: 25%)

Measures alignment between:

- JD requirements
- Profile summary
- Career descriptions
- Skills

Primary focus:

- ranking systems
- retrieval systems
- recommendation systems
- production AI

All keyword sets are expanded through a centralized synonym registry (`features/synonyms.py`) that maps canonical terms to domain-equivalent variations (e.g., "retrieval" → "information retrieval", "dense retrieval", "sparse retrieval"). This expansion is applied across all feature modules.

Non-technical titles (e.g., "Graphic Designer", "Accountant") receive a negative penalty.

---

## 2. Career Relevance Score (Weight: 25%)

Measures actual work evidence from career history descriptions rather than self-declared interests.

Tiered keyword matching:

- High-value terms (×5): ranking, retrieval, recommendation, re-ranking, embedding
- Medium-value terms (×2): machine learning, xgboost, lightgbm, pytorch, tensorflow, nlp
- Data terms (×1): spark, kafka, airflow, data pipeline

All term sets are expanded via the synonym registry.

---

## 3. Experience Fit Score (Weight: 15%)

A composite score combining three sub-signals:

- **Years of experience band** (40%): Sweet spot is 5–9 years (score 1.0). 3–5 or 9–12 years score 0.7. Outside that scores 0.3.
- **Title relevance** (30%): Non-technical titles score 0.0. AI/ML-related titles score 1.0. Others score 0.5.
- **Retrieval experience depth** (30%): Counts retrieval/search/ranking/vector keywords across career history. Normalized to [0, 1] with cap at 5 hits.

Based on JD preference for the 5–9 year range.

---

## 4. Behavioral Score (Weight: 20%)

Derived from:

- recruiter response rate
- interview completion rate
- GitHub activity score (normalized, capped at 100)
- recruiter saves in last 30 days (normalized, capped at 20)

All four signals are averaged to produce a [0, 1] score.

Purpose:

Estimate real-world hireability.

---

## 5. Availability Score (Weight: 15%)

Derived from:

- open-to-work flag (+0.4)
- notice period (≤30d: +0.3, ≤60d: +0.2, ≤90d: +0.1)
- relocation willingness (+0.2)
- work mode flexibility (+0.1 if not onsite-only)

Shorter notice periods and higher flexibility receive higher scores. Capped at 1.0.

---

## 6. Consistency / Honeypot Score (Multiplier)

Detects profile inconsistencies and applies a penalty multiplier (each flag reduces by 0.15, minimum 0.0).

Checks:

- Non-technical title claiming expert-level AI/ML skills
- Expert/Advanced proficiency with less than 3 months duration
- AI/ML title but no technical evidence in career history
- Impossible experience timelines (career months > 125% of stated years)
- Keyword stuffing (≥4 AI keywords in summary, 0 in career descriptions)

Candidates with major inconsistencies can have their score reduced to zero.

---

## Score Aggregation

```text
raw_score = 0.25 × Semantic + 0.25 × Career + 0.20 × Behavior + 0.15 × Experience + 0.15 × Availability

final_score = raw_score × Honeypot Multiplier
```

---

# Current Working Hypothesis

Strong candidates will usually show:

- 5–9 years experience
- Product-company background
- Search / retrieval / ranking experience
- Production engineering history
- Active platform engagement
- Reasonable notice period

Weak candidates will often show:

- Keyword stuffing
- Generic AI buzzwords
- No production evidence
- Purely non-technical careers
- Low engagement signals

---

# Guiding Principle

Career evidence > Skills

Behavior > Buzzwords

Retrieval / Ranking experience > Generic AI keywords

Real systems > Framework familiarity
