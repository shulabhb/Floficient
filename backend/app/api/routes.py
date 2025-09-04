from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging
import asyncio
import threading
import time

from app.db.session import SessionLocal, get_db
from app.db.models import TrafficFlow, TrafficIncident
from app.utils.logger import get_logger
from app.scheduler.traffic_flow import TrafficFlowETL
from app.scheduler.traffic_incidents import TrafficIncidentsETL

logger = logging.getLogger(__name__)
router = APIRouter()

# Global variables for ETL state
last_etl_time = None
etl_in_progress = False
fallback_timer = None
cleanup_timer = None

# ETL instances
flow_etl = TrafficFlowETL()
incidents_etl = TrafficIncidentsETL()

# San Francisco bounding box ONLY
SF_BBOX = "-122.52,37.70,-122.35,37.83"

# Configuration
CACHE_WINDOW_MINUTES = 30  # Cache window for user visits (30 minutes)
FALLBACK_HOURS = 5  # Fallback timer when no users visit (5 hours)
CLEANUP_HOURS = 24  # Database cleanup every 24 hours

def should_run_etl():
    """Check if ETL should run based on cache window"""
    global last_etl_time
    
    if last_etl_time is None:
        return True
    
    time_since_last_etl = datetime.utcnow() - last_etl_time
    cache_duration = timedelta(minutes=CACHE_WINDOW_MINUTES)
    
    return time_since_last_etl > cache_duration

def should_run_fallback_etl():
    """Check if fallback ETL should run (5 hours)"""
    global last_etl_time
    
    if last_etl_time is None:
        return True
    
    time_since_last_etl = datetime.utcnow() - last_etl_time
    fallback_duration = timedelta(hours=FALLBACK_HOURS)
    
    return time_since_last_etl > fallback_duration

def should_run_cleanup():
    """Check if database cleanup should run (24 hours)"""
    global last_cleanup_time
    
    if not hasattr(should_run_cleanup, 'last_cleanup_time') or should_run_cleanup.last_cleanup_time is None:
        return True
    
    time_since_last_cleanup = datetime.utcnow() - should_run_cleanup.last_cleanup_time
    cleanup_duration = timedelta(hours=CLEANUP_HOURS)
    
    return time_since_last_cleanup > cleanup_duration

async def run_etl_async():
    """Run ETL asynchronously for San Francisco ONLY"""
    global last_etl_time, etl_in_progress
    
    if etl_in_progress:
        logger.info("ETL already in progress, skipping...")
        return
    
    etl_in_progress = True
    logger.info("🚀 Starting on-demand ETL for San Francisco...")
    logger.info(f"📊 Current cache window: {CACHE_WINDOW_MINUTES} minutes")
    logger.info(f"⏰ Fallback timer: {FALLBACK_HOURS} hours")
    
    try:
        # Run flow ETL for San Francisco ONLY
        logger.info("Running traffic flow ETL for San Francisco...")
        flow_etl.run(SF_BBOX)
        
        # Run incidents ETL for San Francisco ONLY
        logger.info("Running traffic incidents ETL for San Francisco...")
        incidents_etl.run(SF_BBOX)
        
        last_etl_time = datetime.utcnow()
        logger.info(f"ETL completed successfully at {last_etl_time}")
        
    except Exception as e:
        logger.error(f"ETL failed: {e}")
        raise HTTPException(status_code=500, detail=f"ETL failed: {str(e)}")
    finally:
        etl_in_progress = False

