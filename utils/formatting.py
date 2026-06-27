IMAGE_BASE = "https://image.tmdb.org/t/p/w200"


# -------------------------
# IMAGE
# -------------------------

def poster_url(path):
    if not path:
        return "https://via.placeholder.com/100x150?text=No+Image"
    return f"{IMAGE_BASE}{path}"


# -------------------------
# PROVIDER NORMALISATION
# -------------------------

def normalize_provider_name(name: str) -> str:
    name = name.strip()

    replacements = {
        "Amazon Prime Video with Ads": "Amazon Prime Video",
        "Amazon Prime Video (Channel)": "Amazon Prime Video",
        "Netflix with Ads": "Netflix",
        "Netflix Basic with Ads": "Netflix",
        "Netflix Standard with Ads": "Netflix",
        "HBO Max Amazon Channel": "HBO Max",
        "Max": "HBO Max",
        "Apple TV Store": "Apple TV",
        "Google Play Movies": "Google Play",
    }

    if name in replacements:
        return replacements[name]

    if " with Ads" in name:
        return name.replace(" with Ads", "").strip()

    return name


# -------------------------
# PROVIDER HTML BUILDER
# -------------------------

def build_providers_html(providers_data):
    au = providers_data.get("results", {}).get("AU")

    if not au:
        return "<p><i>No streaming data available in Australia.</i></p>"

    html = ""

    for key, label in {
        "flatrate": "Streaming",
        "rent": "Rent",
        "buy": "Buy"
    }.items():

        if key not in au:
            continue

        seen = set()
        section = ""

        for p in au[key]:
            name = normalize_provider_name(p["provider_name"])

            if name in seen:
                continue

            seen.add(name)
            section += f"<li>{name}</li>"

        if section:
            html += f"<h3>{label}</h3><ul>{section}</ul>"

    return html or "<p>No providers found.</p>"