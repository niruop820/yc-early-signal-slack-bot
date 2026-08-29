from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID


def send_slack_alert(
    company_name: str,
    founder_name: str,
    batch: str,
    source: str,
    status: str,
    url: str,
    description: str = "",
):
    """
    Send a YC/Speedrun detection alert to the configured Slack channel.
    """

    if not SLACK_BOT_TOKEN:
        print("Slack bot token is not configured.")
        return False

    if not SLACK_CHANNEL_ID:
        print("Slack channel ID is not configured.")
        return False

    client = WebClient(token=SLACK_BOT_TOKEN)

    # Use a special heading for early founder announcements.
    if "Early" in status or "early" in status:
        title = "🔥 EARLY YC SIGNAL — Founder Announced Before YC"
    else:
        title = "🟢 NEW YC / SPEEDRUN COMPANY"

    message = (
        f"*{title}*\n\n"
        f"*Company:* {company_name or 'Unknown'}\n"
        f"*Founder:* {founder_name or 'Unknown'}\n"
        f"*Batch:* {batch or 'Unknown'}\n"
        f"*Source:* {source}\n"
        f"*Status:* {status}\n"
    )

    if description:
        message += f"*Description:* {description}\n"

    if url:
        message += f"*Link:* {url}\n"

    try:
        client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            text=message,
        )

        print(f"Slack alert sent for: {company_name}")
        return True

    except SlackApiError as error:
        print(f"Slack API error: {error.response.get('error')}")
        return False
    except Exception as error:
        print(f"Unexpected Slack error: {error}")
        return False
