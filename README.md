# AI Insights Assistant

AI Insights Assistant is a small full-stack app that answers natural language questions using three data sources:

- PDF reports for unstructured insights
- CSV data for analytics
- SQLite for structured movie records

The backend is built with FastAPI, and the frontend is a lightweight HTML/JavaScript interface.

## Features

- Multi-source query answering across PDF, CSV, and SQL
- Automatic routing based on query intent
- Source-aware responses
- Automatic database initialization on backend startup
- Genre distribution chart generated through an API endpoint
- Simple local frontend for testing queries

## How It Works

1. The frontend sends a query to `POST /chat`.
2. The backend routes the query:
   - CSV analytics for ranking/performance questions
   - SQL for movie/database questions
   - PDF retrieval as the generic default for report-style questions
3. The selected tool returns data.
4. The backend formats the answer and includes a source label.

## Project Structure

```text
ai-assistant/
├── backend/
│   ├── main.py
│   ├── db.py
│   ├── init_db.py
│   ├── data.db
│   ├── services/
│   │   ├── ai_service.py
│   │   └── hf_service.py
│   └── tools/
│       ├── __init__.py
│       ├── csv_tools.py
│       ├── pdf_tools.py
│       └── sql_tools.py
├── data/
│   ├── movies.csv
│   └── pdfs/
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

Then edit `.env` and add your real value:

```env
HF_API_KEY=your_huggingface_api_key_here
```

4. Start the backend:

```bash
cd backend
uvicorn main:app --reload
```

5. Start the frontend in another terminal:

```bash
cd frontend
python -m http.server 5500
```

Open `http://localhost:5500`.

## Database Initialization

The SQLite database is initialized automatically when the FastAPI app starts.

On startup, `backend/main.py` calls `load_data()` from `backend/db.py`, which loads `data/movies.csv` into the `movies` table.

Current behavior:

- The active database file is `backend/data.db`
- The movies table is recreated from the CSV on startup

If you want to manually initialize it, you can still run:

```bash
python backend/init_db.py
```

## API Endpoints

- `GET /` - simple backend status message
- `GET /health` - health check and env verification
- `GET /movies` - returns all movie rows from SQLite
- `POST /chat` - main AI query endpoint
- `GET /chart` - returns the genre distribution chart as a PNG

Example request:

```json
{
  "query": "Which movies performed best?"
}
```

## Example Queries

### PDF / report queries

- `What is summary?`
- `What are audience behavior insights?`
- `What is trending in the report?`

### CSV / analytics queries

- `Which movies performed best?`
- `What is top movie performance?`

### SQL / database queries

- `Show all movies`
- `How many movies are there?`
- `Show movies in the database`

## Visualization

The app provides a chart endpoint at `GET /chart` that generates a genre distribution bar chart.

For macOS/server safety, Matplotlib uses the non-GUI `Agg` backend so chart generation does not crash the FastAPI worker thread.

## Environment Variables

The project includes `.env.example` so secrets do not need to be committed.

Currently used variables:

- `HF_API_KEY` - used by `backend/services/hf_service.py`

## Git Notes

The project includes a `.gitignore` that excludes:

- `.env`
- local virtual environments
- Python cache files
- local database files
- generated chart/image artifacts

## Known Limitations

- PDF retrieval is lexical/token based, not embedding-based semantic search
- PDF extraction quality depends on how text is structured inside the source PDF
- Query routing is practical but still simple
- Database initialization currently reloads the CSV on each backend startup

## Future Improvements

- Add semantic PDF retrieval with embeddings
- Return file/page metadata in chat responses
- Improve intent routing with a more formal classifier
- Add tests for routing and PDF section ranking
- Avoid reloading the database if it already exists

## Tech Stack

- FastAPI
- SQLite
- SQLAlchemy
- Pandas
- Matplotlib
- PyPDF
- Python dotenv
- HTML / CSS / JavaScript
