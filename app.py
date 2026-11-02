"""PhonePe Insights: a beginner-friendly Streamlit dashboard."""

import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from case_studies import CASES
from charts import COLORS, LABELS, bar_chart, india_map, pretty_name, style_chart
from queries import DATABASE, categories, districts, periods, run_query, state_summary, top_places, trend

BASE_DIR = Path(__file__).resolve().parent
st.set_page_config(page_title="PhonePe Insights", page_icon="📊", layout="wide")


def format_number(value, money=False):
    """Display Indian units; charts and CSVs retain the original numbers."""
    if pd.isna(value):
        return "Unavailable"
    prefix = "₹" if money else ""
    if money and abs(value) >= 1_000_000_000_000:
        return f"{prefix}{value / 1_000_000_000_000:,.2f} L Cr"
    if abs(value) >= 10_000_000:
        return f"{prefix}{value / 10_000_000:,.2f} Cr"
    if abs(value) >= 100_000:
        return f"{prefix}{value / 100_000:,.2f} L"
    return f"{prefix}{value:,.0f}"


def download_table(data, filename, key):
    st.download_button("Download CSV", data.to_csv(index=False).encode("utf-8"),
                       file_name=filename, mime="text/csv", key=key)


st.markdown("""
<style>
    .block-container {padding-top: 4rem; padding-bottom: 2rem; max-width: 1550px;}
    [data-testid="stSidebar"] {border-right: 1px solid #343047;}
    [data-testid="stMetric"] {background: #1b1b2e; border: 1px solid #343047;
        border-radius: 14px; padding: 18px;}
    [data-testid="stMetricLabel"] {color: #b9b5cf;}
    [data-testid="stMetricValue"] {font-size: 1.7rem;}
    h1 {letter-spacing: -1.4px;}
    .eyebrow {font-size: 12px; color: #a78bfa; letter-spacing: 3px; font-weight: 700;}
    .hero-note {color: #b9b5cf; font-size: 16px; margin-bottom: 28px;}
</style>
""", unsafe_allow_html=True)

if not DATABASE.exists():
    st.title("PhonePe Insights")
    st.info("Load the dataset first. Run `python load_data.py` in the project folder.")
    st.stop()

with st.sidebar:
    st.markdown("### ◈ PhonePe Insights")
    st.caption("A digital payments data explorer")
    st.divider()
    topic = st.selectbox("Explore", ["Transactions", "Users", "Insurance"])
    available_periods = periods(topic)
    years = sorted(available_periods["year"].unique().tolist(), reverse=True)
    year = st.selectbox("Year", years)
    quarters = sorted(available_periods.loc[available_periods["year"] == year, "quarter"].tolist())
    quarter = st.selectbox("Quarter", quarters, index=len(quarters) - 1,
                           format_func=lambda q: f"Q{q} · " + ["Jan–Mar", "Apr–Jun", "Jul–Sep", "Oct–Dec"][q - 1])
    summary = state_summary(topic, year, quarter)
    state = st.selectbox("Region", ["india"] + sorted(summary["state"].tolist()),
                         format_func=lambda s: "All India" if s == "india" else pretty_name(s))
    metrics = ["registered_users", "app_opens"] if topic == "Users" else ["transaction_count", "amount"]
    metric = st.selectbox("Map and chart metric", metrics, format_func=lambda m: LABELS[m])
    st.divider()
    st.caption("SOURCE · PHONEPE PULSE")
    st.caption("Preserved legacy dataset\n\n2018–2024 · Quarterly data")
    st.caption("Insurance starts in 2020. Historical data, not a live payment feed.")
    with st.expander("Source details"):
        metadata = json.loads((BASE_DIR / "data" / "source.json").read_text(encoding="utf-8"))
        st.write(metadata["dataset"])
        st.code(metadata["commit"], language=None)
        st.link_button("View dataset source", metadata["source_url"].removesuffix(".git"))

