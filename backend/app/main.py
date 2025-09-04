from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as traffic_router
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Floficient Traffic API",
    description="Real-time traffic data API for California cities",
    version="1.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the traffic routes
app.include_router(traffic_router, prefix="/api/v1", tags=["traffic"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Floficient Traffic API",
        "version": "1.0.0",
        "endpoints": {
            "traffic_flow": "/api/v1/traffic/flow",
            "traffic_incidents": "/api/v1/traffic/incidents", 
            "road_names": "/api/v1/traffic/roads",
            "health": "/api/v1/health",
            "etl_status": "/api/v1/etl/status",
            "etl_trigger": "/api/v1/etl/trigger",
            "cleanup_trigger": "/api/v1/cleanup/trigger"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
