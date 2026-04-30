"""Tools package for backend helper modules."""

import os
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "movies.csv")

engine = create_engine(f"sqlite:///{DB_PATH}")

def initialize_database():
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='movies';")
        ).fetchone()

    if exists:
        print("✅ DB already initialized")
        return

    if not os.path.exists(CSV_PATH):
        print("❌ movies.csv not found")
        return

    df = pd.read_csv(CSV_PATH)
    df.to_sql("movies", engine, index=False, if_exists="replace")
    print("✅ DB initialized from CSV")