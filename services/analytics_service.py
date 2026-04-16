from data.db import get_connection


def get_overall_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sessions")
    total_sessions = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(duration_minutes), 0) FROM sessions")
    total_minutes = cursor.fetchone()[0]

    avg_session = 0
    if total_sessions > 0:
        avg_session = round(total_minutes / total_sessions, 2)

    conn.close()

    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "average_session": avg_session
    }


def get_stats_for_game(game_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sessions WHERE game_id = ?", (game_id,))
    total_sessions = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COALESCE(SUM(duration_minutes), 0) FROM sessions WHERE game_id = ?",
        (game_id,)
    )
    total_minutes = cursor.fetchone()[0]

    avg_session = 0
    if total_sessions > 0:
        avg_session = round(total_minutes / total_sessions, 2)

    conn.close()

    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "average_session": avg_session
    }

def get_playtime_by_game():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT games.title, COALESCE(SUM(sessions.duration_minutes), 0) as total_minutes
        FROM games
        LEFT JOIN sessions ON games.id = sessions.game_id
        GROUP BY games.id, games.title
        ORDER BY total_minutes DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_goal_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM goals WHERE status = 'Active'")
    active_goals = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM goals WHERE status = 'Completed'")
    completed_goals = cursor.fetchone()[0]

    conn.close()

    return {
        "active_goals": active_goals,
        "completed_goals": completed_goals
    }


def get_goal_stats_for_game(game_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM goals WHERE game_id = ? AND status = 'Active'",
        (game_id,)
    )
    active_goals = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM goals WHERE game_id = ? AND status = 'Completed'",
        (game_id,)
    )
    completed_goals = cursor.fetchone()[0]

    conn.close()

    return {
        "active_goals": active_goals,
        "completed_goals": completed_goals
    }


def get_active_goals_list(game_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if game_id is None:
        cursor.execute("""
            SELECT games.title, goals.goal_name, goals.target
            FROM goals
            JOIN games ON goals.game_id = games.id
            WHERE goals.status = 'Active'
            ORDER BY games.title, goals.goal_name
        """)
    else:
        cursor.execute("""
            SELECT games.title, goals.goal_name, goals.target
            FROM goals
            JOIN games ON goals.game_id = games.id
            WHERE goals.status = 'Active' AND goals.game_id = ?
            ORDER BY games.title, goals.goal_name
        """, (game_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows