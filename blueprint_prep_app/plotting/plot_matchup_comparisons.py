import pandas as pd
import plotly.graph_objects as go


# -----------------------------
# Ratings Comparison
# -----------------------------

def plot_matchup_ratings(
    team_a: str,
    team_b: str,
    team_a_ratings: dict,
    team_b_ratings: dict,
    league_ratings_df: pd.DataFrame | None = None,
    team_a_color: str = "lightskyblue",
    team_b_color: str = "royalblue",
    title: str | None = None,
    width: int | None = None,
    height: int | None = None,
    decimals: int = 2,
) -> go.Figure:
    """
    Create a mirrored horizontal bar chart for raw matchup ratings.

    Parameters
    ----------
    team_a : str
        Team A display name.

    team_b : str
        Team B display name.

    team_a_ratings : dict
        Ratings dictionary for Team A.

    team_b_ratings : dict
        Ratings dictionary for Team B.

    league_ratings_df : pd.DataFrame | None, default=None
        League-wide ratings dataframe already filtered to the selected season
        and division. Used to compute per-metric normalization factors.

    team_a_color : str, default="#2ca25f"
        Bar color for Team A.

    team_b_color : str, default="#4c78a8"
        Bar color for Team B.

    title : str | None, default=None
        Optional chart title.

    width : int | None, default=None
        Optional figure width in pixels.

    height : int | None, default=None
        Optional Figure height in pixels.

    decimals : int, default=2
        Number of decimals shown in value labels.

    Returns
    -------
    go.Figure
        Plotly mirrored bar chart.

    Notes
    -----
    This chart normalizes each metric using the maximum absolute league value
    for that metric:

        league_abs_max = max(abs(league_min), abs(league_max))

    That means:
    - bar lengths reflect where each team's raw value sits relative to the
      full league range for that metric
    - text labels carry the actual raw values
    """
    df = build_matchup_ratings_df(
        team_a=team_a,
        team_b=team_b,
        team_a_ratings=team_a_ratings,
        team_b_ratings=team_b_ratings,
    ).copy()
    # display(df)

    if title is None:
        title = "Team Ratings"

    if league_ratings_df is None:
        raise ValueError("league_ratings_df must be provided for league-based normalization.")

    # Compute league normalization factors for each metric    
    metric_cols = df["SourceMetric"].tolist()

    missing_cols = [col for col in metric_cols if col not in league_ratings_df.columns]
    if missing_cols:
        raise ValueError(
            f"These metric columns are missing from league_ratings_df: {missing_cols}"
        )

    league_min = league_ratings_df[metric_cols].min()
    league_max = league_ratings_df[metric_cols].max()
    league_abs_max = pd.concat(
        [league_min.abs(), league_max.abs()],
        axis=1
    ).max(axis=1).replace(0, 1.0)

    norm_df = (
        league_abs_max
        .rename("league_abs_max")
        .reset_index()
        .rename(columns={"index": "SourceMetric"})
    )

    df = df.merge(norm_df, on="SourceMetric", how="left")

    # Team A goes left, Team B goes right
    df["team_a_plot"] = -(df[team_a] / df["league_abs_max"])
    df["team_b_plot"] = df[team_b] / df["league_abs_max"]

    # Raw value labels
    df["team_a_label"] = df[team_a].map(lambda x: f"{x:.{decimals}f}")
    df["team_b_label"] = df[team_b].map(lambda x: f"{x:.{decimals}f}")

    # compute figure height dynamically (for consistent bar thickness)
    n_metrics = len(df)
    if height is None:
        height = 110 + n_metrics * 90

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df["Metric"],
            x=df["team_a_plot"],
            orientation="h",
            name=team_a,
            marker=dict(color=team_a_color),
            text=df["team_a_label"],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"{team_a}: "
                + "%{customdata:.2f}<extra></extra>"
            ),
            customdata=df[team_a],
        )
    )

    fig.add_trace(
        go.Bar(
            y=df["Metric"],
            x=df["team_b_plot"],
            orientation="h",
            name=team_b,
            marker=dict(color=team_b_color),
            text=df["team_b_label"],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"{team_b}: "
                + "%{customdata:.2f}<extra></extra>"
            ),
            customdata=df[team_b],
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=20), x=0.46),
        template="plotly_white",
        barmode="overlay",
        height=height,
        margin=dict(l=40, r=40, t=100, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
        xaxis=dict(
            title="",
            range=[-1.25, 1.25],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black",
            showgrid=False,
            tickmode="array",
            tickvals=[-1, 0, 1],
            ticktext=["", "", ""],
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
            showticklabels=False,
        ),
        bargap=0.65,
    )

    if width is not None:
        fig.update_layout(width=width)

    # add metric labels
    for metric in df["Metric"]:
        fig.add_annotation(
            x=0,
            y=metric,
            text=f"<b>{metric}</b>",
            showarrow=False,
            xanchor="center",
            yanchor="bottom",
            yshift=15,
            font=dict(size=14),
        )

    return fig


