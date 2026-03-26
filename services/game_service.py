from datetime import datetime
import sqlite3

from data.db import get_connection
from utils.validators import validate_game_title


def add_game(title: str, platform: str = "", genre_mode: str = "", notes: str = ""):
    """
    Adds a game to the database.
    Returns: (success: bool, message: str)
    """
    error = validate_game_title(title)
    if error:
        return False, error

    title = title.strip()
    platform = platform.strip()
    genre_mode = genre_mode.strip()
    notes = notes.strip()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO games (title, platform, genre_mode, notes, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            title,
            platform,
            genre_mode,
            notes,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()
        return True, "Game added successfully."

    except sqlite3.IntegrityError:
        return False, "A game with that title already exists."

    except Exception as e:
        return False, f"Error adding game: {e}"


def get_all_games():
    """
    Returns all games sorted by title.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, platform, genre_mode, notes, created_at
        FROM games
        ORDER BY title COLLATE NOCASE
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows