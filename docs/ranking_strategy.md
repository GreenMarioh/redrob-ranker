# Ranking Strategy v1

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

# Planned Ranking Components

## 1. Semantic Fit Score

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

---

## 2. Experience Fit Score

Measures:

- years of experience
- seniority
- role progression

Target range:

- 5 to 9 years

Based on JD preference.

---

## 3. Product Engineering Score

Rewards candidates with evidence of:

- shipping systems
- ownership
- production deployments
- product-company experience

Penalizes purely managerial profiles.

---

## 4. Retrieval / Ranking Score

Rewards evidence of:

- search systems
- retrieval systems
- recommendation engines
- vector search
- information retrieval

Expected to be one of the strongest positive signals.

---

## 5. Behavioral Score

Derived from:

- recruiter response rate
- activity recency
- interview completion rate
- recruiter saves
- GitHub activity

Purpose:

Estimate real-world hireability.

---

## 6. Availability Score

Derived from:

- notice period
- open-to-work status
- relocation preference

Shorter notice periods receive higher scores.

---

## 7. Consistency / Honeypot Score

Detects profile inconsistencies.

Examples:

- Marketing Manager with advanced AI skills
- Expert skills with near-zero duration
- Career descriptions contradicting titles
- Impossible experience timelines

Candidates with major inconsistencies receive penalties.

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
