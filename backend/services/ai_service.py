import re
from tools.sql_tools import (
    get_all_movies,
    get_best_movie,
    get_top_titles,
    get_title_comparison,
    get_trending_title,
    get_city_engagement,
    get_genre_performance,
    get_comedy_analysis,
    get_marketing_roi,
)
from tools.csv_tools import (
    top_titles_from_csv,
    trending_from_csv,
    compare_titles_from_csv,
    city_engagement_from_csv,
    comedy_from_csv,
    marketing_roi_from_csv,
    genre_performance_from_csv,
    analyze_movies,
)
from tools.pdf_tools import search_pdfs


def _fmt_movie(m):
    return (
        f"• {m['title']} ({m.get('genre','?')}, {m.get('release_year','?')}) "
        f"— Rating: {m.get('rating','?')}, Views: {int(m.get('total_views',0)):,}"
    )


def _detect(query_lower, keywords):
    return any(k in query_lower for k in keywords)


def _known_titles(q):
    known = ["stellar run", "dark orbit", "last kingdom", "hollow earth",
             "fire & frost", "vortex rising", "neon mirage", "iron phoenix",
             "shadow protocol", "crimson tide"]
    return [t for t in known if t in q]


# ── CSV direct path ───────────────────────────────────────────────────────────

def _answer_from_csv(q):
    # Q5: Comedy
    if _detect(q, ["comedy", "comedies", "funny", "laugh", "humor", "humour"]):
        data = comedy_from_csv()
        movies = data.get("movies", [])
        sentiment = data.get("sentiment", {})
        spend = data.get("marketing", {})
        movie_lines = [f"• {m['title']} — Rating: {m['rating']}, Views: {int(m.get('total_views',0)):,}" for m in movies]
        sent_lines = [f"• {k}: {v} reviews" for k, v in sentiment.items()]
        answer = (
            "Comedy performance (direct from CSV):\n\nTitles:\n" + "\n".join(movie_lines)
            + "\n\nSentiment:\n" + ("\n".join(sent_lines) if sent_lines else "No reviews")
            + f"\n\nMarketing: ${spend.get('total_spend',0):,} spend, {spend.get('total_conversions',0):,} conversions"
        )
        return {"answer": answer, "data": data, "source": "CSV Direct"}

    # Q3: Compare
    compare_match = re.search(r"compar\w*\s+([\w\s]+?)\s+(?:vs?\.?|versus|and)\s+([\w\s]+)", q)
    if compare_match or _detect(q, ["compare", "versus", " vs "]):
        if compare_match:
            a, b = compare_match.group(1).strip(), compare_match.group(2).strip()
        else:
            found = _known_titles(q)
            a, b = (found[0], found[1]) if len(found) >= 2 else ("dark orbit", "last kingdom")
        data = compare_titles_from_csv(a, b)
        if len(data) < 2:
            return {"answer": f"Could not find both '{a}' and '{b}' in CSV.", "source": "CSV Direct"}
        fields = ["genre", "release_year", "rating", "total_views", "box_office_m", "budget_m", "trending_score"]
        labels = {"total_views": "Views", "box_office_m": "Box Office ($M)", "budget_m": "Budget ($M)",
                  "rating": "Rating", "trending_score": "Trending Score"}
        lines = []
        for field in fields:
            label = labels.get(field, field.replace("_", " ").title())
            vals = [f"{int(m.get(field,0)):,}" if field == "total_views" else str(m.get(field,"?")) for m in data[:2]]
            lines.append(f"  {label}: {data[0]['title']} = {vals[0]}  |  {data[1]['title']} = {vals[1]}")
        return {"answer": f"Comparison (from CSV): {data[0]['title']} vs {data[1]['title']}\n\n" + "\n".join(lines),
                "data": data, "source": "CSV Direct"}

    # Q1: Best / top
    if _detect(q, ["best", "top", "perform", "2025", "highest rated"]):
        year_match = re.search(r"\b(20\d{2})\b", q)
        year = int(year_match.group(1)) if year_match else None

        if not year and _detect(q, ["best movie", "best film", "highest rated", "most rating", "highest rating"]):
            data = top_titles_from_csv(year=None)
            best = data["top_titles"][0] if data["top_titles"] else None
            if not best:
                return {"answer": "No movies found in CSV.", "source": "CSV Direct"}
            answer = (
                f"The best movie by rating (from CSV):\n\n"
                f"• {best['title']} ({best.get('genre','?')}, {best.get('release_year','?')})\n"
                f"  Rating: {best['rating']}/10\n"
                f"  Views: {int(best.get('total_views',0)):,}\n"
                f"  Trending Score: {best.get('trending_score','?')}/100"
            )
            return {"answer": answer, "data": best, "source": "CSV Direct"}

        data = top_titles_from_csv(year)
        genre_lines = [
            f"• {g['genre']}: avg rating {g['avg_rating']}, {int(g['total_views']):,} views"
            for g in data["genre_stats"]
        ]
        label = f"in {year}" if year else "overall"
        answer = (
            f"Top titles {label} (direct from CSV):\n\n"
            + "\n".join(_fmt_movie(m) for m in data["top_titles"])
            + "\n\nGenre breakdown:\n" + "\n".join(genre_lines)
        )
        return {"answer": answer, "data": data, "source": "CSV Direct"}

    # Q2: Trending
    if _detect(q, ["trending", "trend", "popular", "viral", "buzz"]):
        tm = re.search(r"(stellar run|dark orbit|last kingdom|hollow earth|fire.{0,6}frost|"
                       r"vortex rising|iron phoenix|neon mirage|shadow protocol|crimson tide)", q)
        hint = tm.group(1) if tm else None
        data = trending_from_csv(hint)
        if data:
            m = data[0]
            answer = (f"{m['title']} trending score: {m.get('trending_score','?')}/100 "
                      f"(from CSV)\nRating: {m.get('rating','?')} · Views: {int(m.get('total_views',0)):,}")
        else:
            answer = "No trending data found in CSV."
        return {"answer": answer, "data": data, "source": "CSV Direct"}

    # Q4: City engagement
    if _detect(q, ["city", "cities", "region", "regional", "location", "engagement", "geographic"]):
        month = next(
            (m for m in ["january","february","march","april","may","june",
                          "july","august","september","october","november","december"] if m in q), None
        )
        data = city_engagement_from_csv(month)
        label = f"in {month.title()}" if month else "overall"
        lines = [
            f"• {r['city']}, {r['country']} — Engagement: {r['avg_engagement']}, Views: {int(r['total_views']):,}"
            for r in data
        ]
        return {"answer": f"Top cities by engagement {label} (from CSV):\n\n" + "\n".join(lines),
                "data": data, "source": "CSV Direct"}

    # Q6: Recommendations / marketing ROI
    if _detect(q, ["recommend", "leadership", "strategy", "strategic", "advice", "suggest", "marketing", "roi"]):
        roi = marketing_roi_from_csv()
        genre = genre_performance_from_csv()
        genre_lines = [f"• {g['genre']}: avg rating {g['avg_rating']}, {int(g['total_views']):,} views" for g in genre]
        roi_lines = [f"• {r['title']} via {r['channel']}: {r['conversions_per_1k_spend']} conv/$1K" for r in roi[:5]]
        answer = (
            "Analytics from CSV:\n\nGenre performance:\n" + "\n".join(genre_lines)
            + "\n\nTop marketing ROI:\n" + "\n".join(roi_lines)
        )
        return {"answer": answer, "data": {"genre": genre, "roi": roi[:5]}, "source": "CSV Direct"}

    # Generic CSV fallback
    data = analyze_movies()
    return {
        "answer": f"CSV analytics — avg rating: {data['average_rating']}, "
                  f"top title: {data['top_movies'][0]['title'] if data['top_movies'] else 'N/A'}",
        "data": data,
        "source": "CSV Direct",
    }


