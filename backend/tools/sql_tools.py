from pathlib import Path

from sqlalchemy import create_engine, text
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BACKEND_DIR / "data.db"
engine = create_engine(f"sqlite:///{DB_PATH}")


def _query(sql, **params):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params).to_dict(orient="records")


def get_all_movies():
    return _query("SELECT * FROM movies ORDER BY rating DESC")


def get_best_movie():
    rows = _query("SELECT * FROM movies ORDER BY rating DESC LIMIT 1")
    return rows[0] if rows else None


def get_top_titles(year=None):
    if year:
        return _query(
            "SELECT title, genre, release_year, rating, total_views, trending_score "
            "FROM movies WHERE release_year = :y ORDER BY rating DESC LIMIT 10",
            y=int(year),
        )
    return _query(
        "SELECT title, genre, release_year, rating, total_views, trending_score "
        "FROM movies ORDER BY rating DESC LIMIT 10"
    )


def get_top_titles_2025():
    return get_top_titles(year=2025)


def get_title_comparison(title_a: str, title_b: str):
    rows = _query(
        "SELECT title, genre, release_year, rating, total_views, box_office_m, budget_m, trending_score "
        "FROM movies WHERE LOWER(title) LIKE :a OR LOWER(title) LIKE :b",
        a=f"%{title_a.lower()}%",
        b=f"%{title_b.lower()}%",
    )
    return rows


def get_trending_title(title: str):
    rows = _query(
        "SELECT title, genre, rating, total_views, trending_score, release_date "
        "FROM movies WHERE LOWER(title) LIKE :t ORDER BY trending_score DESC",
        t=f"%{title.lower()}%",
    )
    return rows


def get_city_engagement(month: str = None):
    if month:
        return _query(
            "SELECT city, country, total_views, unique_viewers, avg_watch_time_min, engagement_score "
            "FROM regional_performance WHERE LOWER(month) = :m ORDER BY engagement_score DESC LIMIT 10",
            m=month.lower(),
        )
    return _query(
        "SELECT city, country, SUM(total_views) as total_views, "
        "AVG(engagement_score) as avg_engagement "
        "FROM regional_performance GROUP BY city, country "
        "ORDER BY avg_engagement DESC LIMIT 10"
    )


def get_genre_performance():
    return _query(
        "SELECT genre, COUNT(*) as title_count, AVG(rating) as avg_rating, "
        "SUM(total_views) as total_views, AVG(trending_score) as avg_trending "
        "FROM movies GROUP BY genre ORDER BY avg_rating DESC"
    )


def get_comedy_analysis():
    movies = _query("SELECT movie_id, title, rating, total_views FROM movies WHERE LOWER(genre) = 'comedy'")
    ids = tuple(m["movie_id"] for m in movies) if movies else (0,)
    placeholders = ",".join(str(i) for i in ids)
    reviews = _query(
        f"SELECT sentiment, COUNT(*) as count FROM reviews "
        f"WHERE movie_id IN ({placeholders}) GROUP BY sentiment"
    )
    spend = _query(
        f"SELECT SUM(spend_usd) as total_spend, SUM(conversions) as total_conversions "
        f"FROM marketing_spend WHERE LOWER(title) IN "
        f"({','.join(repr(m['title'].lower()) for m in movies)})"
    ) if movies else []
    return {"movies": movies, "sentiment": reviews, "marketing": spend}


def get_marketing_roi():
    return _query(
        "SELECT title, channel, spend_usd, impressions, clicks, conversions, "
        "ROUND(CAST(conversions AS FLOAT)/spend_usd*1000, 2) as conversions_per_1k_spend "
        "FROM marketing_spend ORDER BY conversions_per_1k_spend DESC LIMIT 15"
    )
