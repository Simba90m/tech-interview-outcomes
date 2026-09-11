"""
Export the dbt marts to parquet snapshots bundled into the Streamlit app, so the
app runs from a fresh clone without needing to run dbt or hold the DuckDB file.
Mirrors the approach used in the Workforce/HR and Logistics projects.
"""
import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "dbt_project" / "warehouse.duckdb"
OUT_DIR = Path(__file__).parent.parent / "app" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    con = duckdb.connect(str(DB_PATH))

    con.execute(f"""
        COPY (
            select interview_id, source_id, candidate_name, role_norm, role_display,
                   role_family, decision, reason_category, is_requirement_leak,
                   resume_word_count, transcript_word_count
            from fct_interviews
        ) TO '{OUT_DIR / "fct_interviews.parquet"}' (FORMAT PARQUET)
    """)

    con.execute(f"""
        COPY dim_role TO '{OUT_DIR / "dim_role.parquet"}' (FORMAT PARQUET)
    """)

    con.execute(f"""
        COPY (
            select interview_id, reason_raw, job_description, resume_text, transcript_text
            from stg_interviews
        ) TO '{OUT_DIR / "interview_detail.parquet"}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    con.close()
    for f in OUT_DIR.glob("*.parquet"):
        print(f"{f.name}: {f.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