# ── SQL + PDF path (default) ──────────────────────────────────────────────────

def _answer_from_sql_pdf(q, raw_query):
    # Q5: Comedy
    if _detect(q, ["comedy", "comedies", "funny", "laugh", "humor", "humour"]):
        db_data = get_comedy_analysis()
        pdf_data = search_pdfs("comedy performance weak explanation")
        pdf_context = ""
        if pdf_data and isinstance(pdf_data, list) and "content" in pdf_data[0]:
            pdf_context = "\n\nFrom audience report:\n" + pdf_data[0]["content"][:700]
        movies = db_data.get("movies", [])
        sentiment = db_data.get("sentiment", [])
        movie_lines = [f"• {m['title']} — Rating: {m['rating']}, Views: {int(m.get('total_views',0)):,}" for m in movies]
        sent_lines = [f"• {s['sentiment']}: {s['count']} reviews" for s in sentiment]
        answer = (
            "Comedy genre performance analysis:\n\nTitles:\n" + "\n".join(movie_lines)
            + "\n\nReview sentiment:\n" + ("\n".join(sent_lines) if sent_lines else "No reviews found")
            + pdf_context
        )
        return {"answer": answer, "data": db_data, "source": "SQL + PDF"}

    # Q3: Compare
    compare_match = re.search(r"compar\w*\s+([\w\s]+?)\s+(?:vs?\.?|versus|and)\s+([\w\s]+)", q)
    if compare_match or _detect(q, ["compare", "versus", " vs "]):
        if compare_match:
            a, b = compare_match.group(1).strip(), compare_match.group(2).strip()
        else:
            found = _known_titles(q)
            a, b = (found[0], found[1]) if len(found) >= 2 else ("dark orbit", "last kingdom")
        data = get_title_comparison(a, b)
        if len(data) < 2:
            return {"answer": f"Could not find both '{a}' and '{b}' in the database.", "source": "SQL Database"}
        fields = ["genre", "release_year", "rating", "total_views", "box_office_m", "budget_m", "trending_score"]
        labels = {"total_views": "Views", "box_office_m": "Box Office ($M)", "budget_m": "Budget ($M)",
                  "rating": "Rating", "trending_score": "Trending Score"}
        lines = []
        for field in fields:
            label = labels.get(field, field.replace("_", " ").title())
            vals = [f"{int(m.get(field,0)):,}" if field == "total_views" else str(m.get(field,"?")) for m in data[:2]]
            lines.append(f"  {label}: {data[0]['title']} = {vals[0]}  |  {data[1]['title']} = {vals[1]}")
        return {"answer": f"Comparison: {data[0]['title']} vs {data[1]['title']}\n\n" + "\n".join(lines),
                "data": data, "source": "SQL Database"}

    # Q1: Best / top
    if _detect(q, ["best", "top", "perform", "2025", "highest rated", "highest-rated", "highest rating", "most rating"]):
        year_match = re.search(r"\b(20\d{2})\b", q)
        year = year_match.group(1) if year_match else None

        # "best movie" with no year → return the single highest-rated movie
        if not year and _detect(q, ["best movie", "best film", "highest rated", "most rating", "highest rating"]):
            best = get_best_movie()
            if not best:
                return {"answer": "No movies found.", "source": "SQL Database"}
            answer = (
                f"The best movie by rating is:\n\n"
                f"• {best['title']} ({best.get('genre','?')}, {best.get('release_year','?')})\n"
                f"  Rating: {best['rating']}/10\n"
                f"  Views: {int(best.get('total_views',0)):,}\n"
                f"  Trending Score: {best.get('trending_score','?')}/100"
            )
            return {"answer": answer, "data": best, "source": "SQL Database"}

        # "top titles" / "best in 2025" → ranked list
        data = get_top_titles(year)
        if not data:
            return {"answer": f"No titles found{' for ' + year if year else ''}.", "source": "SQL Database"}
        genre_data = get_genre_performance()
        genre_lines = [
            f"• {g['genre']}: avg rating {round(g['avg_rating'],2)}, {int(g['total_views']):,} total views"
            for g in genre_data
        ]
        label = f"in {year}" if year else "overall"
        answer = (f"Top performing titles {label}:\n\n"
                  + "\n".join(_fmt_movie(m) for m in data)
                  + "\n\nGenre breakdown:\n" + "\n".join(genre_lines))
        return {"answer": answer, "data": data, "source": "SQL Database"}

    # Q2: Trending
    trending_match = re.search(
        r"(stellar run|dark orbit|last kingdom|hollow earth|fire.{0,6}frost|"
        r"vortex rising|iron phoenix|neon mirage|shadow protocol|crimson tide)", q)
    if _detect(q, ["trending", "trend", "popular", "viral", "buzz"]):
        title_hint = trending_match.group(1) if trending_match else "stellar run"
        db_data = get_trending_title(title_hint)
        pdf_data = search_pdfs(f"trending {title_hint}")
        pdf_context = ""
        if pdf_data and isinstance(pdf_data, list) and "content" in pdf_data[0]:
            pdf_context = "\n\nFrom content reports:\n" + pdf_data[0]["content"][:600]
        if db_data:
            m = db_data[0]
            answer = (f"{m['title']} is trending with a score of {m.get('trending_score','?')}/100.\n\n"
                      f"Rating: {m.get('rating','?')}/10 · {int(m.get('total_views',0)):,} views · "
                      f"Released {m.get('release_date','?')}" + pdf_context)
        else:
            answer = f"No trending data found for '{title_hint}'." + pdf_context
        return {"answer": answer, "data": db_data, "source": "SQL + PDF"}

    # Q4: City engagement
    if _detect(q, ["city", "cities", "region", "regional", "location", "engagement", "geographic"]):
        month = next(
            (m for m in ["january","february","march","april","may","june",
                          "july","august","september","october","november","december"] if m in q), None
        )
        data = get_city_engagement(month)
        label = f"in {month.title()}" if month else "overall"
        lines = [
            f"• {r['city']}, {r['country']} — "
            f"Engagement: {round(r.get('avg_engagement', r.get('engagement_score', 0)), 1)}, "
            f"Views: {int(r.get('total_views', 0)):,}"
            for r in data
        ]
        return {"answer": f"Top cities by engagement {label}:\n\n" + "\n".join(lines),
                "data": data, "source": "SQL Database"}

    # Q6: Leadership recommendations
    if _detect(q, ["recommend", "leadership", "strategy", "strategic", "advice", "suggest", "what should"]):
        pdf_data = search_pdfs("leadership recommendations strategy")
        roi_data = get_marketing_roi()
        genre_data = get_genre_performance()
        pdf_context = pdf_data[0]["content"][:800] if pdf_data and "content" in pdf_data[0] else ""
        genre_lines = [f"• {g['genre']}: avg rating {round(g['avg_rating'],2)}, {int(g['total_views']):,} views" for g in genre_data]
        top_roi = roi_data[:3]
        roi_lines = [f"• {r['title']} via {r['channel']}: {r.get('conversions_per_1k_spend','?')} conversions per $1K" for r in top_roi]
        answer = (
            "Leadership Recommendations:\n\n"
            + (pdf_context + "\n\n" if pdf_context else "")
            + "Genre performance summary:\n" + "\n".join(genre_lines)
            + "\n\nTop marketing ROI channels:\n" + "\n".join(roi_lines)
        )
        return {"answer": answer, "data": {"genre": genre_data, "roi": top_roi}, "source": "PDF + SQL"}

    # Generic SQL
    if _detect(q, ["movie", "movies", "title", "titles", "database", "sql", "film"]):
        data = get_all_movies()
        return {
            "answer": f"There are {len(data)} titles in the database. Top 5 by rating:\n\n"
                      + "\n".join(_fmt_movie(m) for m in data[:5]),
            "data": data[:5],
            "source": "SQL Database",
        }

    # PDF default
    pdf_data = search_pdfs(raw_query)
    if pdf_data and isinstance(pdf_data, list):
        first = pdf_data[0]
        if "content" in first:
            content = first["content"].strip()
            return {"answer": f"From the reports:\n\n{content[:900]}", "source": "PDF Documents"} if content \
                else {"answer": "Section found but no readable content.", "source": "PDF Documents"}
        if "error" in first:
            return {"answer": f"PDF Error: {first['error']}", "source": "PDF Documents"}
        if "message" in first:
            return {"answer": first["message"], "source": "PDF Documents"}

    return {
        "answer": "I can answer: best titles in 2025, trending titles, title comparisons, city engagement, comedy performance, leadership recommendations.",
        "source": "Fallback",
    }


# ── Entry point ───────────────────────────────────────────────────────────────

def run_agent(query: str):
    try:
        # Detect source override from frontend dropdown ([Use CSV], [Use SQL], [Use PDF])
        csv_forced = "[use csv]" in query.lower()
        pdf_forced = "[use pdf]" in query.lower()

        # Strip the prefix before routing
        clean = re.sub(r"\[use (csv|sql|pdf)\]\s*", "", query, flags=re.IGNORECASE).strip()
        q = clean.lower()

        if csv_forced:
            return _answer_from_csv(q)

        if pdf_forced:
            pdf_data = search_pdfs(clean)
            if pdf_data and isinstance(pdf_data, list) and "content" in pdf_data[0]:
                return {"answer": f"From the reports:\n\n{pdf_data[0]['content'][:900]}", "source": "PDF Documents"}
            return {"answer": "No relevant PDF content found.", "source": "PDF Documents"}

        # Default: SQL + PDF
        return _answer_from_sql_pdf(q, clean)

    except Exception as e:
        return {"answer": f"Internal error: {str(e)}", "source": "Error"}
