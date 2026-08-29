import hashlib
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from ..config import YC_DIRECTORY_URL


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; YC-Early-Signal-Bot/1.0; "
        "+https://github.com/niruop820/yc-early-signal-slack-bot)"
    )
}


def fetch_yc_directory():
    """
    Fetch the public YC company directory.

    Returns a list of detected company records.
    """
    response = requests.get(
        YC_DIRECTORY_URL,
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    companies = []

    # YC pages contain company links under /companies/<slug>.
    seen = set()

    for link in soup.select('a[href^="/companies/"]'):
        href = link.get("href", "").strip()

        if not href or href.rstrip("/") == "/companies":
            continue

        if href in seen:
            continue

        name = link.get_text(" ", strip=True)

        if not name:
            continue

        seen.add(href)

        companies.append(
            {
                "company_name": name,
                "source": "YC Directory",
                "url": f"https://www.ycombinator.com{href}",
                "description": "",
                "batch": "",
                "status": "Confirmed by YC",
                "detected_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    return companies


def make_signal_key(company):
    """
    Create a stable ID so the same YC company is not alerted repeatedly.
    """
    raw = (
        f"{company.get('company_name', '').lower().strip()}|"
        f"{company.get('url', '').lower().strip()}"
    )

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
