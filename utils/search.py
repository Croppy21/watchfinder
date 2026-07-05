from rapidfuzz import fuzz
from services.title_cache import get_cache


# -------------------------
# RANK SEARCH RESULTS
# -------------------------
def rank_results(query: str, results: list):

    q = query.lower().strip()

    def score(item):
        title = item.get("title") or item.get("name") or ""
        popularity = item.get("popularity", 0)

        t = title.lower()

        fuzzy_score = fuzz.WRatio(q, t)

        # popularity is small influence only
        return (fuzzy_score * 10) + (popularity * 0.2)

    return sorted(results, key=score, reverse=True)


# -------------------------
# DID YOU MEAN (FINAL FIXED VERSION)
# -------------------------
def did_you_mean_top3(query: str):

    cache = get_cache()
    if not cache:
        return []

    q = query.lower().strip()
    q_words = set(q.split())

    scored = []

    # -------------------------
    # STEP 1: STRICT CANDIDATE FILTER (IMPORTANT FIX)
    # -------------------------
    for item in cache:
        title = item.get("title") or ""
        if not title:
            continue

        t = title.lower()
        t_words = set(t.split())

        base = fuzz.WRatio(q, t)

        # HARD GATES (THIS FIXES YOUR ISSUE)
        has_overlap = len(q_words & t_words) > 0
        prefix_match = t.startswith(q[:3])
        strong_match = base >= 60

        if not (has_overlap or prefix_match or strong_match):
            continue

        # -------------------------
        # STEP 2: SCORING
        # -------------------------
        score = base

        overlap = len(q_words & t_words)
        score += overlap * 20

        if t == q:
            score += 100

        if t.startswith(q[:4]):
            score += 25

        if len(t.split()) <= 2:
            score += 8

        scored.append((score, title))

    if not scored:
        return []

    scored.sort(reverse=True, key=lambda x: x[0])

    best_score = scored[0][0]

    results = []
    seen = set()

    for score, title in scored:

        norm = title.lower()

        if norm in seen:
            continue

        # tight clustering
        if score < max(60, best_score * 0.80):
            continue

        results.append(title)
        seen.add(norm)

        if len(results) == 3:
            break

    return results