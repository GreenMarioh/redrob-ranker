# System Architecture

## Overview

The candidate ranking system is designed as a modular pipeline that transforms raw candidate data into an ordered list of highly relevant AI and Machine Learning candidates.

The architecture emphasizes:

- Scalability
- Explainability
- Modular feature engineering
- Reproducible ranking

The system successfully processes and ranks over 100,000 candidate profiles.

---

# High-Level Architecture

```text
                candidates.jsonl
                        │
                        ▼
                Data Loading Layer
                        │
                        ▼
                  Parsing Layer
                        │
                        ▼
             Structured Candidate Objects
                        │
                        ▼
              Feature Extraction Layer
                        │
                        ▼
                 Scoring Engine
                        │
                        ▼
                 Ranking Engine
                        │
                        ▼
                 Export Layer
                        │
                        ▼
        ranked_candidates.csv / .xlsx
```

---

# Component Breakdown

## 1. Data Loading Layer

### File

```text
parsing/loader.py
```

### Responsibilities

- Read candidate records from JSONL files
- Parse large datasets efficiently
- Convert raw JSON into structured Python objects

### Input

```text
candidates.jsonl
```

### Output

```text
List[Candidate]
```

---

## 2. Parsing Layer

### File

```text
parsing/schema.py
```

### Responsibilities

- Define all candidate-related dataclasses
- Ensure type consistency across the system
- Standardize candidate representation

### Core Entities

```text
Candidate
Profile
CareerEntry
Education
Skill
Certification
Language
RedrobSignals
```

### Output

Structured candidate objects used throughout the pipeline.

---

## 3. Feature Extraction Layer

### Directory

```text
features/
```

This layer computes individual ranking signals.

---

### Experience Module

```text
features/experience.py
```

Measures:

- Years of experience
- Seniority alignment
- Target experience range fit

Output:

```text
experience_score
```

---

### Semantic Module

```text
features/semantic.py
```

Measures:

- AI relevance
- ML relevance
- Retrieval relevance
- Recommendation relevance
- NLP relevance

Output:

```text
semantic_score
```

---

### Career Relevance Module

```text
features/career_relevance.py
```

Measures:

- Real-world AI experience
- Retrieval systems experience
- Recommendation systems experience
- Production ML exposure
- Data engineering relevance

Output:

```text
career_relevance_score
```

---

### Behavioral Module

```text
features/behavior.py
```

Measures:

- Recruiter response rate
- Interview completion rate
- GitHub activity
- Recruiter engagement

Output:

```text
behavior_score
```

---

### Availability Module

```text
features/availability.py
```

Measures:

- Open-to-work status
- Notice period
- Relocation preference
- Work-mode flexibility

Output:

```text
availability_score
```

---

### Honeypot / Consistency Module

```text
features/honeypot.py
```

Detects profile inconsistencies and returns a penalty multiplier.

Checks:

- Non-technical title with expert-level AI/ML skills
- Expert proficiency with near-zero duration
- AI/ML title but no technical evidence in career history
- Impossible experience timelines
- Keyword stuffing (summary packed with buzzwords, career history empty)

Output:

```text
honeypot_penalty (multiplier: 0.0 to 1.0)
```

Each detected flag reduces the multiplier by 0.15.

---

### Synonym Expansion Module

```text
features/synonyms.py
```

Centralized technical synonym registry used by all feature modules.

Responsibilities:

- Map canonical keywords to domain-equivalent terms
- Expand keyword sets and weighted keyword dicts
- Provide new keyword categories for additional coverage

Example:

```text
"retrieval" → {"retrieval", "information retrieval", "dense retrieval", "sparse retrieval"}
"faiss" → {"faiss", "annoy", "scann", "hnsw", "approximate nearest neighbor"}
```

---

# Scoring Engine

### File

```text
features/scorer.py
```

The scoring engine combines all extracted signals into a single ranking score using a weighted sum, then applies the honeypot consistency multiplier.

Formula:

```text
raw_score = 0.25 × semantic
          + 0.25 × career_relevance
          + 0.20 × behavior
          + 0.15 × experience
          + 0.15 × availability

final_score = raw_score × honeypot_penalty
```

Inputs:

```text
semantic_score
career_relevance_score
experience_score
behavior_score
availability_score
honeypot_penalty
```

Output:

```text
total_score
```

The weighting strategy prioritizes technical relevance (semantic + career = 50%) while preserving practical recruiting considerations (behavior + availability = 35%). The honeypot multiplier ensures inconsistent profiles are penalized regardless of keyword density.

---

# Ranking Engine

### File

```text
ranking/rank.py
```

Responsibilities:

- Score every candidate
- Sort candidates by descending score
- Generate final ranking order

Input:

```text
List[Candidate]
```

Output:

```text
Ranked Candidate List
```

---

# Explanation Engine

### File

```text
ranking/explanations.py
```

Responsibilities:

- Generate feature-level explanations
- Support debugging and analysis
- Improve model transparency

Example:

```text
Semantic Score: 48
Career Score: 24
Behavior Score: 0.64
Availability Score: 0.90
```

This module helps explain why a candidate received a particular rank.

---

# Export Layer

### File

```text
scripts/export_submission.py
```

Responsibilities:

- Generate final ranked outputs
- Create CSV submission file
- Create XLSX submission file

Outputs:

```text
outputs/ranked_candidates.csv
outputs/ranked_candidates.xlsx
```

---

# Project Structure

```text
redrob-ranker/
│
├── data/
│   └── raw/
│
├── parsing/
│   ├── schema.py
│   └── loader.py
│
├── features/
│   ├── semantic.py
│   ├── career_relevance.py
│   ├── experience.py
│   ├── behavior.py
│   ├── availability.py
│   ├── honeypot.py
│   ├── synonyms.py
│   └── scorer.py
│
├── ranking/
│   ├── rank.py
│   ├── explanations.py
│   └── exporter.py
│
├── scripts/
│   ├── export_submission.py
│   ├── rank_10000.py
│   ├── explore_top_candidates.py
│   └── explore_bottom_candidates.py
│
├── tests/
│
├── notebooks/
│
├── outputs/
│
├── customOutput/
│
└── docs/
```

---

# Design Decisions

## Modularity

Each ranking signal is implemented independently, making the system easier to debug and improve.

## Explainability

Every candidate score can be decomposed into individual feature contributions.

## Scalability

The architecture is capable of processing datasets containing tens of thousands of candidates.

## Recruiter-Centric Ranking

The system evaluates not only technical fit but also candidate responsiveness and hiring readiness.

---

# End-to-End Flow

```text
Raw Candidate Data
        │
        ▼
Structured Candidate Objects
        │
        ▼
Feature Extraction
        │
        ▼
Score Calculation
        │
        ▼
Candidate Ranking
        │
        ▼
CSV / XLSX Export
        │
        ▼
Recruiter Consumption
```

This architecture provides a complete and explainable pipeline for large-scale AI candidate ranking.
