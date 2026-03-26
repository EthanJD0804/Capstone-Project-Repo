def validate_game_title(title: str) -> str | None:
    """
    Returns an error message if invalid, otherwise None.
    """
    if not title or not title.strip():
        return "Game title is required."

    return None