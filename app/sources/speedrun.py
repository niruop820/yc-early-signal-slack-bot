import hashlib
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


# Official a16z Speedrun website.
SPEEDRUN_URL = "https://speedrun.a16z.com/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; YC-Early-Signal-Bot/1.0; "
        "+https://github.com/niruop820/yc-early-signal-slack-bot)"
    )
}


def fetch_new_speedrun_companies():    """
    Fetch publicly visible companies from the a16z Speedrun website.

    The parser is intentionally modular so the source adapter can be
    updated if the website changes its HTML structure.
    """

    response = requests.get(
        SPEEDRUN_URL,
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    companies = []
    seen = set()

    # Look for links that appear to point to company/profile pages.
    for link in soup.find_all("a", href=True):
        href = link.get("href", "").strip()

        if not href:
            continue

        text = link.get_text(" ", strip=True)

        if not text:
            continue

        # Keep only likely company/profile links.
        if not any(
            keyword in href.lower()
            for keyword in [
                "company",
                "companies",
                "portfolio",
                "startup",
            ]
        ):
            continue

        if href.startswith("/"):
            full_url = f"https://speedrun.a16z.com{href}"
        elif href.startswith("http"):
            full_url = href
        else:
            continue

        if full_url in seen:
            continue

        seen.add(full_url)

        companies.append(
            {
                "company_name": text,
                "source": "a16z Speedrun",
                "url": full_url,
                "description": "",
                "batch": "",
                "status": "Confirmed by a16z Speedrun",
                "detected_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    return companies


def make_signal_key(company):
    """
    Create a stable identifier for duplicate prevention.
    """

    raw = (
        f"{company.get('company_name', '').lower().strip()}|"
        f"{company.get('url', '').lower().strip()}"
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()
