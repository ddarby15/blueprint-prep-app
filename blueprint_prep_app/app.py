import streamlit as st

from load_data.common import load_csv_data
from load_data.stats import filter_team_stats, filter_league_data
from plotting.plot_team_trends_mpl import plot_team_trends


st.set_page_config(
    page_title="Blueprint Prep",
    page_icon="🏀",
    layout="wide",
)

# Header
st.title("Blueprint Prep 🏀")
st.caption("NCAA Matchup Analytics for Coaches")

# --- Sidebar controls ---
with st.sidebar:
    st.title("Matchup Setup")

    season = st.selectbox(
        "Select Season",
        options=[2026, 2025, 2024]
    )
    
    division = st.selectbox(
        "Select Division",
        options=["Mens", "Womens"]
    )

    team_a = st.selectbox(
        "Select Team A",
        options=["Iowa", "Duke", "Houston", "UConn", "Purdue"]
    )

    team_b = st.selectbox(
        "Select Team B",
        options=["Florida", "Kansas", "Tennessee", "Auburn"]
    )
    
# Prediction placeholder
st.markdown("## Matchup Prediction")
st.info("Model prediction card will go here.")


# Team comparison section
st.markdown("## Team Comparison")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### {team_a}")
    st.write("Wins: --")
    st.write("Losses: --")
    st.write("WinPct: --")
    st.write("AvgMargin: --")
    st.write("SOS: --")
    st.write("SRS: --")
    st.write("Elo: --")

with col2:
    st.markdown(f"### {team_b}")
    st.write("Wins: --")
    st.write("Losses: --")
    st.write("WinPct: --")
    st.write("AvgMargin: --")
    st.write("SOS: --")
    st.write("SRS: --")
    st.write("Elo: --")

# Matchup metrics
st.markdown("## Matchup Edge")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("WinPct Diff", "--")
m2.metric("AvgMargin Diff", "--")
m3.metric("SOS Diff", "--")
m4.metric("SRS Diff", "--")
m5.metric("Elo Diff", "--")


# -----------------------------
# Plotting
# -----------------------------

# load data
teams_df = load_csv_data("teams.csv")
advanced_df = load_csv_data("games_advanced_box_score_stats.csv")
adv_league_data = filter_league_data(df=advanced_df, division=division, season=season)   # filter league level data for league averages

team_a_adv_stats = filter_team_stats(
    df=advanced_df,
    team_name=team_a,
    season=season,
    division=division,
    add_names=True,
    teams_df=teams_df,
)
# st.dataframe(team_a_adv_stats)

team_b_adv_stats = filter_team_stats(
    df=advanced_df,
    team_name=team_b,
    season=season,
    division=division,
    add_names=True,
    teams_df=teams_df,
)
# st.dataframe(team_b_adv_stats)

st.markdown("## Team Trend Analysis")
tab1, tab2 = st.tabs(["Ratings", "Four Factors"])
# Tab 1 - Compare Raw Ratings Trends
with tab1:
    st.markdown("### Ratings Trend Comparison")
    ratings_a_col, ratings_b_col = st.columns(2)


# Tab 2 - Plot Four Factors Trends
with tab2:
    offense_tab, defense_tab = st.tabs(["Offense", "Defense"])

    four_factors = ['eFG_pct', 'ORB_pct', 'TOV_pct', 'FTr']
    four_factors_opp = ['eFG_pct_opp', 'ORB_pct_opp', 'TOV_pct_opp', 'FTr_opp']

    with offense_tab:
        st.markdown(f"### {team_a} Offense Vs {team_b} Defense")
        ff_a_off_col, ff_b_off_col = st.columns(2)
        
        # Team A Metrics (Offense)
        with ff_a_off_col:
            team_a_off_adv_fig, axes = plot_team_trends(
                df=team_a_adv_stats,
                team_name=team_a,
                title="Offense",
                cols=four_factors,
                x_col=None,
                sort_by=None,
                ncols=1,
                rolling_window=5,
                league_df=adv_league_data,
                show_league_avg=True,
            )
            st.pyplot(team_a_off_adv_fig, use_container_width=False)

        # Team B's Opponents Metrics (Defense)
        with ff_b_off_col:
            team_b_def_adv_fig, axes = plot_team_trends(
                df=team_b_adv_stats,
                team_name=team_b,
                title="Defense",
                cols=four_factors_opp,
                x_col=None,
                sort_by=None,
                ncols=1,
                rolling_window=5,
                league_df=adv_league_data,
                show_league_avg=True,
            )
            st.pyplot(team_b_def_adv_fig, use_container_width=False)
            
    with defense_tab:
        st.markdown(f"### {team_a} Defense Vs {team_b} Offense")
        ff_a_def_col, ff_b_def_col = st.columns(2)
        
        # Team A's Opponents Metrics (Defense)
        with ff_a_def_col:
            team_a_def_adv_fig, axes = plot_team_trends(
                df=team_a_adv_stats,
                team_name=team_a,
                title="Defense",
                cols=four_factors_opp,
                x_col=None,
                sort_by=None,
                ncols=1,
                rolling_window=5,
                league_df=adv_league_data,
                show_league_avg=True,
            )
            st.pyplot(team_a_def_adv_fig, use_container_width=False)

        # Team B Metrics (Offense)
        with ff_b_def_col:
            team_b_off_adv_fig, axes = plot_team_trends(
                df=team_b_adv_stats,
                team_name=team_b,
                title="Offense",
                cols=four_factors,
                x_col=None,
                sort_by=None,
                ncols=1,
                rolling_window=5,
                league_df=adv_league_data,
                show_league_avg=True,
            )
            st.pyplot(team_b_off_adv_fig, use_container_width=False)
    