def build_matchup_ratings_df(
    team_a: str,
    team_b: str,
    team_a_ratings: dict,
    team_b_ratings: dict,
) -> pd.DataFrame:
    """
    Build a dataframe of raw team values for high-level matchup metrics.

    Parameters
    ----------
    team_a : str
        Team A display name.

    team_b : str
        Team B display name.

    team_a_ratings : dict
        Ratings dictionary for Team A.

    team_b_ratings : dict
        Ratings dictionary for Team B.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - SourceMetric
        - Metric
        - team_a
        - team_b
    """
    required_keys = ["Adj_Rating", "AvgMargin", "SOS"]

    missing_a = [k for k in required_keys if k not in team_a_ratings]
    missing_b = [k for k in required_keys if k not in team_b_ratings]

    if missing_a:
        raise ValueError(f"team_a_ratings is missing required keys: {missing_a}")
    if missing_b:
        raise ValueError(f"team_b_ratings is missing required keys: {missing_b}")

    return pd.DataFrame(
        {
            "SourceMetric": ["Adj_Rating", "AvgMargin", "SOS"],
            "Metric": ["Adjusted Rating", "Average MoV", "Strength of Schedule"],
            team_a: [
                float(team_a_ratings["Adj_Rating"]),
                float(team_a_ratings["AvgMargin"]),
                float(team_a_ratings["SOS"]),
            ],
            team_b: [
                float(team_b_ratings["Adj_Rating"]),
                float(team_b_ratings["AvgMargin"]),
                float(team_b_ratings["SOS"]),
            ],
        }
    )


# -----------------------------
# Matchup Edge
# -----------------------------

