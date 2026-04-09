from datetime import datetime
from data.db import get_connection


def create_session(game_id, duration, session_type, outcome, notes):
    duration = str(duration).strip()

    if not duration:
        return False, "Duration is required."

    try:
        duration = int(duration)
        if duration <= 0:
            return False, "Duration must be greater than 0."
    except:
        return False, "Duration must be a number."

    if not session_type:
        return False, "Session type is required."

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions (
                game_id,
                session_datetime,
                duration_minutes,
                session_type,
                outcome,
                notes,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            game_id,
            datetime.now().isoformat(),
            duration,
            session_type,
            outcome,
            notes,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        return True, "Session logged successfully."

    except Exception as e:
        return False, f"Error logging session: {e}"


def get_all_sessions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sessions.id,
            sessions.game_id,
            games.title,
            sessions.session_datetime,
            sessions.duration_minutes,
            sessions.session_type,
            sessions.outcome,
            sessions.notes
        FROM sessions
        JOIN games ON sessions.game_id = games.id
        ORDER BY sessions.session_datetime DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_sessions_by_game(game_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sessions.id,
            sessions.game_id,
            games.title,
            sessions.session_datetime,
            sessions.duration_minutes,
            sessions.session_type,
            sessions.outcome,
            sessions.notes
        FROM sessions
        JOIN games ON sessions.game_id = games.id
        WHERE sessions.game_id = ?
        ORDER BY sessions.session_datetime DESC
    """, (game_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def update_session(session_id, duration, session_type, outcome, notes):
    duration = str(duration).strip()

    if not duration:
        return False, "Duration is required."

    try:
        duration = int(duration)
        if duration <= 0:
            return False, "Duration must be greater than 0."
    except:
        return False, "Duration must be a number."

    if not session_type:
        return False, "Session type is required."

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE sessions
            SET duration_minutes = ?, session_type = ?, outcome = ?, notes = ?
            WHERE id = ?
        """, (
            duration,
            session_type,
            outcome,
            notes,
            session_id
        ))

        conn.commit()
        conn.close()

        return True, "Session updated successfully."

    except Exception as e:
        return False, f"Error updating session: {e}"


def delete_session(session_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()

        return True, "Session deleted successfully."

    except Exception as e:
        return False, f"Error deleting session: {e}"