import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

# --- Altair setup: avoid 5k row error and ensure Altair is ready ---
alt.data_transformers.disable_max_rows()

DB_PATH = "baseball.db"

EXPECTED = {
    "batting_avg": ["Name", "Team", "Year", "Batting_Average"],
    "home_runs": ["Name", "Career_Home_Runs"],
    "career_strikeouts": ["Name", "League", "Career_Strikeouts"],
}

def read_table(conn, table, cols):
    """Read a table if it exists; otherwise return an empty DF with expected columns."""
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        # If the table exists but has different col names, standardize if possible
        # (light touch: only keep expected columns that are present)
        present = [c for c in cols if c in df.columns]
        if present:
            return df[present]
        # If nothing matches, return empty with expected schema
        return pd.DataFrame(columns=cols)
    except Exception:
        return pd.DataFrame(columns=cols)

def load_data():
    conn = sqlite3.connect(DB_PATH)
    batting = read_table(conn, "batting_avg", EXPECTED["batting_avg"])
    hr = read_table(conn, "home_runs", EXPECTED["home_runs"])
    k = read_table(conn, "career_strikeouts", EXPECTED["career_strikeouts"])
    conn.close()
    return batting, hr, k

st.set_page_config(page_title="Baseball Stats Dashboard", layout="wide")
st.title("⚾ Baseball Stats Dashboard")

df_batting, df_home_runs, df_career_strikeouts = load_data()

# --- Sidebar filters, guarded by data availability ---
st.sidebar.header("Filters")

# Filters for batting avg
if not df_batting.empty:
    all_years = sorted(df_batting["Year"].dropna().unique())
    all_teams = sorted(df_batting["Team"].dropna().unique())
    years = st.sidebar.multiselect("Select Year(s)", all_years, default=all_years)
    teams = st.sidebar.multiselect("Select Team(s)", all_teams, default=all_teams)
else:
    years, teams = [], []

# Slider for home runs
if not df_home_runs.empty and "Career_Home_Runs" in df_home_runs.columns:
    max_home_runs = int(df_home_runs["Career_Home_Runs"].max())
    min_home_runs = st.sidebar.slider("Career Home Runs (min)", 0, max_home_runs, min(100, max_home_runs))
else:
    min_home_runs = None

# League select
if not df_career_strikeouts.empty and "League" in df_career_strikeouts.columns:
    leagues = sorted(df_career_strikeouts["League"].dropna().unique())
    league = st.sidebar.selectbox("Select League", leagues) if leagues else None
else:
    league = None

# --- Chart 1: Batting Average Over Time ---
st.header("Batting Average Over Time by Team")
if df_batting.empty:
    st.info("No batting average data found. Ensure `data/batting_avg.csv` (or DB table) is loaded.")
else:
    df_line = df_batting
    if years:
        df_line = df_line[df_line["Year"].isin(years)]
    if teams:
        df_line = df_line[df_line["Team"].isin(teams)]

    if df_line.empty:
        st.info("No rows match the selected Year/Team filters.")
    else:
        try:
            chart = (
                alt.Chart(df_line)
                .mark_line(point=True)
                .encode(
                    x=alt.X("Year:O", title="Year"),
                    y=alt.Y("Batting_Average:Q", title="Batting Average"),
                    color=alt.Color("Team:N", title="Team"),
                    tooltip=["Name", "Team", "Year", "Batting_Average"]
                )
                .properties(width=900, height=400)
            )
            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.error(f"Could not render batting-average chart: {e}")

# --- Chart 2: Career Home Runs ---
st.header("Top Career Home Run Hitters")
if df_home_runs.empty or min_home_runs is None:
    st.info("No home run data found. Ensure `data/home_runs.csv` (or DB table) is loaded.")
else:
    df_hr = df_home_runs[df_home_runs["Career_Home_Runs"] >= min_home_runs]
    if df_hr.empty:
        st.info("No players meet the selected minimum career home runs.")
    else:
        try:
            bar = (
                alt.Chart(df_hr.sort_values("Career_Home_Runs", ascending=False))
                .mark_bar()
                .encode(
                    x=alt.X("Name:N", sort="-y", title="Player"),
                    y=alt.Y("Career_Home_Runs:Q", title="Career Home Runs"),
                    tooltip=["Name", "Career_Home_Runs"]
                )
                .properties(width=900, height=350)
            )
            st.altair_chart(bar, use_container_width=True)
            st.dataframe(
                df_hr[["Name","Career_Home_Runs"]]
                .sort_values("Career_Home_Runs", ascending=False),
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Could not render home-runs chart: {e}")

# --- Chart 3: Career Strikeouts by League (cumulative) ---
st.header("Career Strikeouts by League (Cumulative)")
if df_career_strikeouts.empty or league is None:
    st.info("No career strikeouts data found. Ensure `data/career_strikeouts.csv` (or DB table) is loaded.")
else:
    df_k = df_career_strikeouts[df_career_strikeouts["League"] == league].copy()
    df_k = df_k.sort_values("Career_Strikeouts")
    if df_k.empty:
        st.info(f"No strikeout data for league '{league}'.")
    else:
        df_k["Cumulative"] = df_k["Career_Strikeouts"].cumsum()
        try:
            area = (
                alt.Chart(df_k)
                .mark_area(opacity=0.5)
                .encode(
                    x=alt.X("Name:N", sort=None, title="Player"),
                    y=alt.Y("Cumulative:Q", title="Cumulative Career Strikeouts"),
                    tooltip=["Name", "Career_Strikeouts"]
                )
                .properties(width=900, height=350)
            )
            st.altair_chart(area, use_container_width=True)
        except Exception as e:
            st.error(f"Could not render strikeouts chart: {e}")

# --- Combined Stats for a Player ---
st.header("🔍 Combined Stats for a Player")
if df_batting.empty:
    st.info("Load batting data to use the player detail view.")
else:
    player_list = sorted(df_batting["Name"].dropna().unique())
    selected_player = st.selectbox("Select Player", player_list) if player_list else None

    if selected_player:
        df_combined = df_batting[df_batting["Name"] == selected_player].copy()
        if not df_home_runs.empty:
            df_combined = df_combined.merge(df_home_runs, on="Name", how="left")
        if not df_career_strikeouts.empty:
            df_combined = df_combined.merge(df_career_strikeouts, on="Name", how="left")

        if df_combined.empty:
            st.write("No combined stats found for this player.")
        else:
            keep_cols = [c for c in ["Year", "Batting_Average", "Career_Home_Runs", "Career_Strikeouts"] if c in df_combined.columns]
            if "Year" in keep_cols:
                st.dataframe(df_combined[keep_cols].set_index("Year"), use_container_width=True)
            else:
                st.dataframe(df_combined[keep_cols], use_container_width=True)
