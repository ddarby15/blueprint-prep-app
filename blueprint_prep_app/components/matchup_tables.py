from __future__ import annotations

import pandas as pd
import streamlit as st


def build_tale_of_the_tape_df(
    team_a: str,
    team_b: str,
    team_a_ratings: dict,
    team_b_ratings: dict,
) -> pd.DataFrame:
    """
    Build a tale-of-the-tape style matchup table.

    Parameters
    ----------
    team_a : str
        Display name for Team A.

    team_b : str
        Display name for Team B.

    team_a_ratings : dict
        Dictionary of Team A ratings/summary values.
        Expected keys:
        - "Wins"
        - "Losses"
        - "WinPct"
        - "Adj_Rating"
        - "AvgMargin"
        - "SOS"

    team_b_ratings : dict
        Dictionary of Team B ratings/summary values.
        Expected keys:
        - "Wins"
        - "Losses"
        - "WinPct"
        - "Adj_Rating"
        - "AvgMargin"
        - "SOS"

    Returns
    -------
    pd.DataFrame
        Tale-of-the-tape DataFrame with metric names as the index and
        [team_a, team_b, "Matchup Edge"] as columns.

    Notes
    -----
    Matchup Edge is currently defined as:

        Team A metric - Team B metric

    So:
    - positive edge means Team A is numerically higher
    - negative edge means Team B is numerically higher

    Interpretation of whether that is "good" or "bad" depends on the metric.
    """
    required_keys = ["Wins", "Losses", "WinPct", "Adj_Rating", "AvgMargin", "SOS"]

    missing_a = [key for key in required_keys if key not in team_a_ratings]
    missing_b = [key for key in required_keys if key not in team_b_ratings]

    if missing_a:
        raise ValueError(f"team_a_ratings is missing required keys: {missing_a}")
    if missing_b:
        raise ValueError(f"team_b_ratings is missing required keys: {missing_b}")

    team_a_wins = int(team_a_ratings["Wins"])
    team_a_losses = int(team_a_ratings["Losses"])
    team_b_wins = int(team_b_ratings["Wins"])
    team_b_losses = int(team_b_ratings["Losses"])

    df = pd.DataFrame(
        {
            team_a: [
                f"{team_a_wins} - {team_a_losses}",
                float(team_a_ratings["WinPct"]),
                float(team_a_ratings["Adj_Rating"]),
                float(team_a_ratings["AvgMargin"]),
                float(team_a_ratings["SOS"]),
            ],
            team_b: [
                f"{team_b_wins} - {team_b_losses}",
                float(team_b_ratings["WinPct"]),
                float(team_b_ratings["Adj_Rating"]),
                float(team_b_ratings["AvgMargin"]),
                float(team_b_ratings["SOS"]),
            ],
            "Matchup Edge": [
                "-",
                float(team_a_ratings["WinPct"]) - float(team_b_ratings["WinPct"]),
                float(team_a_ratings["Adj_Rating"]) - float(team_b_ratings["Adj_Rating"]),
                float(team_a_ratings["AvgMargin"]) - float(team_b_ratings["AvgMargin"]),
                float(team_a_ratings["SOS"]) - float(team_b_ratings["SOS"]),
            ],
        },
        index=[
            "Record",
            "Win %",
            "Adjusted Rating",
            "Average MoV",
            "Strength of Schedule",
        ],
    )

    return df


