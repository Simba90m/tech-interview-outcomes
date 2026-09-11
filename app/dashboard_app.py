import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(page_title="Tech Interview Outcomes Explorer", layout="wide")


@st.cache_data
def load_data():
    fct = pd.read_parquet(DATA_DIR / "fct_interviews.parquet")
    dim_role = pd.read_parquet(DATA_DIR / "dim_role.parquet")
    detail = pd.read_parquet(DATA_DIR / "interview_detail.parquet")
    return fct, dim_role, detail


fct, dim_role, detail = load_data()

st.title("Tech Interview Outcomes Explorer")
st.caption(
    "Companion app for the Tech Interview Outcomes Tableau dashboard. "
    "10,174 real interview records across 38 tech and non-tech roles: "
    "selection rate, why candidates are selected or rejected, and how resume "
    "and interview depth relate to the outcome."
)

with st.sidebar:
    st.header("Filters")
    families = sorted(fct["role_family"].dropna().unique())
    picked_families = st.multiselect("Role family", families, default=families)
    roles_available = sorted(
        fct.loc[fct["role_family"].isin(picked_families), "role_display"].dropna().unique()
    )
    picked_roles = st.multiselect("Role", roles_available, default=roles_available)
    exclude_leak = st.checkbox(
        "Exclude the data-quality anomaly rows (requirement text leaked into reason field)",
        value=True,
    )

filtered = fct[fct["role_family"].isin(picked_families) & fct["role_display"].isin(picked_roles)]
if exclude_leak:
    filtered = filtered[~filtered["is_requirement_leak"]]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Interviews", f"{len(filtered):,}")
col2.metric("Selected", f"{(filtered['decision'] == 'select').sum():,}")
sel_rate = (filtered["decision"] == "select").mean() * 100 if len(filtered) else 0
col3.metric("Selection rate", f"{sel_rate:.1f}%")
col4.metric(
    "Data quality anomaly rows",
    f"{fct['is_requirement_leak'].sum():,}",
    help="Rows where the reason field contains leaked job-requirement text instead of a real decision reason.",
)

st.divider()

left, right = st.columns([1.3, 1])

with left:
    st.subheader("Selection rate by role")
    role_stats = (
        filtered.groupby(["role_display", "role_family"])
        .agg(interviews=("interview_id", "count"), selected=("decision", lambda s: (s == "select").sum()))
        .reset_index()
    )
    role_stats["selection_rate"] = (role_stats["selected"] / role_stats["interviews"] * 100).round(1)
    role_stats = role_stats.sort_values("selection_rate")
    fig = px.bar(
        role_stats,
        x="selection_rate",
        y="role_display",
        color="role_family",
        orientation="h",
        labels={"selection_rate": "Selection rate (%)", "role_display": "", "role_family": "Role family"},
        height=max(400, len(role_stats) * 22),
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Why candidates are selected or rejected")
    reason_stats = (
        filtered.groupby(["reason_category", "decision"]).size().reset_index(name="count")
    )
    fig2 = px.bar(
        reason_stats,
        x="count",
        y="reason_category",
        color="decision",
        orientation="h",
        barmode="group",
        labels={"count": "Interviews", "reason_category": "", "decision": "Decision"},
        color_discrete_map={"select": "#0F9B8E", "reject": "#D6006C"},
    )
    st.plotly_chart(fig2, width="stretch")

    st.subheader("Resume & transcript length vs outcome")
    length_stats = filtered.groupby("decision")[["resume_word_count", "transcript_word_count"]].mean().round(0)
    st.dataframe(length_stats.rename(columns={
        "resume_word_count": "Avg resume words",
        "transcript_word_count": "Avg transcript words",
    }))

st.divider()
st.subheader("Look up a candidate")
lookup_id = st.selectbox("Interview ID", filtered["interview_id"].sort_values().tolist())
if lookup_id:
    row = filtered[filtered["interview_id"] == lookup_id].iloc[0]
    text_row = detail[detail["interview_id"] == lookup_id].iloc[0]
    st.markdown(
        f"**{row['candidate_name']}**, {row['role_display']}. "
        f"Decision: **{row['decision'].upper()}**. Reason category: {row['reason_category']}"
    )
    st.caption(text_row["reason_raw"])
    tab1, tab2, tab3 = st.tabs(["Job description", "Resume", "Transcript"])
    tab1.write(text_row["job_description"])
    tab2.text(text_row["resume_text"])
    tab3.text(text_row["transcript_text"])

st.divider()
st.caption(
    "Data: [AI Recruitment Pipeline Dataset](https://www.kaggle.com/datasets/yaswanthkumary/ai-recruitment-pipeline-dataset) on Kaggle. "
    "Modeled with dbt (staging to marts, tested). Reason categories are keyword-classified from the source text, "
    "not an original field in the dataset."
)