def plot_matchup_edge_overview(
    team_a: str,
    team_b: str,
    team_a_ratings: dict,
    team_b_ratings: dict,
    team_a_color: str = "lightskyblue",
    team_b_color: str = "royalblue",
    title: str | None = None,
    height: int | None = None,
) -> go.Figure:
    """
    Create a Plotly diverging horizontal bar chart for matchup edges.

    Parameters
    ----------
    team_a : str
        Team A display name.

    team_b : str
        Team B display name.

    team_a_ratings : dict
        Ratings dictionary for Team A.

    team_b_ratings : dict
        Ratings dictionary for Team B.

    team_a_color : str, default="#2ca25f"
        Color used when Team A has the advantage.

    team_b_color : str, default="#4c78a8"
        Color used when Team B has the advantage.

    title : str | None, default=None
        Optional chart title.

    height : int, default=360
        Figure height in pixels.

    Returns
    -------
    go.Figure
        Plotly figure.
    """
    df = build_matchup_edge_df(
        team_a=team_a,
        team_b=team_b,
        team_a_ratings=team_a_ratings,
        team_b_ratings=team_b_ratings,
    )
    # display(df)
    plot_df = df.copy()

    plot_df["TeamAPlot"] = plot_df["PlotValue"].where(plot_df["AdvantageTeam"] == team_a, 0.0)
    plot_df["TeamBPlot"] = plot_df["PlotValue"].where(plot_df["AdvantageTeam"] == team_b, 0.0)
    # display(plot_df)

    max_abs = max(abs(plot_df["PlotValue"]).max(), 1.0)
    axis_limit = max_abs * 1.25

    if title is None:
        title = f"Matchup Edge"
        
    # compute figure height dynamically (for consistent bar thickness)
    n_metrics = len(df)
    if height is None:
        height = 110 + n_metrics * 90

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=plot_df["Metric"],
            x=plot_df["TeamAPlot"],
            orientation="h",
            name=f"{team_a}",
            marker=dict(color=team_a_color),
            text=[
                label if adv == team_a else ""
                for label, adv in zip(plot_df["Label"], plot_df["AdvantageTeam"])
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"Advantage: {team_a}<br>"
                "Edge: %{text}<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Bar(
            y=plot_df["Metric"],
            x=plot_df["TeamBPlot"],
            orientation="h",
            name=f"{team_b}",
            marker=dict(color=team_b_color),
            text=[
                label if adv == team_b else ""
                for label, adv in zip(plot_df["Label"], plot_df["AdvantageTeam"])
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"Advantage: {team_b}<br>"
                "Edge: %{text}<extra></extra>"
            ),
        )
    )

    for _, row in plot_df.iterrows():
        if row["AdvantageTeam"] == "Even":
            fig.add_annotation(
                x=0,
                y=row["Metric"],
                text="0.00",
                showarrow=False,
                xanchor="center",
                yanchor="middle",
                font=dict(size=12),
            )

    fig.update_layout(
        title=dict(text=title, font=dict(size=20), x=0.46),   # centers the title horizontally
        template="plotly_white",
        barmode="overlay",
        height=height,
        margin=dict(l=40, r=40, t=100, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
        xaxis=dict(
            title="",
            range=[-axis_limit, axis_limit],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            tickmode="array",
            tickvals=[-axis_limit, 0, axis_limit],
            ticktext=[f"", "", f""],
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
            showticklabels=False,
        ),
        bargap=0.65,
    )

    # add metric labels
    for metric in df["Metric"]:
        fig.add_annotation(
            x=0,
            y=metric,
            text=f"<b>{metric}</b>",
            showarrow=False,
            xanchor="center",
            yanchor="bottom",
            yshift=15,   # moves label slightly above the bars
            font=dict(size=14),
        )

    return fig


def build_matchup_edge_df(
    team_a: str,
    team_b: str,
    team_a_ratings: dict,
    team_b_ratings: dict,
) -> pd.DataFrame:
    """
    Build a dataframe of matchup edges for the high-level overview metrics.

    Parameters
    ----------
    team_a : str
        Team A display name.

    team_b : str
        Team B display name.

    team_a_ratings : dict
        Ratings dictionary for Team A.
        Expected keys:
        - "Adj_Rating"
        - "AvgMargin"
        - "SOS"

    team_b_ratings : dict
        Ratings dictionary for Team B.
        Expected keys:
        - "Adj_Rating"
        - "AvgMargin"
        - "SOS"

    Returns
    -------
    pd.DataFrame
        DataFrame with:
        - Metric
        - Edge
        - PlotValue
        - AdvantageTeam
        - Label

    Notes
    -----
    Edge is defined as:

        team_a_metric - team_b_metric

    PlotValue is transformed so that:
    - Team A advantage plots to the LEFT
    - Team B advantage plots to the RIGHT
    """
    required_keys = ["Adj_Rating", "AvgMargin", "SOS"]

    missing_a = [k for k in required_keys if k not in team_a_ratings]
    missing_b = [k for k in required_keys if k not in team_b_ratings]

    if missing_a:
        raise ValueError(f"team_a_ratings is missing required keys: {missing_a}")
    if missing_b:
        raise ValueError(f"team_b_ratings is missing required keys: {missing_b}")

    metrics = [
        ("Adjusted Rating", float(team_a_ratings["Adj_Rating"]), float(team_b_ratings["Adj_Rating"])),
        ("Average MoV", float(team_a_ratings["AvgMargin"]), float(team_b_ratings["AvgMargin"])),
        ("Strength of Schedule", float(team_a_ratings["SOS"]), float(team_b_ratings["SOS"])),
    ]

    rows = []
    for metric_name, a_val, b_val in metrics:
        edge = a_val - b_val

        if edge > 0:
            plot_value = -edge
            advantage_team = team_a
        elif edge < 0:
            plot_value = abs(edge)
            advantage_team = team_b
        else:
            plot_value = 0.0
            advantage_team = "Even"

        rows.append(
            {
                "Metric": metric_name,
                "Edge": edge,
                "PlotValue": plot_value,
                "AdvantageTeam": advantage_team,
                "Label": f"{edge:+.2f}",
            }
        )

    return pd.DataFrame(rows)