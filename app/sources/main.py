"""
YC Early Signal Slack Bot

Main monitoring loop.

Sources:
- YC Directory
- YC Speedrun
- X
- LinkedIn

The bot keeps checking for new signals and sends only
new/unique alerts to Slack.
"""

import time
import logging

from app.config import POLL_INTERVAL_HOURS
from app.database import init_db, is_seen, mark_seen
from app.alerts import send_slack_alert

from app.sources.yc_directory import fetch_new_yc_companies
from app.sources.speedrun import fetch_new_speedrun_companies
from app.sources.x_monitor import search_x_signals
from app.sources.linkedin_monitor import search_linkedin_signals


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def process_signal(signal):
    """
    Process one signal.

    A signal is sent to Slack only if it has not already
    been stored in the local database.
    """

    signal_id = signal.get("id")

    if not signal_id:
        logger.warning("Signal has no ID: %s", signal)
        return

    if is_seen(signal_id):
        logger.info("Already seen: %s", signal_id)
        return

    logger.info("New signal detected: %s", signal.get("company"))

    try:
        send_slack_alert(signal)
        mark_seen(signal_id)

        logger.info(
            "Slack alert sent successfully: %s",
            signal.get("company"),
        )

    except Exception as error:
        logger.exception(
            "Failed to process signal %s: %s",
            signal_id,
            error,
        )


def run_monitoring_cycle():
    """
    Run one complete monitoring cycle across all sources.
    """

    logger.info("Starting monitoring cycle...")

    sources = [
        ("YC Directory", fetch_new_yc_companies),
        ("YC Speedrun", fetch_new_speedrun_companies),
        ("X", search_x_signals),
        ("LinkedIn", search_linkedin_signals),
    ]

    for source_name, fetch_function in sources:

        logger.info("Checking %s...", source_name)

        try:
            signals = fetch_function()

            if not signals:
                logger.info(
                    "No new signals from %s.",
                    source_name,
                )
                continue

            for signal in signals:
                process_signal(signal)

        except Exception as error:
            logger.exception(
                "Error while checking %s: %s",
                source_name,
                error,
            )

    logger.info("Monitoring cycle completed.")


def main():
    """
    Start continuous monitoring.
    """

    init_db()

    logger.info("====================================")
    logger.info("YC Early Signal Slack Bot started")
    logger.info("====================================")

    while True:

        run_monitoring_cycle()

        sleep_seconds = POLL_INTERVAL_HOURS * 60 * 60

        logger.info(
            "Sleeping for %s hours...",
            POLL_INTERVAL_HOURS,
        )

        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()
