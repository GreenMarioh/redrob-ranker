from parsing.schema import Candidate

def experience_score(candidate: Candidate) -> float:
    score = 0.0

    years = candidate.profile.years_of_experience

    if 5 <= years <= 9:
        score += 1.0
    elif 3 <= years < 5:
        score += 0.7
    elif 9 < years <= 12:
        score += 0.7
    else:
        score += 0.3
    
    return score