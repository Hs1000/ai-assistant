import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, "data", "movies.csv")


def analyze_movies():
    try:
        if not os.path.exists(CSV_PATH):
            return {"error": "CSV file not found"}

        df = pd.read_csv(CSV_PATH)

        # 🔥 Validate required columns
        required_cols = ["rating", "genre"]
        for col in required_cols:
            if col not in df.columns:
                return {"error": f"Missing column: {col}"}

        # 🔥 Handle bad data
        df = df.dropna(subset=["rating", "genre"])

        # Top movies
        top_movies = df.sort_values(by="rating", ascending=False).head(5)

        genre_distribution = df["genre"].value_counts().to_dict()
        avg_rating = float(round(df["rating"].mean(), 2))

        return {
            "top_movies": top_movies.to_dict(orient="records"),
            "genre_distribution": genre_distribution,
            "average_rating": avg_rating
        }

    except Exception as e:
        return {"error": str(e)}