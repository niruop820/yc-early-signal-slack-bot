import os
from dotenv import load_dotenv

load_dotenv()

# Slack
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "")

# Monitoring
CHECK_INTERVAL_HOURS = int(os.getenv("CHECK_INTERVAL_HOURS", "8"))

# YC
YC_DIRECTORY_URL = "https://www.ycombinator.com/companies"

# Keywords used for early YC/Speedrun signal detection
YC_KEYWORDS = [
    "y combinator",
    "ycombinator",
    "yc s26",
    "yc w26",
    "yc s25",
    "yc w25",
    "accepted into yc",
    "got into yc",
    "got into y combinator",
    "backed by y combinator",
    "backed by yc",
]

SPEEDRUN_KEYWORDS = [
    "yc speedrun",
    "speedrun batch",
    "speedrun",
    "backed by speedrun",
]
