import pandas as pd
from load_data.common import load_csv_data


def get_team_id(
    team_name: str,
    division: str,
    teams_df: pd.DataFrame | None = None,
) -> int:
    """
    Get the TeamID for a given team name within a division.

    Parameters
    ----------
    team_name : str
        Team name to look up.

    division : str
        One of:
        - "Mens"
        - "Womens"

    teams_df : pd.DataFrame | None, default=None
        Optional teams lookup dataframe. If None, teams.csv will be loaded.

    Returns
    -------
    int
        TeamID for the matched team.
    """
    if teams_df is None:
        teams_df = load_csv_data("teams.csv")

    if division == "Mens":
        df = teams_df.loc[teams_df["TeamID"] < 3000].copy()
    elif division == "Womens":
        df = teams_df.loc[teams_df["TeamID"] > 3000].copy()
    else:
        raise ValueError("division must be either 'Mens' or 'Womens'")

    matches = df.loc[df["TeamName"] == team_name, "TeamID"]

    if matches.empty:
        raise ValueError(f"Team '{team_name}' not found in division '{division}'.")

    return int(matches.iloc[0])