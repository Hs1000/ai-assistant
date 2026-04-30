from pathlib import Path

from sqlalchemy import create_engine
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DB_PATH = BACKEND_DIR / "data.db"
DATA_DIR = PROJECT_ROOT / "data"

engine = create_engine(f"sqlite:///{DB_PATH}")

CSV_TABLES = {
    "movies": DATA_DIR / "movies.csv",
    "viewers": DATA_DIR / "viewers.csv",
    "watch_activity": DATA_DIR / "watch_activity.csv",
    "reviews": DATA_DIR / "reviews.csv",
    "marketing_spend": DATA_DIR / "marketing_spend.csv",
    "regional_performance": DATA_DIR / "regional_performance.csv",
}


def load_data():
    for table, csv_path in CSV_TABLES.items():
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df.to_sql(table, engine, if_exists="replace", index=False)
            print(f"Loaded {len(df)} rows into '{table}'")
        else:
            print(f"WARNING: {csv_path} not found, skipping '{table}'")
