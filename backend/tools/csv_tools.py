import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _load(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{filename} not found")
    return pd.read_csv(path)


def analyze_movies():
    df = _load("movies.csv")
    df = df.dropna(subset=["rating", "genre"])
    top_movies = df.sort_values("rating", ascending=False).head(5)
    return {
        "top_movies": top_movies.to_dict(orient="records"),
        "genre_distribution": df["genre"].value_counts().to_dict(),
        "average_rating": float(round(df["rating"].mean(), 2)),
    }


def top_titles_from_csv(year=None):
    df = _load("movies.csv")
    if year:
        df = df[df["release_year"] == int(year)]
    df = df.sort_values("rating", ascending=False)
    genre_stats = (
        df.groupby("genre")
        .agg(avg_rating=("rating", "mean"), total_views=("total_views", "sum"), title_count=("title", "count"))
        .round(2)
        .reset_index()
        .sort_values("avg_rating", ascending=False)
        .to_dict(orient="records")
    )
    return {"top_titles": df.head(10).to_dict(orient="records"), "genre_stats": genre_stats}


def trending_from_csv(title_hint=None):
    df = _load("movies.csv")
    if title_hint:
        mask = df["title"].str.lower().str.contains(title_hint.lower(), na=False)
        result = df[mask].sort_values("trending_score", ascending=False)
        if not result.empty:
            return result.to_dict(orient="records")
    return df.sort_values("trending_score", ascending=False).head(5).to_dict(orient="records")


def compare_titles_from_csv(title_a, title_b):
    df = _load("movies.csv")
    mask = (
        df["title"].str.lower().str.contains(title_a.lower(), na=False) |
        df["title"].str.lower().str.contains(title_b.lower(), na=False)
    )
    return df[mask].to_dict(orient="records")


def city_engagement_from_csv(month=None):
    df = _load("regional_performance.csv")
    if month:
        df = df[df["month"].str.lower() == month.lower()]
    result = (
        df.groupby(["city", "country"])
        .agg(total_views=("total_views", "sum"), avg_engagement=("engagement_score", "mean"))
        .round(1)
        .reset_index()
        .sort_values("avg_engagement", ascending=False)
        .head(10)
    )
    return result.to_dict(orient="records")


def comedy_from_csv():
    movies = _load("movies.csv")
    reviews = _load("reviews.csv")
    spend = _load("marketing_spend.csv")

    comedy_movies = movies[movies["genre"].str.lower() == "comedy"]
    comedy_ids = comedy_movies["movie_id"].tolist()

    comedy_reviews = reviews[reviews["movie_id"].isin(comedy_ids)]
    sentiment_counts = comedy_reviews["sentiment"].value_counts().to_dict()

    comedy_titles = comedy_movies["title"].str.lower().tolist()
    comedy_spend = spend[spend["title"].str.lower().isin(comedy_titles)]
    spend_summary = {
        "total_spend": int(comedy_spend["spend_usd"].sum()),
        "total_conversions": int(comedy_spend["conversions"].sum()),
    }

    return {
        "movies": comedy_movies[["title", "rating", "total_views", "trending_score"]].to_dict(orient="records"),
        "sentiment": sentiment_counts,
        "marketing": spend_summary,
    }


def marketing_roi_from_csv():
    df = _load("marketing_spend.csv")
    df["conversions_per_1k_spend"] = (df["conversions"] / df["spend_usd"] * 1000).round(2)
    return df.sort_values("conversions_per_1k_spend", ascending=False).head(15).to_dict(orient="records")


def genre_performance_from_csv():
    df = _load("movies.csv")
    result = (
        df.groupby("genre")
        .agg(title_count=("title", "count"), avg_rating=("rating", "mean"),
             total_views=("total_views", "sum"), avg_trending=("trending_score", "mean"))
        .round(2)
        .reset_index()
        .sort_values("avg_rating", ascending=False)
    )
    return result.to_dict(orient="records")
