import sqlite3
from pathlib import Path

DB_FILE = 'magazine.db'

def get_connection():
    """
    Return a sqlite3 connection with row factory set to sqlite3.Row.
    """
    # Ensure the database file directory exists (useful in some test setups)
    db_path = Path(DB_FILE)
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """
    Create authors, magazines, and articles tables with proper foreign keys.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON;")

    # Authors table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """
    )

    # Magazines table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS magazines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL
        );
        """
    )

    # Articles table with foreign keys to authors and magazines
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            magazine_id INTEGER NOT NULL,
            FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
            FOREIGN KEY (magazine_id) REFERENCES magazines(id) ON DELETE CASCADE
        );
        """
    )

    conn.commit()
    conn.close()