region = "All India" if state == "india" else pretty_name(state)
st.markdown('<div class="eyebrow">THE DIGITAL PAYMENTS LANDSCAPE</div>', unsafe_allow_html=True)
st.title("Follow the flow of payments.")
st.markdown(f'<div class="hero-note">{region} &nbsp; / &nbsp; Q{quarter} {year} &nbsp; / &nbsp; {topic}</div>',
            unsafe_allow_html=True)

selected = summary if state == "india" else summary[summary["state"] == state]
totals = selected.select_dtypes(include="number").sum(min_count=1)
history = trend(topic, state)
current_index = history.index[(history["year"] == year) & (history["quarter"] == quarter)][0]
current_value = history.loc[current_index, metric]
previous_value = history.loc[current_index - 1, metric] if current_index > 0 else None
growth = None
if previous_value is not None and pd.notna(previous_value) and previous_value > 0:
    # Compare only consecutive quarters, not an arbitrary previous observation.
    current_period = year * 4 + quarter
    previous_period = int(history.loc[current_index - 1, "year"]) * 4 + int(history.loc[current_index - 1, "quarter"])
    if current_period - previous_period == 1:
        growth = (current_value / previous_value - 1) * 100

cards = st.columns(4)
if topic == "Users":
    cards[0].metric("Registered users", format_number(totals["registered_users"]))
    cards[1].metric("App opens", format_number(totals["app_opens"]))
    ratio = totals["app_opens"] / totals["registered_users"] if totals["registered_users"] else None
    cards[2].metric("Opens / registered user", "Unavailable" if pd.isna(ratio) else f"{ratio:.2f}")
else:
    cards[0].metric("Total transactions", format_number(totals["transaction_count"]))
    cards[1].metric("Total value", format_number(totals["amount"], money=True))
    average = totals["amount"] / totals["transaction_count"] if totals["transaction_count"] else None
    cards[2].metric("Average transaction", "Unavailable" if pd.isna(average) else f"₹{average:,.2f}")
cards[3].metric("Growth vs previous quarter",
                "Unavailable" if growth is None else f"{growth:+.2f}%")
st.write("")
st.caption("All India totals sum the state records used in the map. Some historical quarters differ slightly from the source's separately published national totals.")

explore_tab, trends_tab, sql_tab, guide_tab = st.tabs(["Explore India", "Trends & categories", "SQL case studies", "How it works"])

with explore_tab:
    map_column, ranking_column = st.columns([1.65, 1], gap="large")
    with map_column:
        st.subheader("Where the activity happens")
        map_level = st.radio("Map level", ["States", "Districts"], horizontal=True)
        district_data = districts(topic, year, quarter, state)
        map_data = district_data if map_level == "Districts" else selected
        if map_data.empty or map_data[metric].isna().all():
            st.info("This metric is unavailable for this selection.")
        else:
            figure, unmatched = india_map(map_data, metric, district_view=map_level == "Districts")
            st.plotly_chart(figure, width="stretch", key="india_map")
            st.caption("Hover to inspect values. Use the chart toolbar to zoom or save an image.")
            if map_level == "Districts":
                st.caption("District boundaries are an older geographic reference. New or renamed districts may be absent; use the table for complete data.")
            if unmatched:
                with st.expander(f"{len(unmatched)} places could not be matched to map boundaries"):
                    st.write(", ".join(unmatched))
                    st.caption("These places remain included in totals, rankings and downloads.")
    with ranking_column:
        st.subheader("Leaders at a glance")
        rank_level = st.radio("Rank places", ["States", "Districts", "PIN codes"], horizontal=True)
        entity_type = {"States": "states", "Districts": "districts", "PIN codes": "pincodes"}[rank_level]
        rank_metric = "registered_users" if topic == "Users" else metric
        leaders = top_places(topic, year, quarter, state, entity_type, rank_metric)
        if leaders.empty:
            st.info("No published data for this ranking and period.")
        else:
            st.plotly_chart(bar_chart(leaders, "entity_name", rank_metric), width="stretch", key="rank_chart")
            leader = leaders.iloc[0]
            st.info(f"{pretty_name(leader['entity_name'])} leads this selection with "
                    f"{format_number(leader[rank_metric], money=rank_metric == 'amount')} "
                    f"{LABELS[rank_metric].lower()}.")
            download_table(leaders, "top_places.csv", "download_leaders")
        if topic == "Users":
            st.caption("User rankings use registered users. Top PIN-code data has no app-open metric.")
        if rank_level == "PIN codes":
            st.caption("PIN-code ranks cover the source's published top list. Sorting by value only reorders that subset.")
    with st.expander("View the numbers behind the map"):
        st.dataframe(map_data, hide_index=True, width="stretch")
        download_table(map_data, "map_data.csv", "download_map")

