from math import ceil
from typing import Sequence

import pandas as pd
import matplotlib.pyplot as plt

from utils.get_team_id import get_team_id


def plot_team_trends(
    df: pd.DataFrame,
    team_name: str,
    title: str = "Team Trends",
    cols: Sequence[str] | None = None,
    team_col: str = "TeamName",
    x_col: str | None = "DayNum",
    sort_by: str | None = "DayNum",
    ncols: int = 2,
    figsize_per_subplot: tuple[int, int] = (7, 4),
    rolling_window: int | None = None,
    show_raw: bool = True,
    show_trend: bool = True,
    show_league_avg: bool = True,
    league_df: pd.DataFrame | None = None,
    league_avg_label: str = "League avg",
    marker: str = "o",
    show: bool = True,
):
    """
    Plot team-level stat trends across games using line charts.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe at the team-game grain
        (typically one row per team per game).

    team_name : str
        Team name to filter the dataframe to a single team.

    cols : Sequence[str] | None, default=None
        Numeric stat columns to plot. If None, numeric columns are inferred.

    team_col : str, default="TeamName"
        Column containing the team name.

    x_col : str | None, default="DayNum"
        Column to use on the x-axis. Common examples:
        "DayNum", "GameDate", or "GameNumber".
        If None, game order (0..n-1) is used.

    sort_by : str | None, default="DayNum"
        Column used to sort the team data before plotting.
        If None, preserves the current dataframe order.

    ncols : int, default=2
        Number of subplot columns.

    figsize_per_subplot : tuple[int, int], default=(7, 4)
        Width and height per subplot.

    rolling_window : int | None, default=None
        Optional rolling mean window size to overlay a smoothed trend line.
        Example: 3 plots a 3-game rolling average.

    show_raw : bool, default=True
        Whether to plot the raw game-by-game values.

    show_trend : bool, default=True
        Whether to plot the rolling trend line when `rolling_window` is provided.
        If `rolling_window` is None, only the raw line is shown.

    show_league_avg : bool, default=True
        Whether to draw a horizontal line for the league-wide average of each metric.

    league_df : pd.DataFrame | None, default=None
        Dataframe used to compute league averages. If None, uses `df`.
        This is useful if you want to plot one subset but compare against a broader
        or different reference population.

    league_avg_label : str, default="League avg"
        Legend label for the league-average line.

    marker : str, default="o"
        Marker style for the raw line.

    show : bool, default=True
        Whether to display the figure immediately.

    Returns
    -------
    tuple[matplotlib.figure.Figure, np.ndarray]
        Figure and axes array.

    Raises
    ------
    ValueError
        If the team column is missing, the team is not found, or no valid
        numeric columns are available to plot.
    """
    league_df = df if league_df is None else league_df

    team_df = _get_team_frame(
        df=df,
        team_name=team_name,
        team_col=team_col,
        sort_by=sort_by,
    )

    columns = _resolve_plot_columns(
        team_df=team_df,
        cols=cols,
        x_col=x_col,
        sort_by=sort_by,
    )

    x, x_label = _resolve_x_values(
        team_df=team_df,
        x_col=x_col,
    )

    league_averages = _compute_league_averages(
        league_df=league_df,
        columns=columns,
    )

    nrows = ceil(len(columns) / ncols)
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(figsize_per_subplot[0] * ncols, figsize_per_subplot[1] * nrows),
        squeeze=False,
    )
    flat_axes = axes.flatten()

    for ax, col in zip(flat_axes, columns):
        y = team_df[col]

        if show_raw:
            ax.plot(
                x,
                y,
                marker=marker,
                linewidth=1.8,
                label="Game-by-game",
            )

        if show_trend and rolling_window is not None and rolling_window > 1:
            trend = y.rolling(window=rolling_window, min_periods=1).mean()
            ax.plot(
                x,
                trend,
                linewidth=2.5,
                linestyle="--",
                label=f"{rolling_window}-game rolling avg",
            )

        if show_league_avg and col in league_averages and pd.notna(league_averages[col]):
            ax.axhline(
                y=league_averages[col],
                color='red',
                linewidth=2,
                linestyle=":",
                alpha=0.9,
                label=f"{league_avg_label}: {league_averages[col]:.2f}",
            )

        ax.set_title(col)
        ax.set_xlabel(x_label)
        ax.set_ylabel(col)
        ax.grid(True, alpha=0.3)

        if ax.get_legend_handles_labels()[0]:
            ax.legend()

    for ax in flat_axes[len(columns):]:
        ax.remove()

    fig.suptitle(f"{team_name} {title}", fontsize=14, y=1.02)
    fig.tight_layout()

    if show:
        plt.show()

    # display(team_df.reset_index(drop=True))

    return fig, axes


def _get_team_frame(
    df: pd.DataFrame,
    team_name: str,
    team_col: str,
    sort_by: str | None,
) -> pd.DataFrame:
    """
    Validate team column, filter to a single team, and optionally sort rows.
    """
    if team_col not in df.columns:
        raise ValueError(f"{team_col!r} was not found in dataframe columns.")

    team_df = df.loc[df[team_col] == team_name].copy()

    if team_df.empty:
        available_teams = sorted(df[team_col].dropna().astype(str).unique())
        raise ValueError(
            f"team_name={team_name!r} was not found in column {team_col!r}. "
            f"Example teams: {available_teams[:10]}"
        )

    if sort_by is not None:
        if sort_by not in team_df.columns:
            raise ValueError(f"sort_by={sort_by!r} was not found in dataframe columns.")
        team_df = team_df.sort_values(sort_by).reset_index(drop=True)

    return team_df


def _resolve_plot_columns(
    team_df: pd.DataFrame,
    cols: Sequence[str] | None,
    x_col: str | None,
    sort_by: str | None,
) -> list[str]:
    """
    Resolve which numeric columns should be plotted.
    """
    if cols is None:
        numeric_cols = team_df.select_dtypes(include="number").columns.tolist()

        exclude_default = {
            "Season",
            "DayNum",
            "NumOT",
            "TeamID",
            "TeamID_opp",
        }

        if x_col is not None:
            exclude_default.add(x_col)
        if sort_by is not None:
            exclude_default.add(sort_by)

        columns = [c for c in numeric_cols if c not in exclude_default]
    else:
        columns = [c for c in cols if c in team_df.columns]

    columns = [c for c in columns if pd.api.types.is_numeric_dtype(team_df[c])]

    if not columns:
        raise ValueError("No numeric columns available to plot for this team.")

    return columns


def _resolve_x_values(
    team_df: pd.DataFrame,
    x_col: str | None,
) -> tuple[pd.Series | range, str]:
    """
    Resolve x-axis values and label.
    """
    if x_col is not None:
        if x_col not in team_df.columns:
            raise ValueError(f"x_col={x_col!r} was not found in dataframe columns.")
        return team_df[x_col], x_col

    return range(len(team_df)), "Game Order"


def _compute_league_averages(
    league_df: pd.DataFrame,
    columns: Sequence[str],
) -> dict[str, float]:
    """
    Compute league-wide averages for the plotted columns.
    """
    averages = {}
    for col in columns:
        if col in league_df.columns and pd.api.types.is_numeric_dtype(league_df[col]):
            averages[col] = league_df[col].mean(skipna=True)
    return averages