def style_tale_of_the_tape(
    df: pd.DataFrame,
    metric_directions: dict[str, str] | None = None,
    decimals: int = 2,
) -> pd.io.formats.style.Styler:
    """
    Style a tale-of-the-tape DataFrame using pandas Styler.

    Parameters
    ----------
    df : pd.DataFrame
        Tale-of-the-tape DataFrame from build_tale_of_the_tape_df().

    metric_directions : dict[str, str] | None, default=None
        Mapping of metric name -> direction rule.

        Allowed values:
        - "higher" : higher is better
        - "lower"  : lower is better

        Example:
        {
            "Win %": "higher",
            "Adjusted Rating": "higher",
            "Average MoV": "higher",
            "Strength of Schedule": "higher",
        }

        If None, all supported metrics default to "higher".

    decimals : int, default=2
        Number of decimal places used for numeric formatting.

    Returns
    -------
    pd.io.formats.style.Styler
        Styled table ready for HTML rendering in Streamlit.

    Notes
    -----
    Coloring is only applied to the "Matchup Edge" column.
    """
    if metric_directions is None:
        metric_directions = {
            "Win %": "higher",
            "Adjusted Rating": "higher",
            "Average MoV": "higher",
            "Strength of Schedule": "higher",
        }

    edge_col = "Matchup Edge"

    def format_value(x):
        if isinstance(x, (int, float)):
            return f"{x:.{decimals}f}"
        return x

    def edge_cell_style(val, metric_name: str) -> str:
        if metric_name == "Record":
            return "text-align: center;"

        if val == "-" or pd.isna(val):
            return "text-align: center;"

        diff = float(val)
        direction = metric_directions.get(metric_name, "higher")

        if diff == 0:
            return (
                "background-color: #f2f2f2; "
                "color: black; "
                "font-weight: bold; "
                "text-align: center;"
            )

        if direction == "higher":
            team_a_advantage = diff > 0
        elif direction == "lower":
            team_a_advantage = diff < 0
        else:
            raise ValueError(
                f"Invalid metric direction '{direction}' for metric '{metric_name}'. "
                "Use 'higher' or 'lower'."
            )

        bg = "#c6efce" if team_a_advantage else "#ffc7ce"

        return (
            f"background-color: {bg}; "
            "color: black; "
            "font-weight: bold; "
            "text-align: center;"
        )

    styler = df.style.format(format_value)

    styler = styler.set_properties(
        **{
            "text-align": "center",
            "border": "1px solid #d0d0d0",
            "padding": "6px 10px",
        }
    )

    styler = styler.set_table_styles(
        [
            {"selector": "table", "props": [("border-collapse", "collapse"), ("width", "100%")]},
            {"selector": "th", "props": [("text-align", "center")]},
            {"selector": "th.row_heading", "props": [("text-align", "left")]},
        ]
    )

    for metric in df.index:
        styler = styler.map(
            lambda v, m=metric: edge_cell_style(v, m),
            subset=pd.IndexSlice[[metric], [edge_col]],
        )

    return styler


def render_tale_of_the_tape(
    team_a: str,
    team_b: str,
    team_a_ratings: dict,
    team_b_ratings: dict,
    metric_directions: dict[str, str] | None = None,
    decimals: int = 2,
    title: str | None = "Tale of the Tape",
) -> pd.DataFrame:
    """
    Build, style, and render a tale-of-the-tape table in Streamlit.

    Parameters
    ----------
    team_a : str
        Display name for Team A.

    team_b : str
        Display name for Team B.

    team_a_ratings : dict
        Team A ratings dictionary.

    team_b_ratings : dict
        Team B ratings dictionary.

    metric_directions : dict[str, str] | None, default=None
        Metric direction mapping passed to style_tale_of_the_tape().

    decimals : int, default=2
        Decimal formatting passed to style_tale_of_the_tape().

    title : str | None, default="Tale of the Tape"
        Optional section title shown above the table.
        Set to None to suppress the title.

    Returns
    -------
    pd.DataFrame
        The underlying tale-of-the-tape DataFrame.

    Notes
    -----
    The styled table is rendered via HTML because Streamlit's default dataframe
    display is less flexible for this presentation style.
    """
    df = build_tale_of_the_tape_df(
        team_a=team_a,
        team_b=team_b,
        team_a_ratings=team_a_ratings,
        team_b_ratings=team_b_ratings,
    )

    styler = style_tale_of_the_tape(
        df=df,
        metric_directions=metric_directions,
        decimals=decimals,
    )

    if title:
        st.subheader(title)

    st.markdown(styler.to_html(), unsafe_allow_html=True)

    return df