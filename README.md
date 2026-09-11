# Tech Interview Outcomes

An analysis of 10,174 real tech-industry interview records: what predicts a "select" versus a "reject" decision, across 38 roles and 8 role families. Built with dbt (DuckDB), explored in a Streamlit companion app, and visualized in Tableau Public.

- **Tableau Public dashboard**: link here once published (see `TABLEAU_BUILD_SPEC.md`)
- **Streamlit companion app**: link here once deployed to Streamlit Community Cloud
- Third project in a portfolio series alongside [Workforce & HR Analytics](#) and [Logistics & Supply Chain Analytics](#)

## Why this project exists, and why the scope changed mid-build

The original plan for this project was a time-to-hire and pipeline-conversion dashboard, tracking how candidates move through recruiting stages over time. After an extensive search for a public dataset with real funnel stages and real dates, none existed. Rather than fabricate synthetic funnel data and present it as real, the scope was reframed around a dataset that is genuinely real: 10,174 tech interview records with resumes, transcripts, and outcomes. The question changed from "how long does hiring take" to "what actually separates a selected candidate from a rejected one." That is a more honest use of the data that was actually available, and it is still directly relevant to recruiting and HR analytics work.

## Data

Source: [AI Recruitment Pipeline Dataset](https://www.kaggle.com/datasets/yaswanthkumary/ai-recruitment-pipeline-dataset) on Kaggle, 10,174 rows, no missing values. Each row is one interview: candidate name, role applied for, full transcript text, full resume text, the decision (select/reject), a free-text reason for the decision, and the job description.

### Two real data quality issues found and disclosed

Rather than clean these silently, both are flagged as first-class fields in the model so anyone using this data can see them:

1. **Leaked requirement text (`is_requirement_leak`)**: about 9.5% of rows (963 of 10,174) have the "reason for decision" field populated with a job-requirement string (`expected_experience: X years, domains: ...`) instead of a genuine decision reason. These are a data entry or generation artifact in the source, not a real interview outcome. They are flagged, categorized separately as "Data Quality: Requirement Text Leaked", and excluded by default in both the Streamlit app and the Tableau dashboard (with a visible toggle to include them).
2. **Duplicate source IDs**: three pairs of distinct candidates (different names, different roles, different decisions) shared the same `ID` value in the raw data, a genuine collision bug in the source. A surrogate `interview_id` was generated (`row_number() over (order by "ID")`) to guarantee a unique key; the original value is preserved as `source_id` for traceability.

## Data model

Built with dbt against a local DuckDB warehouse, following the same staging-to-marts pattern as the other two projects in this series:

- **`raw.raw_interviews`**: the source CSV, loaded via a Python/pandas script (`scripts/01_load_raw.py`), not a dbt seed, since a 10,174-row table with long free text is a poor fit for seeds.
- **`seed_role_family`** (dbt seed): a curated 38-row lookup mapping each raw role string to a clean display name and one of 8 role families (Software Engineering, Data & AI, Infrastructure & Cloud, Security, Design, Product & Business, Hardware & Robotics, Non-Technical). Built by hand rather than with `initcap()`, since naive title-casing mangles acronym-bearing roles like "AR/VR Developer" and "UI/UX Designer".
- **`stg_interviews`**: cleans role casing, derives resume/transcript word counts, classifies each free-text reason into one of 8 categories via keyword matching (the 539 unique reason phrases in the raw data are too numerous and combinatorial for an exact-match lookup), and flags the leaked-requirement rows.
- **`stg_role_family`**: passthrough of the seed.
- **`dim_role`**: one row per role, with total interviews, total selected, and selection rate.
- **`fct_interviews`**: one row per interview, joined to role family and display name, ready for BI tools.

20 dbt tests pass across both layers (uniqueness and not-null on keys, accepted values on `decision`, referential integrity between the fact and dimension tables).

## Key findings

- Overall selection rate sits close to 50% across the dataset, with real variation by role, roles like Robotics Engineer and several non-technical roles trend higher, while some Data & AI and Infrastructure & Cloud roles trend lower.
- "Technical Skills" is by far the largest reason category on both sides of the decision (roughly 3,000 select and 3,000 reject mentions), meaning technical ability is cited as often as a reason to reject as it is to select, so it is discriminating but not one-directional.
- Resume and transcript length barely differ between selected and rejected candidates (about 336-338 average resume words either way), a mildly counter-intuitive finding worth noting: longer documents are not, on their own, predictive of outcome in this data.

## Repository structure

```
tech-interview-outcomes/
  data/                  raw source CSV
  dbt_project/           staging + marts models, seeds, tests
  scripts/               load raw data, export parquet (app) and CSV (Tableau)
  app/                   Streamlit companion app + bundled parquet snapshots
  tableau_data/          CSV exports for Tableau Desktop
  TABLEAU_BUILD_SPEC.md  chart-by-chart Tableau build instructions
```

## Running the Streamlit app locally

```
cd app
pip install -r requirements.txt
streamlit run dashboard_app.py
```

The app reads the bundled parquet snapshots in `app/data/`, so it runs from a fresh clone without needing dbt or DuckDB installed.

## Rebuilding the data from scratch

```
python scripts/01_load_raw.py
cd dbt_project && dbt build
cd ..
python scripts/02_export_parquet.py
python scripts/03_export_tableau.py
```
