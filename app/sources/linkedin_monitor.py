"""
LinkedIn monitor for YC / Speedrun founder and company signals.

This module is intentionally separated from the other sources so
additional social platforms can be added later.
"""

import os
import requests


LINKEDIN_API_URL = "https://api.linkedin.com/v2"


def get_access_token():
    """Read LinkedIn access token from environment variables."""
    return os.getenv("LINKEDIN_ACCESS_TOKEN")


def search_linkedin_signals(keywords=None):
    """
    Search LinkedIn for YC / Speedrun related signals.

    Note:
    LinkedIn's official API has access restrictions for search/discovery.
    This function provides the integration point for an approved
    LinkedIn API or data provider.
    """
    if keywords is None:
        keywords = [
            "YC S26",
            "Y Combinator",
            "Speedrun",
            "YC W26",
            "YC founder",
        ]

    token = get_access_token()

    if not token:
        return []

    # Placeholder for approved LinkedIn API integration.
    # Do not scrape LinkedIn without permission.
    return []


def detect_early_founder_signal(post):
    """
    Determine whether a LinkedIn post appears to be an early
    YC/Speedrun founder announcement.
    """
    text = post.get("text", "").lower()

    keywords = [
        "got into yc",
        "accepted into yc",
        "accepted to yc",
        "y combinator",
        "yc s26",
        "yc w26",
        "speedrun",
        "backed by y combinator",
    ]

    return any(keyword in text for keyword in keywords)
