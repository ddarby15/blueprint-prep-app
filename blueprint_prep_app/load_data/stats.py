import pandas as pd

from load_data.common import load_csv_data # filter_league_data, add_team_names
from utils.get_team_id import get_team_id


# -----------------------------
# Team Level Stats 
# -----------------------------

def filter_team_stats(
    df: pd.DataFrame,
    team_name: str,
    season: int,
    division: str,
    add_names: bool = False,
    teams_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Filter a team-level stats dataframe to one team in one season.

    Parameters
    ----------
    df : pd.DataFrame
        Team-level stats dataframe (basic stats, advanced stats, etc.).

    team_name : str
        Team name to filter to.

    season : int
        Season to filter to.

    division : str
        One of:
        - "Mens"
        - "Womens"

    add_names : bool, default=False
        If True, merge TeamName and TeamName_opp columns.

    teams_df : pd.DataFrame | None, default=None
        Optional teams lookup dataframe. If None, teams.csv will be loaded.

    Returns
    -------
    pd.DataFrame
        Team-level stats dataframe for the selected team and season.
    """
    if teams_df is None:
        teams_df = load_csv_data("teams.csv")
            
    team_id = get_team_id(
        team_name=team_name,
        division=division,
        teams_df=teams_df,
    )

    data = filter_league_data(
        df=df,
        division=division,
        season=season,
    )

    data = data.loc[data["TeamID"] == team_id].copy()

    if add_names:
        data = add_team_names(data, teams_df=teams_df)

    sort_cols = [col for col in ["Season", "TeamID", "DayNum"] if col in data.columns]
    if sort_cols:
        data = data.sort_values(sort_cols).reset_index(drop=True)

    return data


# -----------------------------
# League Level Stats (for league average computations)
# -----------------------------

def filter_league_data(
    df: pd.DataFrame,
    division: str | None = None,
    season: int | None = None,
) -> pd.DataFrame:
    """
    Filter a team-level NCAA dataframe by division and/or season.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing at least Season and TeamID columns.

    division : str | None, default=None
        One of:
        - "Mens"
        - "Womens"
        - None for no division filter

    season : int | None, default=None
        Season to filter to. If None, keep all seasons.

    Returns
    -------
    pd.DataFrame
        Filtered dataframe.
    """
    out = df.copy()

    if season is not None:
        out = out.loc[out["Season"] == season].copy()

    if division is not None:
        if division == "Mens":
            out = out.loc[out["TeamID"] < 3000].copy()
        elif division == "Womens":
            out = out.loc[out["TeamID"] > 3000].copy()
        else:
            raise ValueError("division must be one of: None, 'Mens', 'Womens'")

    return out



# -----------------------------
# Helpers
# -----------------------------
def add_team_names(
    df: pd.DataFrame,
    teams_df: pd.DataFrame,
    team_col: str = "TeamID",
    opp_col: str = "TeamID_opp",
) -> pd.DataFrame:
    """
    Optionally merge team and opponent names into a dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    teams_df : pd.DataFrame
        Teams lookup dataframe with TeamID and TeamName columns.

    team_col : str, default="TeamID"
        Team ID column in df.

    opp_col : str, default="TeamID_opp"
        Opponent team ID column in df.

    Returns
    -------
    pd.DataFrame
        Dataframe with TeamName and optionally TeamName_opp added.
    """
    out = df.copy()

    if team_col in out.columns:
        lookup_team = teams_df[["TeamID", "TeamName"]].rename(
            columns={"TeamID": team_col, "TeamName": "TeamName"}
        )
        out = out.merge(lookup_team, how="left", on=team_col)

    if opp_col in out.columns:
        lookup_opp = teams_df[["TeamID", "TeamName"]].rename(
            columns={"TeamID": opp_col, "TeamName": "TeamName_opp"}
        )
        out = out.merge(lookup_opp, how="left", on=opp_col)

    return out