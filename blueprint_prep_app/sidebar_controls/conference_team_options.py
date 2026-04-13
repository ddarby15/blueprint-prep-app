import pandas as pd


def get_conference_options(
    conf_hist_enriched: pd.DataFrame,
    season: int | None = None,
    division: str | None = None,
    include_all: bool = True,
) -> list[str]:
    """
    Get conference dropdown options for a given season and division.
    """
    out = _filter_conf_history(
        conf_hist_enriched=conf_hist_enriched,
        season=season,
        division=division,
    )

    conferences = sorted(out["Description"].dropna().unique().tolist())

    if include_all:
        return ["All"] + conferences

    return conferences


def get_conference_teams(
    conf_hist_enriched: pd.DataFrame,
    conference: str | None = None,
    season: int | None = None,
    division: str | None = None,
) -> list[str]:
    """
    Get team dropdown options for a given season, division, and conference.

    Parameters
    ----------
    conf_hist_enriched : pd.DataFrame
        Enriched conference history dataframe with columns:
        Season, TeamID, ConfAbbrev, Description, TeamName

    conference : str | None, default=None
        Conference description to filter on. If None or "All",
        returns all teams for the season/division.

    season : int | None, default=None
        Season to filter on.

    division : str | None, default=None
        One of: None, "Mens", "Womens"

    Returns
    -------
    list[str]
        Sorted team names.
    """
    out = _filter_conf_history(
        conf_hist_enriched=conf_hist_enriched,
        season=season,
        division=division,
    )

    if conference not in [None, "All"]:
        out = out.loc[out["Description"] == conference].copy()

    teams = sorted(out["TeamName"].dropna().unique().tolist())
    return teams


def _filter_conf_history(
    conf_hist_enriched: pd.DataFrame,
    season: int | None = None,
    division: str | None = None,
) -> pd.DataFrame:
    """
    Filter conference history data by season and division.

    Parameters
    ----------
    conf_hist_enriched : pd.DataFrame
        DataFrame with columns:
        Season, TeamID, ConfAbbrev, Description, TeamName

    season : int | None, default=None
        Season to filter on.

    division : str | None, default=None
        One of: None, "Mens", "Womens"

    Returns
    -------
    pd.DataFrame
        Filtered dataframe.
    """
    out = conf_hist_enriched.copy()

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