# Deployment Guide for Floficient

## Quick Deploy Options

### 1. Railway (Recommended for beginners)
1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub account
3. Select the Floficient repository
4. Railway will automatically detect the monorepo structure
5. Deploy both frontend and backend services

### 2. Vercel (Frontend) + Railway (Backend)
**Frontend on Vercel:**
1. Go to [Vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app`

**Backend on Railway:**
1. Deploy backend to Railway
2. Update frontend environment variable with Railway URL

### 3. Heroku
**Backend:**
1. Create a new Heroku app
2. Add PostgreSQL addon
3. Set environment variables
4. Deploy from GitHub

**Frontend:**
1. Create another Heroku app
2. Use buildpack: `heroku/nodejs`
3. Set root directory to `frontend`

### 4. DigitalOcean App Platform
1. Go to DigitalOcean App Platform
2. Create new app from GitHub
3. Configure both frontend and backend services
4. Add PostgreSQL database

## Environment Variables

### Backend (.env)
```
HERE_API_KEY=your_here_api_key
DATABASE_URL=postgresql://user:pass@host:port/dbname
PYTHONPATH=/app
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

## Manual Deployment Steps

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run build
npm start
```

## Docker Deployment
```bash
docker-compose up -d
```

## Database Setup
The app currently uses SQLite for development. For production:
1. Set up PostgreSQL database
2. Update DATABASE_URL in environment variables
3. Run database migrations

## API Keys Required
- HERE Technologies API key for traffic data
- (Optional) Mapbox token for custom map styles

## Notes
- The app is designed to work with San Francisco traffic data
- OSM road data is included in the repository
- ETL processes run automatically every 5 minutes
- Frontend is optimized for mobile and desktop
