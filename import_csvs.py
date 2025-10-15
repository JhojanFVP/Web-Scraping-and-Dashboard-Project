from pathlib import Path
import pandas as pd
import sqlite3

DB_PATH = Path("baseball.db")
CSV_DIR = Path("data")  # <-- use the local data/ folder

REQUIRED = {
    "batting_avg.csv": "batting_avg",
    "home_runs.csv": "home_runs",
    "career_strikeouts.csv": "career_strikeouts",
}

CSV_DTYPES = {
    "batting_avg": {"Name": str, "Team": str, "Year": "Int64", "Batting_Average": "float"},
    "home_runs": {"Name": str, "Career_Home_Runs": "Int64"},
    "career_strikeouts": {"Name": str, "League": str, "Career_Strikeouts": "Int64"},
}

def import_one(csv_name, table_name, conn):
    csv_path = CSV_DIR / csv_name
    if not csv_path.exists():
        print(f"⚠️  Skipping {table_name}: CSV not found at {csv_path}")
        return
    df = pd.read_csv(csv_path)
    # normalize column names
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    # apply dtypes if declared
    if table_name in CSV_DTYPES:
        for col, typ in CSV_DTYPES[table_name].items():
            if col in df.columns:
                df[col] = df[col].astype(typ, errors="ignore")
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"✅ Loaded {csv_name} -> table '{table_name}' ({len(df)} rows)")

def main():
    if not CSV_DIR.exists():
        print(f"CSV directory not found: {CSV_DIR.resolve()}")
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        for csv_name, table in REQUIRED.items():
            import_one(csv_name, table, conn)
        # show tables
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print("📦 Tables in DB:", [r[0] for r in cur.fetchall()])
    finally:
        conn.close()

if __name__ == "__main__":
    main()

