import pandas as pd
import random

def generate_movies():
    movies = pd.DataFrame({
        "movie_id": range(1, 11),
        "title": [f"Movie {i}" for i in range(1, 11)],
        "genre": random.choices(["Action", "Comedy", "Drama"], k=10),
        "release_year": random.choices([2024, 2025], k=10),
        "rating": [round(random.uniform(5, 9), 1) for _ in range(10)]
    })

    movies.to_csv("data/movies.csv", index=False)
    print("movies.csv generated!")

if __name__ == "__main__":
    generate_movies()