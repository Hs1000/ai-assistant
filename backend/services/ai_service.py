import re
from tools.sql_tools import (
    get_all_movies,
    get_top_titles_2025,
    get_title_comparison,
    get_trending_title,
    get_city_engagement,
    get_genre_performance,
    get_comedy_analysis,
    get_marketing_roi,
)
from tools.pdf_tools import search_pdfs


def _fmt_movie(m):
    return (
        f"• {m['title']} ({m.get('genre','?')}, {m.get('release_year','?')}) "
        f"— Rating: {m.get('rating','?')}, Views: {int(m.get('total_views',0)):,}"
    )


def _detect(query_lower, keywords):
    return any(k in query_lower for k in keywords)


def run_agent(query: str):
    q = query.lower().strip()

    try:
        # ── Q5: Comedy — checked first to avoid "perform" false match ────
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
                "Comedy genre performance analysis:\n\n"
                "Titles:\n" + "\n".join(movie_lines)
                + "\n\nReview sentiment:\n" + ("\n".join(sent_lines) if sent_lines else "No reviews found")
                + pdf_context
            )
            return {"answer": answer, "data": db_data, "source": "SQL + PDF"}

        # ── Q3: Compare — checked before trending to avoid title-name clash
        compare_match = re.search(r"compar\w*\s+([\w\s]+?)\s+(?:vs?\.?|versus|and)\s+([\w\s]+)", q)
        if compare_match or _detect(q, ["compare", "versus", " vs "]):
            if compare_match:
                a = compare_match.group(1).strip()
                b = compare_match.group(2).strip()
            else:
                known = ["stellar run", "dark orbit", "last kingdom", "hollow earth",
                         "fire & frost", "vortex rising", "neon mirage", "iron phoenix",
                         "shadow protocol", "crimson tide"]
                found = [t for t in known if t in q]
                a, b = (found[0], found[1]) if len(found) >= 2 else ("dark orbit", "last kingdom")
            data = get_title_comparison(a, b)
            if len(data) < 2:
                return {"answer": f"Could not find both '{a}' and '{b}' in the database.", "source": "SQL Database"}
            fields = ["genre", "release_year", "rating", "total_views", "box_office_m", "budget_m", "trending_score"]
            labels = {"total_views": "Views", "box_office_m": "Box Office ($M)",
                      "budget_m": "Budget ($M)", "rating": "Rating", "trending_score": "Trending Score"}
            lines = []
            for field in fields:
                label = labels.get(field, field.replace("_", " ").title())
                vals = [f"{int(m.get(field,0)):,}" if field == "total_views" else str(m.get(field, "?")) for m in data[:2]]
                lines.append(f"  {label}: {data[0]['title']} = {vals[0]}  |  {data[1]['title']} = {vals[1]}")
            return {"answer": f"Comparison: {data[0]['title']} vs {data[1]['title']}\n\n" + "\n".join(lines),
                    "data": data, "source": "SQL Database"}

        # ── Q1: Best performing titles ────────────────────────────────────
        if _detect(q, ["best", "top", "perform", "2025", "highest rated", "highest-rated"]):
            data = get_top_titles_2025()
            if not data:
                return {"answer": "No 2025 titles found.", "source": "SQL Database"}
            genre_data = get_genre_performance()
            genre_lines = [
                f"• {g['genre']}: avg rating {round(g['avg_rating'],2)}, {int(g['total_views']):,} total views"
                for g in genre_data
            ]
            answer = ("Top performing titles in 2025:\n\n"
                      + "\n".join(_fmt_movie(m) for m in data)
                      + "\n\nGenre breakdown:\n" + "\n".join(genre_lines))
            return {"answer": answer, "data": data, "source": "SQL Database"}

        # ── Q2: Trending title ────────────────────────────────────────────
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
                answer = (
                    f"{m['title']} is trending with a score of {m.get('trending_score','?')}/100.\n\n"
                    f"Rating: {m.get('rating','?')}/10 · {int(m.get('total_views',0)):,} views · "
                    f"Released {m.get('release_date','?')}" + pdf_context
                )
            else:
                answer = f"No trending data found for '{title_hint}'." + pdf_context
            return {"answer": answer, "data": db_data, "source": "SQL + PDF"}

        # ── Q4: City engagement ───────────────────────────────────────────
        if _detect(q, ["city", "cities", "region", "regional", "location", "engagement", "geographic"]):
            month = next(
                (m for m in ["january","february","march","april","may","june",
                              "july","august","september","october","november","december"] if m in q),
                None
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

        # ── Q6: Leadership recommendations ────────────────────────────────
        if _detect(q, ["recommend", "leadership", "strategy", "strategic", "advice", "suggest", "what should"]):
            pdf_data = search_pdfs("leadership recommendations strategy")
            roi_data = get_marketing_roi()
            genre_data = get_genre_performance()
            pdf_context = pdf_data[0]["content"][:800] if pdf_data and "content" in pdf_data[0] else ""
            genre_lines = [
                f"• {g['genre']}: avg rating {round(g['avg_rating'],2)}, {int(g['total_views']):,} views"
                for g in genre_data
            ]
            top_roi = roi_data[:3]
            roi_lines = [
                f"• {r['title']} via {r['channel']}: {r.get('conversions_per_1k_spend','?')} conversions per $1K"
                for r in top_roi
            ]
            answer = (
                "Leadership Recommendations:\n\n"
                + (pdf_context + "\n\n" if pdf_context else "")
                + "Genre performance summary:\n" + "\n".join(genre_lines)
                + "\n\nTop marketing ROI channels:\n" + "\n".join(roi_lines)
            )
            return {"answer": answer, "data": {"genre": genre_data, "roi": top_roi}, "source": "PDF + SQL"}

        # ── Generic SQL fallback ──────────────────────────────────────────
        if _detect(q, ["movie", "movies", "title", "titles", "database", "sql", "film"]):
            data = get_all_movies()
            return {
                "answer": f"There are {len(data)} titles in the database. Top 5 by rating:\n\n"
                          + "\n".join(_fmt_movie(m) for m in data[:5]),
                "data": data[:5],
                "source": "SQL Database",
            }

        # ── PDF default ───────────────────────────────────────────────────
        pdf_data = search_pdfs(query)
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

    except Exception as e:
        return {"answer": f"Internal error: {str(e)}", "source": "Error"}