async def run_cleanup_async():
    """Run database cleanup asynchronously"""
    global cleanup_in_progress
    
    if hasattr(run_cleanup_async, 'cleanup_in_progress') and run_cleanup_async.cleanup_in_progress:
        logger.info("Cleanup already in progress, skipping...")
        return
    
    run_cleanup_async.cleanup_in_progress = True
    logger.info("Starting database cleanup...")
    
    try:
        db = SessionLocal()
        
        # Calculate cutoff time (24 hours ago)
        cutoff_time = datetime.utcnow() - timedelta(hours=CLEANUP_HOURS)
        
        # Delete old traffic flow records
        flow_deleted = db.query(TrafficFlow).filter(TrafficFlow.timestamp < cutoff_time).delete()
        logger.info(f"Deleted {flow_deleted} old traffic flow records")
        
        # Delete old traffic incident records
        incidents_deleted = db.query(TrafficIncident).filter(TrafficIncident.timestamp < cutoff_time).delete()
        logger.info(f"Deleted {incidents_deleted} old traffic incident records")
        
        db.commit()
        
        # Update last cleanup time
        should_run_cleanup.last_cleanup_time = datetime.utcnow()
        logger.info(f"Database cleanup completed at {should_run_cleanup.last_cleanup_time}")
        
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")
        db.rollback()
    finally:
        db.close()
        run_cleanup_async.cleanup_in_progress = False

def start_fallback_timer():
    """Start the fallback timer for 5-hour intervals"""
    global fallback_timer
    
    def fallback_worker():
        while True:
            time.sleep(60)  # Check every minute
            if should_run_fallback_etl():
                logger.info("Fallback timer triggered - running ETL")
                asyncio.run(run_etl_async())
    
    if fallback_timer is None or not fallback_timer.is_alive():
        fallback_timer = threading.Thread(target=fallback_worker, daemon=True)
        fallback_timer.start()
        logger.info("Fallback timer started (5-hour intervals)")

def start_cleanup_timer():
    """Start the cleanup timer for 24-hour intervals"""
    global cleanup_timer
    
    def cleanup_worker():
        while True:
            time.sleep(60)  # Check every minute
            if should_run_cleanup():
                logger.info("Cleanup timer triggered - running database cleanup")
                asyncio.run(run_cleanup_async())
    
    if cleanup_timer is None or not cleanup_timer.is_alive():
        cleanup_timer = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_timer.start()
        logger.info("Cleanup timer started (24-hour intervals)")

# Start timers when module loads
start_fallback_timer()
start_cleanup_timer()

