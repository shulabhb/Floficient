# Floficient

A real-time traffic congestion and incident dashboard for San Francisco, powered by HERE API, OpenStreetMap, FastAPI, and Next.js.

---

## Features
- **Live Traffic Flow & Incidents**: Real-time congestion and incident data for San Francisco
- **Congestion Line Extension**: Congestion lines are extended along real road geometry using OSM data
- **Accurate Road Names**: All incidents and congestion segments are enriched with OSM-based road names
- **Modern UI**: Interactive dashboard built with Next.js, MapLibre, and React
- **No "Other" Incidents**: Uninformative incidents are filtered out
- **Scheduler & ETL**: Automated ingestion and enrichment of HERE API data

---

## Project Structure

```
Floficient/
  backend/
    app/
      api/                # FastAPI endpoints
      db/                 # SQLAlchemy models, OSM enrichment, road lookup
      scheduler/          # ETL for traffic flow and incidents
      utils/              # API client, geo helpers, logging
      main.py             # FastAPI app entrypoint
    requirements.txt      # Python dependencies
  frontend/
    src/                  # Next.js app, components, types
    package.json          # Node dependencies
  README.md               # This file
```

---

## Backend (FastAPI, ETL, OSM Enrichment)

### Setup
1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. **Configure environment**
   - Set `HERE_API_KEY` and `DATABASE_URL` in `.env` (SQLite or PostgreSQL supported)
3. **Initialize the database**
   ```python
   from app.db.models import Base
   from app.db.session import engine
   Base.metadata.create_all(bind=engine)
   ```
4. **Download OSM data**
   - Place your San Francisco OSM extract as `app/db/sf_roads.json` (see scripts for extraction)
5. **Run ETL and API**
   ```bash
   # Run ETL (fetches and enriches data)
   PYTHONPATH=backend python3 -m app.scheduler.traffic_flow
   PYTHONPATH=backend python3 -m app.scheduler.traffic_incidents
   # Run API server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Key Features
- **ETL**: Ingests HERE API data, enriches with OSM road names, extends congestion lines
- **Road Name Lookup**: Uses OSM data for accurate road names and geometry
- **Batch Enrichment**: Scripts to backfill missing road names and clean up data
- **API Endpoints**: `/api/v1/traffic/flow`, `/api/v1/traffic/incidents`, `/api/v1/traffic/roads`, `/api/v1/health`

### Dependencies
See `backend/requirements.txt` for full list. Key packages:
- fastapi, uvicorn, sqlalchemy, requests, apscheduler, shapely, rtree, osmium, python-dotenv

---

## Frontend (Next.js, MapLibre, React)

### Setup
1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   # or yarn install
   ```
2. **Run the development server**
   ```bash
   npm run dev
   # or yarn dev
   ```
3. **Open** [http://localhost:3000](http://localhost:3000)

### Key Features
- **Live Map**: Interactive map with congestion lines and incident markers
- **Incident Details**: Click on incidents to see type, description, and OSM-based road name
- **Congestion Details**: Click on congestion lines to see road name and congestion level (backend support ready)
- **Legend & Filtering**: Clean, modern UI with legend and filtering

### Dependencies
See `frontend/package.json` for full list. Key packages:
- next, react, maplibre-gl, react-map-gl, leaflet, react-leaflet, recharts, tailwindcss, @tanstack/react-query

---

## Data Enrichment & OSM Integration
- **OSM Road Data**: Used to enrich all incidents and congestion segments with accurate road names
- **Congestion Extension**: Congestion lines are extended along the actual road geometry for better visualization
- **Batch Scripts**: Utilities for backfilling and cleaning up data

---

## Development & Contribution
- All code is in this monorepo. Use the above setup for backend and frontend.
- PRs and issues welcome!

---

## License
MIT
