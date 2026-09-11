"""
Export the dbt marts to flat CSVs for Tableau Desktop to connect to directly.
Mirrors the export step used for the Workforce/HR and Logistics Tableau projects.
"""
import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "dbt_project" / "warehouse.duckdb"
OUT_DIR = Path(__file__).parent.parent / "tableau_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    con = duckdb.connect(str(DB_PATH))

    con.execute(f"""
        COPY (
            select
                interview_id,
                source_id,
                candidate_name,
                role_norm,
                role_display,
                role_family,
                decision,
                reason_category,
                is_requirement_leak,
                resume_word_count,
                transcript_word_count
            from fct_interviews
        ) TO '{OUT_DIR / "fct_interviews.csv"}' (FORMAT CSV, HEADER)
    """)

    con.execute(f"""
        COPY dim_role TO '{OUT_DIR / "dim_role.csv"}' (FORMAT CSV, HEADER)
    """)

    con.close()
    for f in OUT_DIR.glob("*.csv"):
        print(f"{f.name}: {f.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
