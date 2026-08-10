from rapidfuzz import fuzz
from services.title_cache import get_cache


# -------------------------
# NORMALISE TITLE
# -------------------------

def _normalise(text: str) -> str:
    return " ".join(text.lower().strip().split())


# -------------------------
# RANK AUTOCOMPLETE RESULTS
# -------------------------

def rank_autocomplete_results(query: str, results: list):

    q = _normalise(query)

    def score(item):

        title = item.get("title") or item.get("name") or ""
        t = _normalise(title)

        if not t:
            return 0

        score = 0

        # -------------------------
        # EXACT TITLE
        # -------------------------

        if t == q:
            score += 1000

        # -------------------------
        # TITLE STARTS WITH QUERY
        # -------------------------

        elif t.startswith(q):
            score += 700

        # -------------------------
        # FIRST WORD STARTS WITH QUERY
        # -------------------------

        words = t.split()

        if words and words[0].startswith(q):
            score += 500

        # -------------------------
        # WORD STARTS WITH QUERY
        # -------------------------

        if any(word.startswith(q) for word in words):
            score += 250

        # -------------------------
        # FUZZY MATCH
        # -------------------------

        fuzzy_score = fuzz.WRatio(q, t)
        score += fuzzy_score * 0.5

        # -------------------------
        # POPULARITY
        # Small influence only
        # -------------------------

        popularity = item.get("popularity", 0)
        score += min(popularity, 100) * 0.2

        return score

    return sorted(results, key=score, reverse=True)


# -------------------------
# RANK NORMAL SEARCH RESULTS
# -------------------------

def rank_results(query: str, results: list):

    q = _normalise(query)

    def score(item):

        title = item.get("title") or item.get("name") or ""
        t = _normalise(title)

        if not t:
            return 0

        score = 0

        # -------------------------
        # EXACT TITLE
        # -------------------------

        if t == q:
            score += 1000

        # -------------------------
        # TITLE STARTS WITH QUERY
        # -------------------------

        if t.startswith(q):
            score += 400

        # -------------------------
        # WORD MATCHING
        # -------------------------

        q_words = set(q.split())
        t_words = set(t.split())

        overlap = len(q_words & t_words)

        score += overlap * 100

        # -------------------------
        # FUZZY MATCH
        # -------------------------

        fuzzy_score = fuzz.WRatio(q, t)
        score += fuzzy_score

        # -------------------------
        # POPULARITY
        # Small influence
        # -------------------------

        popularity = item.get("popularity", 0)
        score += min(popularity, 100) * 0.2

        return score

    return sorted(results, key=score, reverse=True)


# -------------------------
# DID YOU MEAN
# -------------------------

def did_you_mean_top3(query: str):

    cache = get_cache()

    if not cache:
        return []

    q = _normalise(query)
    q_words = set(q.split())

    scored = []

    # -------------------------
    # FIND CANDIDATES
    # -------------------------

    for item in cache:

        title = item.get("title") or ""

        if not title:
            continue

        t = _normalise(title)
        t_words = set(t.split())

        base = fuzz.WRatio(q, t)

        # -------------------------
        # MATCH CONDITIONS
        # -------------------------

        has_overlap = len(q_words & t_words) > 0
        prefix_match = t.startswith(q[:3])
        strong_match = base >= 60

        if not (has_overlap or prefix_match or strong_match):
            continue

        # -------------------------
        # SCORING
        # -------------------------

        score = base

        overlap = len(q_words & t_words)
        score += overlap * 20

        # Exact match
        if t == q:
            score += 100

        # Starts with entire query
        if t.startswith(q):
            score += 50

        # Starts with first four characters
        if t.startswith(q[:4]):
            score += 25

        # Short titles get a small preference
        if len(t.split()) <= 2:
            score += 8

        scored.append((score, title))

    if not scored:
        return []

    # -------------------------
    # SORT
    # -------------------------

    scored.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    best_score = scored[0][0]

    # -------------------------
    # RETURN TOP 3
    # -------------------------

    results = []
    seen = set()

    for score, title in scored:

        norm = _normalise(title)

        if norm in seen:
            continue

        # Keep results reasonably close
        # to the strongest match
        if score < max(60, best_score * 0.80):
            continue

        results.append(title)
        seen.add(norm)

        if len(results) == 3:
            break

    return results