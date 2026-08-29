import hashlib
from datetime import datetime, timezone

import requests

from ..config import YC_KEYWORDS, SPEEDRUN_KEYWORDS


X_SEARCH_URL = "https://api.x.com/2/tweets/search/recent"


def build_search_query():
    """
    Build a search query for recent public X posts mentioning YC
    or Speedrun.

    Retweets and replies are excluded because we primarily want
    original founder/company announcements.
    """

    keywords = YC_KEYWORDS + SPEEDRUN_KEYWORDS

    keyword_query = " OR ".join(
        f'"{keyword}"'
        for keyword in keywords
    )

    return f"({keyword_query}) -is:retweet -is:reply"


def classify_post(text: str):
    """
    Classify a post as YC, Speedrun, or unknown based on keywords.
    """

    normalized = text.lower()

    if any(keyword.lower() in normalized for keyword in YC_KEYWORDS):
        return "YC"

    if any(
        keyword.lower() in normalized
        for keyword in SPEEDRUN_KEYWORDS
    ):
        return "Speedrun"

    return "Unknown"


def fetch_x_posts(bearer_token: str, max_results: int = 100):
    """
    Retrieve recent public X posts matching YC/Speedrun keywords.

    X's recent-search endpoint covers recent posts. The application
    database handles duplicate prevention across polling cycles.
    """

    if not bearer_token:
        print("X_BEARER_TOKEN is not configured.")
        return []

    query = build_search_query()

    headers = {
        "Authorization": f"Bearer {bearer_token}",
    }

    params = {
        "query": query,
        "max_results": max(10, min(max_results, 100)),
        "tweet.fields": "created_at,author_id,conversation_id",
        "expansions": "author_id",
        "user.fields": "name,username",
    }

    response = requests.get(
        X_SEARCH_URL,
        headers=headers,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    users = {
        user["id"]: user
        for user in payload.get("includes", {}).get("users", [])
    }

    posts = []

    for tweet in payload.get("data", []):
        author = users.get(tweet.get("author_id"), {})

        text = tweet.get("text", "")
        category = classify_post(text)

        posts.append(
            {
                "post_id": tweet.get("id"),
                "text": text,
                "source": "X",
                "category": category,
                "author_id": tweet.get("author_id"),
                "author_name": author.get("name", ""),
                "author_username": author.get("username", ""),
                "created_at": tweet.get(
                    "created_at",
                    datetime.now(timezone.utc).isoformat(),
                ),
                "url": (
                    f"https://x.com/"
                    f"{author.get('username', 'i')}/status/"
                    f"{tweet.get('id', '')}"
                ),
            }
        )

    return posts


def make_signal_key(post):
    """
    Generate a stable ID for duplicate detection.
    """

    post_id = post.get("post_id")

    if post_id:
        raw = f"x:{post_id}"
    else:
        raw = (
            f"x:{post.get('author_username', '')}:"
            f"{post.get('text', '')}"
        )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()
