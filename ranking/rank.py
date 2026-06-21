from features.scorer import total_score


def rank_candidates(candidates):

    ranked = []

    for candidate in candidates:
        ranked.append(
            (
                total_score(candidate),
                candidate
            )
        )

    ranked.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return ranked