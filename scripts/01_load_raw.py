"""
Load the raw Kaggle interview dataset into the DuckDB warehouse's `raw` schema.

The dataset (10,174 rows) includes full resume and interview transcript text per
row, so it is loaded directly into DuckDB rather than as a dbt seed (dbt seeds are
meant for small reference tables and would be extremely slow to compile at this
size and text volume).
"""
import duckdb
import pandas as pd
import sys
from pathlib import Path

RAW_CSV = Path(__file__).parent.parent / "data" / "raw_interviews.csv"
DB_PATH = Path(__file__).parent.parent / "dbt_project" / "warehouse.duckdb"

def main():
    if not RAW_CSV.exists():
        sys.exit(f"Missing input file: {RAW_CSV}")

    df = pd.read_csv(RAW_CSV)
    print(f"Loaded {len(df):,} rows, {len(df.columns)} columns from {RAW_CSV.name}")

    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute("CREATE OR REPLACE TABLE raw.raw_interviews AS SELECT * FROM df")
    row_count = con.execute("SELECT COUNT(*) FROM raw.raw_interviews").fetchone()[0]
    print(f"raw.raw_interviews loaded: {row_count:,} rows")
    con.close()

if __name__ == "__main__":
    main()
