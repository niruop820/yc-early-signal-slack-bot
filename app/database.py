import sqlite3
from pathlib import Path
from typing import Optional


# Keep the local database outside the source-code files.
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "signals.db"


def get_connection():
    """Create a connection to the local SQLite database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the database tables if they do not already exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_key TEXT UNIQUE NOT NULL,
                company_name TEXT,
                founder_name TEXT,
                source TEXT NOT NULL,
                url TEXT,
                description TEXT,
                batch TEXT,
                status TEXT,
                detected_at TEXT NOT NULL,
                alert_sent INTEGER DEFAULT 0
            )
            """
        )
        connection.commit()


def signal_exists(signal_key: str) -> bool:
    """Return True when this signal has already been recorded."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT 1 FROM signals WHERE signal_key = ? LIMIT 1",
            (signal_key,),
        ).fetchone()

    return row is not None


def save_signal(
    signal_key: str,
    source: str,
    detected_at: str,
    company_name: Optional[str] = None,
    founder_name: Optional[str] = None,
    url: Optional[str] = None,
    description: Optional[str] = None,
    batch: Optional[str] = None,
    status: Optional[str] = None,
    alert_sent: bool = False,
):
    """Save a newly detected signal."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO signals (
                signal_key,
                company_name,
                founder_name,
                source,
                url,
                description,
                batch,
                status,
                detected_at,
                alert_sent
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                signal_key,
                company_name,
                founder_name,
                source,
                url,
                description,
                batch,
                status,
                detected_at,
                int(alert_sent),
            ),
        )
        connection.commit()


def mark_alert_sent(signal_key: str):
    """Mark a signal as successfully delivered to Slack."""
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE signals
            SET alert_sent = 1
            WHERE signal_key = ?
            """,
            (signal_key,),
        )
        connection.commit()