@router.get("/")
async def root():
    return {"message": "Floficient Traffic API", "status": "running"}

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@router.get("/traffic/flow")
async def get_traffic_flow(
    limit: int = Query(100, ge=1, le=1000),
    hours: Optional[int] = Query(None, ge=1, le=168),
    bbox: Optional[str] = Query(None),
    road_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get traffic flow data with on-demand ETL"""
    # Check if we need to run ETL
    if should_run_etl():
        logger.info("Cache expired - running ETL before serving traffic flow data")
        await run_etl_async()
    
    # Build query
    query = db.query(TrafficFlow)
    
    if hours:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(TrafficFlow.timestamp >= cutoff_time)
    
    if bbox:
        # Parse bbox: "west,south,east,north"
        coords = bbox.split(',')
        if len(coords) == 4:
            west, south, east, north = map(float, coords)
            query = query.filter(
                TrafficFlow.lon >= west,
                TrafficFlow.lon <= east,
                TrafficFlow.lat >= south,
                TrafficFlow.lat <= north
            )
    
    if road_name:
        query = query.filter(TrafficFlow.road_name.ilike(f"%{road_name}%"))
    
    # Order by timestamp and limit
    query = query.order_by(TrafficFlow.timestamp.desc()).limit(limit)
    
    # Execute query
    results = query.all()
    
    return {
        "data": [
        {
            "id": record.id,
            "timestamp": record.timestamp.isoformat(),
            "road_name": record.road_name,
            "speed": record.speed,
            "congestion_level": record.congestion_level,
                "latitude": record.lat,
                "longitude": record.lon,
                "geometry": record.geometry
        }
        for record in results
        ],
        "total": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/traffic/incidents")
async def get_traffic_incidents(
    limit: int = Query(100, ge=1, le=1000),
    hours: Optional[int] = Query(None, ge=1, le=168),
    bbox: Optional[str] = Query(None),
    incident_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get traffic incidents data with on-demand ETL"""
    # Check if we need to run ETL
    if should_run_etl():
        logger.info("Cache expired - running ETL before serving traffic incidents data")
        await run_etl_async()
    
    # Build query
    query = db.query(TrafficIncident)
    
    if hours:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(TrafficIncident.timestamp >= cutoff_time)
    
    if bbox:
        # Parse bbox: "west,south,east,north"
        coords = bbox.split(',')
        if len(coords) == 4:
            west, south, east, north = map(float, coords)
            query = query.filter(
                TrafficIncident.lon >= west,
                TrafficIncident.lon <= east,
                TrafficIncident.lat >= south,
                TrafficIncident.lat <= north
            )
    
    if incident_type:
        query = query.filter(TrafficIncident.type.ilike(f"%{incident_type}%"))
    
    # Order by timestamp and limit
    query = query.order_by(TrafficIncident.timestamp.desc()).limit(limit)
    
    # Execute query
    results = query.all()
    
    return {
        "data": [
        {
            "id": record.id,
            "timestamp": record.timestamp.isoformat(),
            "type": record.type,
            "description": record.description,
            "lat": record.lat,
            "lon": record.lon
        }
        for record in results
        ],
        "total": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/traffic/roads")
async def get_unique_roads(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get unique road names with on-demand ETL"""
    # Check if we need to run ETL
    if should_run_etl():
        logger.info("Cache expired - running ETL before serving road names data")
        await run_etl_async()
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    roads = db.query(TrafficFlow.road_name)\
        .filter(TrafficFlow.timestamp >= cutoff_time)\
        .distinct()\
        .all()
    
    return [road[0] for road in roads]

@router.post("/etl/trigger")
async def trigger_etl():
    """Manually trigger ETL"""
    await run_etl_async()
    return {"message": "ETL triggered successfully", "timestamp": datetime.utcnow().isoformat()}

@router.get("/etl/status")
async def get_etl_status():
    """Get ETL status and cache information"""
    global last_etl_time, etl_in_progress
    
    # Calculate time until next ETL
    time_until_next_etl = None
    if last_etl_time:
        next_etl_time = last_etl_time + timedelta(minutes=CACHE_WINDOW_MINUTES)
        time_until_next_etl = (next_etl_time - datetime.utcnow()).total_seconds() / 60  # minutes
    
    status = {
        "last_etl": last_etl_time.isoformat() if last_etl_time else None,
        "etl_in_progress": etl_in_progress,
        "cache_window_minutes": CACHE_WINDOW_MINUTES,
        "fallback_hours": FALLBACK_HOURS,
        "cleanup_hours": CLEANUP_HOURS,
        "time_until_next_etl_minutes": round(time_until_next_etl, 1) if time_until_next_etl else None,
        "next_fallback_check": None,
        "next_cleanup_check": None,
        "city": "San Francisco Only",
        "api_calls_conservation": "✅ Optimized for free tier - 30min cache, 5hr fallback"
    }
    
    if last_etl_time:
        next_fallback = last_etl_time + timedelta(hours=FALLBACK_HOURS)
        status["next_fallback_check"] = next_fallback.isoformat()
    
    if hasattr(should_run_cleanup, 'last_cleanup_time') and should_run_cleanup.last_cleanup_time:
        next_cleanup = should_run_cleanup.last_cleanup_time + timedelta(hours=CLEANUP_HOURS)
        status["next_cleanup_check"] = next_cleanup.isoformat()
    
    return status

@router.post("/cleanup/trigger")
async def trigger_cleanup():
    """Manually trigger database cleanup"""
    await run_cleanup_async()
    return {"message": "Database cleanup triggered successfully", "timestamp": datetime.utcnow().isoformat()}
