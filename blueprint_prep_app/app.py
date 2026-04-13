import streamlit as st

from sidebar_controls.conference_team_options import get_conference_options, get_conference_teams
from load_data.common import load_csv_data
from load_data.stats import filter_team_stats, filter_league_data, filter_team_ratings
from plotting.plot_matchup_comparisons import plot_matchup_ratings, plot_matchup_edge_overview
from plotting.plot_team_trends_mpl import plot_team_trends


st.set_page_config(
    page_title="Blueprint Prep",
    page_icon="🏀",
    layout="wide",
)

# -----------------------------
# Header
# -----------------------------
st.title("Blueprint Prep 🏀")
st.caption("NCAA Matchup Analytics for Coaches")


# -----------------------------
# Sidebar
# -----------------------------
conf_hist_enriched = load_csv_data("conference_history_enriched.csv")    # load selector data

with st.sidebar:
    st.title("Matchup Selection")

    season = st.selectbox("Season", options=[2026, 2025, 2024])
    division = st.selectbox("Division", options=["Mens", "Womens"])

    conference_options = get_conference_options(
        conf_hist_enriched=conf_hist_enriched,
        season=season,
        division=division,
        include_all=True,
    )

    team_a_conf = st.selectbox("Team A Conference", options=conference_options)
    team_a_options = get_conference_teams(
        conf_hist_enriched=conf_hist_enriched,
        conference=team_a_conf,
        season=season,
        division=division,
    )
    team_a = st.selectbox("Team A", options=team_a_options)

    team_b_conf = st.selectbox("Team B Conference", options=conference_options)
    team_b_options = get_conference_teams(
        conf_hist_enriched=conf_hist_enriched,
        conference=team_b_conf,
        season=season,
        division=division,
    )
    # exclude Team A selection from Team B options
    team_b_options = [team for team in team_b_options if team != team_a]
    team_b = st.selectbox("Team B", options=team_b_options)
    
    
# -----------------------------
# Load & validate CSV
# -----------------------------

teams_df = load_csv_data("teams.csv")
advanced_df = load_csv_data("games_advanced_box_score_stats.csv")
srs_ratings_df = load_csv_data("srs_ratings.csv")

# filter league level data for league averages
adv_league_data = filter_league_data(df=advanced_df, division=division, season=season)
league_ratings_df = filter_league_data(df=srs_ratings_df, division=division, season=season)

# filter Team A and Team B advanced stats
team_a_adv_stats = filter_team_stats(df=advanced_df, team_name=team_a,
                                     season=season, division=division,
                                     add_names=True, teams_df=teams_df
                                     )

team_b_adv_stats = filter_team_stats(df=advanced_df, team_name=team_b,
                                     season=season, division=division,
                                     add_names=True, teams_df=teams_df
                                     )

# filter Team A and Team B ratings
team_a_ratings = filter_team_ratings(df=srs_ratings_df, team_name=team_a,
                                     season=season, division=division,
                                     add_names=True, teams_df=teams_df
                                     )

team_b_ratings = filter_team_ratings(df=srs_ratings_df, team_name=team_b,
                                     season=season, division=division,
                                     add_names=True, teams_df=teams_df
                                     )


# -----------------------------
# Body
# -----------------------------

# --- Tale of the Tape ---
st.markdown("## Tale of the Tape")

# temporary record placeholders
team_a_record = "18 - 4"
team_b_record = "21 - 2"

# team columns
col1, col2 = st.columns(2)

with col1:
    st.html(f"""
    <div style="text-align: center;">
        <h1 style="margin-bottom: 0;">{team_a}</h1>
        <div style="margin-top: 0;">{team_a_record}</div>
    </div>
    """)

with col2:
    st.html(f"""
    <div style="text-align: center;">
        <h1 style="margin-bottom: 0;">{team_b}</h1>
        <div style="margin-top: 0;">{team_b_record}</div>
    </div>
    """)

tab1, tab2, tab3 = st.tabs(["Ratings", "Matchup Edge", "Four Factors"])

with tab1:
    mirrored_fig = plot_matchup_ratings(
        team_a=team_a,
        team_b=team_b,
        team_a_ratings=team_a_ratings,
        team_b_ratings=team_b_ratings,
        league_ratings_df=league_ratings_df
    )
    st.plotly_chart(mirrored_fig, use_container_width=True)
    # st.caption("Bars are normalized within each metric row. Labels show the actual values.")

with tab2:
    edge_fig = plot_matchup_edge_overview(
        team_a=team_a,
        team_b=team_b,
        team_a_ratings=team_a_ratings,
        team_b_ratings=team_b_ratings,
    )
    st.plotly_chart(edge_fig, use_container_width=True)
    # st.caption(f"Left = {team_a} advantage, Right = {team_b} advantage.")
    
with tab3:
    st.info("Four factors matchup plot go here")
    
# --- Matchup Prediction ---
st.markdown("## Matchup Prediction")
st.info("Model prediction card will go here.")


# --- Team Trend Analysis ---
#
# This section compares performance trends throughout the season for both teams in three separate tabs:
#    1. Raw Ratings (Offensive, Defensive, Net)
#    2. Adjusted Ratings (Offensive, Defensive, Net)
#    3. Four Factors  

st.markdown("## Team Trend Analysis")
tab1, tab2, tab3 = st.tabs(["Raw Ratings", "Four Factors", "Adjusted Ratings"])
# Tab 1 - Compare Raw Ratings Trends
with tab1:
    st.markdown("### Ratings Trend Comparison")
    ratings_a_col, ratings_b_col = st.columns(2)
    
    ratings_cols = ['NetRtg', 'ORtg', 'DRtg']
        
    # Team A Metrics (Offense)
    with ratings_a_col:
        team_a_ratings_fig, _ = plot_team_trends(
            df=team_a_adv_stats,
            team_name=team_a,
            title="Raw Ratings",
            cols=ratings_cols,
            x_col=None,
            sort_by=None,
            ncols=1,
            rolling_window=5,
            league_df=adv_league_data,
            show_league_avg=True,
        )
        st.pyplot(team_a_ratings_fig, use_container_width=False)

    # Team B's Opponents Metrics (Defense)
    with ratings_b_col:
        team_b_ratings_fig, _ = plot_team_trends(
            df=team_b_adv_stats,
            team_name=team_b,
            title="Raw Ratings",
            cols=ratings_cols,
            x_col=None,
            sort_by=None,
            ncols=1,
            rolling_window=5,
            league_df=adv_league_data,
            show_league_avg=True,
        )
        st.pyplot(team_b_ratings_fig, use_container_width=False)


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
            team_a_off_adv_fig, _ = plot_team_trends(
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
            team_b_def_adv_fig, _ = plot_team_trends(
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
            team_a_def_adv_fig, _ = plot_team_trends(
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
            team_b_off_adv_fig, _ = plot_team_trends(
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
            
# Tab 3 - Compare Adjusted Ratings Trends
with tab3:
    st.markdown("### Adjusted Ratings Trend Comparison")
           
st.markdown(f"### {team_a} Advanced Stats Schedule")
st.dataframe(team_a_adv_stats)
st.markdown(f"### {team_b} Advanced Stats Schedule")
st.dataframe(team_b_adv_stats)
    