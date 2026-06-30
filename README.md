# Redrob Candidate Ranking System

## Overview

This project ranks candidates for AI, Machine Learning, Search, Retrieval, Recommendation Systems, and Applied AI Engineering roles.

The system processes large-scale candidate datasets, extracts meaningful signals from candidate profiles, and produces an explainable ranked leaderboard of the most relevant candidates.

The final pipeline successfully processed and ranked **100,000 candidate profiles** and generated submission-ready CSV/XLSX outputs.

---

## Problem Statement

Recruiters often need to identify highly relevant candidates from a large pool of applicants.

Traditional keyword matching produces noisy results because:

- Job titles can be misleading
- Candidates may use AI buzzwords without relevant experience
- Technical fit alone does not guarantee recruiter responsiveness
- Hiring readiness varies significantly across candidates

Our goal was to build an explainable ranking system that combines technical relevance, career evidence, engagement signals, and hiring readiness.

---

## Solution

The system evaluates candidates using five independent signals:

### 1. Semantic Relevance (Weight: 25%)

Measures AI/ML relevance using profile summaries, skills, and job descriptions.

All keyword sets are expanded through a curated synonym registry that maps domain-equivalent terms (e.g., "retrieval" expands to include "information retrieval", "dense retrieval", "sparse retrieval").

Examples:

- Retrieval
- Ranking
- Recommendation Systems
- NLP
- Embeddings
- Vector Databases

---

### 2. Career Relevance (Weight: 25%)

Measures actual work experience rather than self-declared interests.

Examples:

- Recommendation System development
- Search Engineering
- Production ML systems
- Retrieval infrastructure
- Data engineering supporting ML workloads

---

### 3. Experience Fit (Weight: 15%)

Measures alignment between candidate seniority and target role requirements.

Factors include:

- Years of experience
- Career progression
- Current role level

---

### 4. Behavioral Signals (Weight: 20%)

Measures recruiter engagement and candidate responsiveness.

Examples:

- Recruiter response rate
- Interview completion rate
- GitHub activity
- Recruiter saves

---

### 5. Availability Signals (Weight: 15%)

Measures hiring readiness.

Examples:

- Open-to-work status
- Notice period
- Relocation willingness
- Work mode preferences

---

### 6. Profile Consistency / Honeypot Detection (Multiplier)

Detects profile inconsistencies and applies a penalty multiplier on the final score.

Checks include:

- Non-technical title claiming expert-level AI/ML skills
- Expert proficiency with near-zero listed duration
- AI/ML title but no technical evidence in career history
- Impossible experience timelines
- Keyword stuffing (summary packed with buzzwords, career history empty)

Candidates with multiple inconsistencies can have their score reduced to zero.

---

### Score Aggregation

The final score is computed as:

```text
Final Score = (0.25 × Semantic + 0.25 × Career + 0.20 × Behavior + 0.15 × Experience + 0.15 × Availability) × Honeypot Multiplier
```

The honeypot multiplier ranges from 1.0 (no penalty) to 0.0 (maximum penalty), with each detected inconsistency reducing it by 0.15.

---

## System Architecture

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

## Project Structure

```text
redrob-ranker/
│
├── data/
│   └── raw/                          # Raw candidate JSONL dataset
│
├── parsing/
│   ├── schema.py                     # Candidate dataclasses
│   └── loader.py                     # JSONL/JSON data loading
│
├── features/
│   ├── semantic.py                   # Semantic keyword relevance scoring
│   ├── career_relevance.py           # Career history evidence scoring
│   ├── experience.py                 # Experience fit scoring
│   ├── behavior.py                   # Behavioral signal scoring
│   ├── availability.py               # Availability signal scoring
│   ├── honeypot.py                   # Profile consistency / honeypot detection
│   ├── synonyms.py                   # Centralized synonym expansion registry
│   └── scorer.py                     # Weighted score aggregation
│
├── ranking/
│   ├── rank.py                       # Candidate ranking engine
│   ├── explanations.py               # Per-candidate score explanations
│   └── exporter.py                   # DataFrame export utility
│
├── scripts/
│   ├── export_submission.py          # Main pipeline — generates submission files
│   ├── rank_10000.py                 # Quick ranking on first 10K candidates
│   ├── explore_top_candidates.py     # Detailed view of top 5 candidates
│   └── explore_bottom_candidates.py  # Detailed view of bottom 5 candidates
│
├── tests/
│   ├── test_loader.py
│   ├── test_experience.py
│   ├── test_honeypot.py
│   └── debug_semantic.py
│
├── notebooks/
│   ├── schema_exploration.ipynb
│   └── audit_top_candidates.ipynb
│
├── outputs/                          # Generated ranked CSV/XLSX files
├── customOutput/                     # Debug and analysis outputs
├── docs/                             # Architecture, methodology, results docs
│
├── requirements.txt
├── submission_metadata.yaml
├── app.py                            # Streamlit Web Dashboard
└── README.md
```

---

## Results

### Dataset Size

- 100,000 Candidate Profiles

### Output Formats

- CSV
- XLSX

### Top Ranked Candidate Types

- Staff Machine Learning Engineers
- Senior Applied Scientists
- Senior NLP Engineers
- Search Engineers
- Recommendation Systems Engineers
- AI Specialists

The final rankings consistently surfaced highly relevant AI and Machine Learning candidates while filtering out unrelated profiles.

---

## Running The Pipeline

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Generate Submission Files

```bash
python scripts/export_submission.py
```

Generated files:

```text
outputs/
├── ranked_candidates.csv
└── ranked_candidates.xlsx
```

### Live Sandbox Deployment

You can explore the ranked candidates and their detailed scoring breakdown visually via our deployed Streamlit application:

🔗 **[Live Demo: Redrob Ranker Sandbox](https://redrobranker.streamlit.app/)**

---

## Design Principles

### Evidence Over Buzzwords

Candidates are rewarded for demonstrated work experience rather than simply mentioning AI-related technologies.

### Explainability

Every ranking can be decomposed into individual feature contributions.

### Recruiter-Centric Ranking

The system evaluates not only technical capability but also recruiter engagement and hiring readiness.

### Scalability

The architecture successfully scales to datasets containing 100,000+ candidate profiles.

---

## Team

- Mohnish Kumar
- Devesh Jaiswal
- Amrit Raj
- Pavitra Rajpoot

---

## Submission Artifacts

- GitHub Repository
- Interactive Streamlit Dashboard (`app.py`)
- Ranked Candidate CSV
- Ranked Candidate XLSX
- Methodology Documentation
- Architecture Documentation
- Results Documentation
- Presentation Deck (PDF)

```

```
