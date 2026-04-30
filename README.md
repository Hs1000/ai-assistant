# AI Insights Assistant

AI Insights Assistant is a full-stack app that answers natural language questions about streaming content performance using three data sources:

- SQL (SQLite) for structured queries across movies, viewers, watch activity, reviews, marketing spend, and regional performance
- PDF reports for unstructured executive and campaign insights
- CSV files read directly with Pandas for analytics (alternative to SQL, user-selectable)

The backend is built with FastAPI and the frontend is a lightweight HTML/React interface.

## Features

- Multi-source query answering across SQL, PDF, and CSV
- Intent-based routing for six supported question types
- User-selectable source: Auto Route, CSV Direct, SQL, or PDF via the UI dropdown
- Source-aware responses with data payloads
- All six database tables auto-loaded from CSV on backend startup
- "Best movie" query returns the single highest-rated title; "best in 2025" returns a ranked list
- Genre distribution chart via API endpoint
- Template dropdown in the UI for all six required questions

## Supported Questions

| Question | Data Source |
|---|---|
| Which titles performed best in 2025? | SQL |
| Why is Stellar Run trending recently? | SQL + PDF |
| Compare Dark Orbit vs Last Kingdom | SQL |
| Which city had the strongest engagement last month? | SQL |
| What explains weak comedy performance? | SQL + PDF |
| What recommendations would you give for leadership? | PDF + SQL |

## How It Works

1. The frontend sends a query to `POST /chat`. The source preference dropdown prepends `[Use CSV]`, `[Use SQL]`, or `[Use PDF]` to the query when not set to Auto Route. Selecting a template overrides whatever is typed in the input field.
2. The backend detects the source override first:
   - `[Use CSV]` → reads CSV files directly with Pandas (`csv_tools.py`)
   - `[Use PDF]` → searches PDF sections only
   - Auto Route / `[Use SQL]` → queries SQLite + PDF where relevant
3. Within each source path, intent is detected by keyword:
   - Comedy keywords → comedy analysis
   - Compare / vs → side-by-side title comparison
   - "Best movie" (no year) → single highest-rated title
   - Best / top + year → ranked list filtered by year
   - Trending / trend → trending score lookup
   - City / engagement / region → regional performance
   - Recommend / leadership / strategy → executive recommendations (PDF + SQL)
   - Anything else → PDF section search, then fallback
4. The backend formats the answer and includes a source label (`SQL Database`, `CSV Direct`, `PDF Documents`, `SQL + PDF`, etc.).

## Project Structure

```text
ai-assistant/
├── backend/
│   ├── main.py
│   ├── db.py
│   ├── init_db.py
│   ├── services/
│   │   ├── ai_service.py
│   │   └── hf_service.py
│   └── tools/
│       ├── csv_tools.py
│       ├── pdf_tools.py
│       └── sql_tools.py
├── data/
│   ├── movies.csv
│   ├── viewers.csv
│   ├── watch_activity.csv
│   ├── reviews.csv
│   ├── marketing_spend.csv
│   ├── regional_performance.csv
│   ├── generate_movies.py
│   ├── generate_pdfs.py
│   └── pdfs/
│       ├── quarterly_executive_report.pdf
│       ├── campaign_performance_summary.pdf
│       ├── content_roadmap.pdf
│       ├── policy_guidelines.pdf
│       └── audience_behavior_report.pdf
├── frontend/
│   └── index.html
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv backend/venv
source backend/venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your environment file:

```bash
cp .env.example .env
```

## Running the Backend

Run from the project root (not from inside `backend/`):

```bash
uvicorn backend.main:app --reload
```

The backend starts at `http://127.0.0.1:8000` and automatically loads all six CSV tables into SQLite on startup.

## Running the Frontend

Open `frontend/index.html` directly in your browser, or serve it:

```bash
cd frontend
python -m http.server 5500
```

Then open `http://localhost:5500`.

## Database Initialization

On startup, `db.py` loads all six CSV files into SQLite tables:

| Table | Source CSV |
|---|---|
| `movies` | `data/movies.csv` |
| `viewers` | `data/viewers.csv` |
| `watch_activity` | `data/watch_activity.csv` |
| `reviews` | `data/reviews.csv` |
| `marketing_spend` | `data/marketing_spend.csv` |
| `regional_performance` | `data/regional_performance.csv` |

The database file (`backend/data.db`) is excluded from git. Each restart recreates all tables from the CSVs.

## Regenerating Data

To regenerate the PDF reports:

```bash
python data/generate_pdfs.py
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Backend status |
| `GET` | `/health` | Health check |
| `GET` | `/movies` | All movie rows from SQLite |
| `POST` | `/chat` | Main AI query endpoint |
| `GET` | `/chart` | Genre distribution chart (PNG) |

Example request:

```json
{
  "query": "Which titles performed best in 2025?"
}
```

## Tech Stack

- FastAPI
- SQLite + SQLAlchemy
- Pandas
- Matplotlib
- PyPDF
- ReportLab (PDF generation)
- Python dotenv
- HTML / CSS / React (via CDN)

## Known Limitations

- PDF retrieval is lexical/token-based, not embedding-based semantic search
- Intent routing uses keyword matching, not an NLP classifier
- Database is fully reloaded from CSV on every backend restart