with trends_tab:
    st.subheader(f"{LABELS[metric]} over time · {region}")
    history["period"] = history["year"].astype(str) + " Q" + history["quarter"].astype(str)
    chart = px.line(history, x="period", y=metric, markers=True, labels=LABELS,
                     color_discrete_sequence=COLORS)
    st.plotly_chart(style_chart(chart), width="stretch", key="trend_chart")
    st.caption("The trend covers all available quarters for the selected region; year and quarter filters select the overview period.")
    if topic == "Users":
        st.caption("Registered users are cumulative at quarter end. Summing them over time would double count users.")
    else:
        category_data = categories(topic, year, quarter, state)
        left, right = st.columns(2)
        with left:
            st.subheader("Category mix")
            pie = px.pie(category_data, names="category", values=metric, hole=0.65,
                         color_discrete_sequence=COLORS)
            st.plotly_chart(style_chart(pie), width="stretch", key="category_chart")
        with right:
            st.subheader("Category totals")
            st.dataframe(category_data, hide_index=True, width="stretch")
            download_table(category_data, "categories.csv", "download_categories")
    st.dataframe(history, hide_index=True, width="stretch")
    download_table(history, "quarterly_trend.csv", "download_trend")

with sql_tab:
    st.subheader("Ask a business question. Read the SQL.")
    st.caption(f"Case studies use All India · Q{quarter} {year}. Region and topic filters affect the Explore and Trends tabs.")
    case_name = st.selectbox("Business case", list(CASES))
    case = CASES[case_name]
    st.write(case["question"])
    st.code(case["sql"], language="sql")
    parameters = (year, quarter, year, quarter) if case.get("repeat_parameters") else (year, quarter)
    result = run_query(case["sql"], parameters)
    if result.empty:
        st.info("No source data for this case in the selected quarter. Insurance data starts in 2020.")
    else:
        st.dataframe(result, hide_index=True, width="stretch")
        st.info("Suggested action: " + case["recommendation"])
        download_table(result, "business_case.csv", "download_case")

with guide_tab:
    st.subheader("One simple path from files to insights")
    st.markdown("""
    **PhonePe JSON → Python lists → SQLite tables → SQL results → Pandas → Plotly → Streamlit**

    1. `load_data.py` reads JSON files using loops and inserts their values into SQL tables.
    2. `schema.sql` defines the nine tables and their columns.
    3. `queries.py` uses `SELECT`, `SUM`, `GROUP BY` and `ORDER BY` to answer questions.
    4. `charts.py` turns the query results into maps and bar charts.
    5. `app.py` adds filters, metric cards, tabs and download buttons.
    6. `case_studies.py` contains five explained business queries.

    **Reading the data correctly**

    - Counts measure transactions. Amounts are in Indian rupees.
    - Registered users are cumulative counts; app opens measure events during a quarter.
    - Insurance transaction count does not equal the number of insured people.
    - State totals use the full aggregated tables. Top tables are only published subsets.
    - This dataset cannot establish individual fraud, customer spending segments or competitor performance.
    - The legacy snapshot is separate from PhonePe's 2026 restated dataset.
    """)
    st.caption("Project created for learning. Geography is supplied by external map sources; unmatched districts are reported rather than assigned invented locations.")

st.divider()
st.caption("PhonePe Insights · Educational project · Python + SQL + Streamlit + Plotly")
