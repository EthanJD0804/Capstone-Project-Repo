import json
from data.db import get_connection


def export_backup(filepath):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM games")
        games = cursor.fetchall()

        cursor.execute("SELECT * FROM goals")
        goals = cursor.fetchall()

        cursor.execute("SELECT * FROM sessions")
        sessions = cursor.fetchall()

        backup_data = {
            "games": games,
            "goals": goals,
            "sessions": sessions
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=4)

        conn.close()
        return True, "Backup exported successfully."

    except Exception as e:
        return False, f"Error exporting backup: {e}"


def import_backup(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sessions")
        cursor.execute("DELETE FROM goals")
        cursor.execute("DELETE FROM games")

        for game in backup_data.get("games", []):
            cursor.execute("""
                INSERT INTO games (id, title, platform, genre_mode, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, tuple(game))

        for goal in backup_data.get("goals", []):
            cursor.execute("""
                INSERT INTO goals (
                    id, game_id, goal_name, goal_type, target,
                    start_date, end_date, status, completion_note, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(goal))

        for session in backup_data.get("sessions", []):
            cursor.execute("""
                INSERT INTO sessions (
                    id, game_id, session_datetime, duration_minutes,
                    session_type, outcome, notes, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(session))

        conn.commit()
        conn.close()

        return True, "Backup imported successfully."

    except Exception as e:
        return False, f"Error importing backup: {e}"