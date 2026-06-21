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

### 1. Semantic Relevance

Measures AI/ML relevance using profile summaries, skills, and job descriptions.

Examples:

- Retrieval
- Ranking
- Recommendation Systems
- NLP
- Embeddings
- Vector Databases

---

### 2. Career Relevance

Measures actual work experience rather than self-declared interests.

Examples:

- Recommendation System development
- Search Engineering
- Production ML systems
- Retrieval infrastructure
- Data engineering supporting ML workloads

---

### 3. Experience Fit

Measures alignment between candidate seniority and target role requirements.

Factors include:

- Years of experience
- Career progression
- Current role level

---

### 4. Behavioral Signals

Measures recruiter engagement and candidate responsiveness.

Examples:

- Recruiter response rate
- Interview completion rate
- GitHub activity
- Recruiter saves

---

### 5. Availability Signals

Measures hiring readiness.

Examples:

- Open-to-work status
- Notice period
- Relocation willingness
- Work mode preferences

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

├── data/
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
│   └── scorer.py
│
├── ranking/
│   ├── rank.py
│   ├── explanations.py
│   └── exporter.py
│
├── scripts/
│   ├── explore_top_candidates.py
│   ├── rank_10000.py
│   └── export_submission.py
│
├── outputs/
│
└── docs/
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
pip install pandas openpyxl
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
- Ranked Candidate CSV
- Ranked Candidate XLSX
- Methodology Documentation
- Architecture Documentation
- Results Documentation
- Presentation Deck (PDF)

```

```
