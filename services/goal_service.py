from datetime import datetime
from data.db import get_connection


def create_goal(game_id, goal_name, goal_type, target, start_date, end_date=None):
    goal_name = (goal_name or "").strip()
    goal_type = (goal_type or "").strip()
    target = (target or "").strip()
    start_date = (start_date or "").strip()
    end_date = (end_date or "").strip()

    if not goal_name:
        return False, "Goal name is required."

    if not goal_type:
        return False, "Goal type is required."

    if not target:
        return False, "Target is required."

    if not start_date:
        return False, "Start date is required."

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO goals (
                game_id, goal_name, goal_type, target,
                start_date, end_date, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            game_id,
            goal_name,
            goal_type,
            target,
            start_date,
            end_date if end_date else None,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        return True, "Goal created successfully."

    except Exception as e:
        return False, f"Error creating goal: {e}"


def get_goals_for_game(game_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, goal_name, goal_type, target, status
        FROM goals
        WHERE game_id = ?
    """, (game_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def complete_goal(goal_id, note=""):
    note = (note or "").strip()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE goals
            SET status = 'Completed', completion_note = ?
            WHERE id = ?
        """, (note, goal_id))

        conn.commit()
        conn.close()

        return True, "Goal completed."

    except Exception as e:
        return False, f"Error completing goal: {e}"