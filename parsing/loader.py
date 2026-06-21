import json
from parsing.schema import (
    Candidate,
    Profile,
    CareerEntry,
    Education,
    Skill,
    Certification,
    Language,
    SalaryRange,
    RedrobSignals,
)

def parse_profile(data: dict) -> Profile:
    return Profile(**data)

def parse_career_history(data: list) -> list[CareerEntry]:
    return [CareerEntry(**entry) for entry in data]

def parse_education(data: list) -> list[Education]:
    return [Education(**entry) for entry in data]

def parse_skills(data: list) -> list[Skill]:
    return [Skill(**entry) for entry in data]

def parse_certifications(data: list) -> list[Certification]:
    return [Certification(**entry) for entry in data]

def parse_languages(data: list) -> list[Language]:
    return [Language(**entry) for entry in data]

def parse_redrob_signals(data: dict) -> RedrobSignals:
    # Safely extract and map nested object before unpacking the rest
    salary_data = data["expected_salary_range_inr_lpa"]
    salary = SalaryRange(
        min=salary_data["min"],
        max=salary_data["max"],
    )
    
    # We can clone the dict, swap out the nested object with the actual dataclass instance, 
    # and unpack it just like the others instead of typing 23 lines manually.
    signals_kwargs = data.copy()
    signals_kwargs["expected_salary_range_inr_lpa"] = salary
    
    return RedrobSignals(**signals_kwargs)

def parse_candidate(data: dict) -> Candidate:
    return Candidate(
        candidate_id=data["candidate_id"],
        profile=parse_profile(data["profile"]),
        career_history=parse_career_history(data["career_history"]),
        education=parse_education(data["education"]),
        skills=parse_skills(data["skills"]),
        certifications=parse_certifications(data["certifications"]),
        languages=parse_languages(data["languages"]),
        redrob_signals=parse_redrob_signals(data["redrob_signals"]),
    )

def load_sample_candidates(path: str) -> list[Candidate]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [parse_candidate(candidate) for candidate in raw]

def load_candidates_jsonl(path: str, limit: int | None = None):
    candidates = []

    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            candidate_dict = json.loads(line)

            candidates.append(
                parse_candidate(candidate_dict)
            )

            if limit is not None and len(candidates) >= limit:
                break

    return candidates