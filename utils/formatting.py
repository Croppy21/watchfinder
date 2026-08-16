IMAGE_BASE = "https://image.tmdb.org/t/p/w200"
PROVIDER_URLS = {
    "Netflix": "https://www.netflix.com/",
    "Amazon Prime Video": "https://www.primevideo.com/",
    "Disney+": "https://www.disneyplus.com/",
    "Apple TV": "https://tv.apple.com/",
    "HBO Max": "https://www.max.com/",
    "YouTube": "https://www.youtube.com/",
    "Foxtel": "https://www.foxtel.com.au/",
    "Google Play": "https://play.google.com/store/movies",
    "Stan": "https://www.stan.com.au/",
    "Binge": "https://binge.com.au/",
    "Paramount+": "https://www.paramountplus.com/",
    "BritBox": "https://www.britbox.com/",
    "MUBI": "https://mubi.com/",
    "SBS": "https://www.sbs.com.au/ondemand/",
    "Fetch": "https://www.fetch.com.au/",
}

def poster_url(path):
    if not path:
        return "https://via.placeholder.com/100x150?text=No+Image"
    return f"{IMAGE_BASE}{path}"


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
        "Paramount Plus Premium": "Paramount+",
        "Paramount Plus": "Paramount+",
        "Paramount Plus Basic": "Paramount+",
        "Paramount+ Amazon Channel": "Paramount+"
    }

    if name in replacements:
        return replacements[name]

    if " with Ads" in name:
        return name.replace(" with Ads", "").strip()

    return name

IMAGE_BASE = "https://image.tmdb.org/t/p/w200"
PROVIDER_LOGO_BASE = "https://image.tmdb.org/t/p/w92"


def poster_url(path):
    if not path:
        return "https://via.placeholder.com/100x150?text=No+Image"
    return f"{IMAGE_BASE}{path}"


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
        "Paramount Plus Premium": "Paramount+",
        "Paramount Plus": "Paramount+",
        "Paramount Plus Basic": "Paramount+",
        "Paramount+ Amazon Channel": "Paramount+"
    }

    if name in replacements:
        return replacements[name]

    if " with Ads" in name:
        return name.replace(" with Ads", "").strip()

    return name


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

            logo_path = p.get("logo_path")

            if logo_path:
                logo = (
                    f'<img src="{PROVIDER_LOGO_BASE}{logo_path}" '
                    f'alt="{name}" class="provider-logo">'
                )
            else:
                logo = ""

            provider_url = PROVIDER_URLS.get(name)

            if provider_url:
                section += f"""
                    <a
                        href="{provider_url}"
                        class="provider-card"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {logo}
                        <span>{name}</span>
                    </a>
                """
            else:
                section += f"""
                    <div class="provider-card">
                        {logo}
                        <span>{name}</span>
                    </div>
                """

        if section:
            html += f"""
                <h3>{label}</h3>
                <div class="providers">
                    {section}
                </div>
            """

    return html or "<p>No providers found.</p>"