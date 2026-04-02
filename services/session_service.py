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