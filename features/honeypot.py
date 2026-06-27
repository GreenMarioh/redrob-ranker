from parsing.schema import Candidate
from features.synonyms import expand_keyword_set, NEW_EXPERT_SKILL_KEYWORDS


# Titles that are definitively non-technical roles
NON_TECH_TITLES = {
    "marketing manager",
    "marketing executive",
    "content writer",
    "content strategist",
    "graphic designer",
    "accountant",
    "chartered accountant",
    "financial analyst",
    "operations manager",
    "operations executive",
    "hr manager",
    "hr executive",
    "human resources",
    "recruiter",
    "talent acquisition",
    "sales manager",
    "sales executive",
    "business development",
    "customer support",
    "customer success",
    "civil engineer",
    "mechanical engineer",
    "electrical engineer",
    "supply chain",
    "logistics",
    "legal counsel",
    "lawyer",
    "doctor",
    "physician",
    "teacher",
}

# Skills that suggest genuine hands-on AI/ML expertise
EXPERT_SKILL_KEYWORDS = expand_keyword_set({
    "retrieval",
    "ranking",
    "recommendation",
    "embedding",
    "vector database",
    "faiss",
    "pinecone",
    "weaviate",
    "qdrant",
    "milvus",
    "elasticsearch",
    "opensearch",
    "bm25",
    "pytorch",
    "tensorflow",
    "xgboost",
    "lightgbm",
    "mlops",
    "kubeflow",
    "spark",
    "kafka",
}) | NEW_EXPERT_SKILL_KEYWORDS

# Proficiency levels that claim high expertise
HIGH_PROFICIENCY_LEVELS = {"expert", "advanced"}


def honeypot_penalty(candidate: Candidate) -> float:
    """
    Detects profile inconsistencies and returns a penalty multiplier.

    Returns a value between 0.0 and 1.0:
      - 1.0 = no penalty (profile is consistent)
      - 0.0 = maximum penalty (extremely inconsistent profile)

    The penalty is applied as a multiplier on the final score in scorer.py.
    """
    flags = []

    flags += _check_non_tech_title_with_expert_skills(candidate)
    flags += _check_expert_skills_with_no_duration(candidate)
    flags += _check_title_career_mismatch(candidate)
    flags += _check_impossible_experience_timeline(candidate)
    flags += _check_keyword_stuffing(candidate)

    # Each flag reduces the multiplier. Start at 1.0, cap minimum at 0.0.
    penalty_per_flag = 0.15
    total_penalty = len(flags) * penalty_per_flag
    multiplier = max(1.0 - total_penalty, 0.0)

    return multiplier


def explain_honeypot(candidate: Candidate) -> list[str]:
    """
    Returns a human-readable list of inconsistency flags found on the profile.
    Useful for debugging and ranking explanations.
    """
    flags = []
    flags += _check_non_tech_title_with_expert_skills(candidate)
    flags += _check_expert_skills_with_no_duration(candidate)
    flags += _check_title_career_mismatch(candidate)
    flags += _check_impossible_experience_timeline(candidate)
    flags += _check_keyword_stuffing(candidate)
    return flags


# ---------------------------------------------------------------------------
# Individual check functions — each returns a list of flag strings
# ---------------------------------------------------------------------------

def _check_non_tech_title_with_expert_skills(candidate: Candidate) -> list[str]:
    """
    Flag: Non-technical current title but claims expert-level AI/ML skills.
    Example: 'Marketing Manager' with 'Expert' proficiency in PyTorch.
    """
    flags = []
    title = candidate.profile.current_title.lower()

    is_non_tech = any(nt in title for nt in NON_TECH_TITLES)
    if not is_non_tech:
        return flags

    for skill in candidate.skills:
        skill_name = skill.name.lower()
        if (
            skill.proficiency.lower() in HIGH_PROFICIENCY_LEVELS
            and any(kw in skill_name for kw in EXPERT_SKILL_KEYWORDS)
        ):
            flags.append(
                f"Non-technical title '{candidate.profile.current_title}' "
                f"claims expert-level skill '{skill.name}'."
            )
            break  # one flag is enough for this check

    return flags


def _check_expert_skills_with_no_duration(candidate: Candidate) -> list[str]:
    """
    Flag: Skill proficiency is 'Expert' or 'Advanced' but duration_months is
    suspiciously low (< 3 months). Suggests fabricated or inflated skills.
    """
    flags = []

    for skill in candidate.skills:
        if (
            skill.proficiency.lower() in HIGH_PROFICIENCY_LEVELS
            and skill.duration_months < 3
        ):
            flags.append(
                f"Skill '{skill.name}' is marked '{skill.proficiency}' "
                f"but has only {skill.duration_months} month(s) of listed duration."
            )

    return flags


def _check_title_career_mismatch(candidate: Candidate) -> list[str]:
    """
    Flag: Current title contains AI/ML keywords but career history descriptions
    have zero evidence of technical work. Suggests keyword-stuffed title.
    """
    flags = []

    title = candidate.profile.current_title.lower()
    title_looks_technical = any(kw in title for kw in EXPERT_SKILL_KEYWORDS)

    if not title_looks_technical:
        return flags

    # Check if any career entry description mentions technical content
    all_career_text = " ".join(
        (job.title + " " + job.description).lower()
        for job in candidate.career_history
    )

    has_technical_evidence = any(kw in all_career_text for kw in EXPERT_SKILL_KEYWORDS)

    if not has_technical_evidence:
        flags.append(
            f"Title '{candidate.profile.current_title}' suggests AI/ML expertise "
            f"but career history contains no technical evidence."
        )

    return flags


def _check_impossible_experience_timeline(candidate: Candidate) -> list[str]:
    """
    Flag: Total months from career history significantly exceeds what is possible
    given the candidate's stated years_of_experience. Detects timeline fabrication.
    Threshold: career months > (years_of_experience * 12) * 1.25 (25% buffer).
    """
    flags = []

    stated_years = candidate.profile.years_of_experience
    if stated_years <= 0:
        return flags

    stated_months = stated_years * 12
    career_months = sum(job.duration_months for job in candidate.career_history)

    # Allow 25% slack to account for overlapping or part-time roles
    if career_months > stated_months * 1.25:
        flags.append(
            f"Career history totals {career_months} months but stated experience "
            f"is only {stated_years} years ({int(stated_months)} months). "
            f"Possible fabricated timeline."
        )

    return flags


def _check_keyword_stuffing(candidate: Candidate) -> list[str]:
    """
    Flag: Profile summary is densely packed with AI keywords but career history
    descriptions have almost no relevant content. Classic buzzword padding pattern.
    """
    flags = []

    summary = candidate.profile.summary.lower()
    summary_hits = sum(1 for kw in EXPERT_SKILL_KEYWORDS if kw in summary)

    career_text = " ".join(
        job.description.lower() for job in candidate.career_history
    )
    career_hits = sum(1 for kw in EXPERT_SKILL_KEYWORDS if kw in career_text)

    # If summary is keyword-rich but career is barren, it's suspicious
    if summary_hits >= 4 and career_hits == 0:
        flags.append(
            f"Summary contains {summary_hits} AI/ML keyword(s) but career "
            f"descriptions have no supporting technical content. "
            f"Possible keyword stuffing."
        )

    return flags
