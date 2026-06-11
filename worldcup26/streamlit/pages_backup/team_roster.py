from functions.team_roster import *


def render_team_roster( df: pd.DataFrame) -> None:
    """
    Render a complete team roster view.

    This function orchestrates the rendering of all squad-related
    sections, including the team header, squad summary, top market
    value players, and the full roster grouped by position.

    Args:
        df (pd.DataFrame): Team squad dataset.

    Returns:
        None

    Raises:
        TypeError: If df is not a pandas DataFrame.
        RuntimeError: If any roster component fails to render.
    """

    # 🔹 Validate input type
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    try:
        # 🔹 Render team header section
        team_header(df)

        # 🔹 Render squad summary and retrieve players-only dataset
        players_only = team_summary(df)

        # 🔹 Render top market value players section
        star_players_market_value(players_only)

        # 🔹 Render complete squad grouped by position
        squad_by_position(players_only)

    except Exception as e:
        raise RuntimeError(
            f"Failed to render team roster: {e}"
        )