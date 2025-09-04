from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import re

from app.db.session import SessionLocal
from app.db.models import TrafficIncident
from app.utils.api_client import HereAPIClient
from app.utils.logger import get_logger
from app.db.road_lookup import RoadLookup
from shapely.geometry import LineString, Point  # For distance calculation

logger = get_logger(__name__)

class TrafficIncidentsETL:
    """ETL pipeline for traffic incidents data from HERE API."""
    
    def __init__(self):
        self.api_client = HereAPIClient()
        self.road_lookup = RoadLookup()
    
    def extract(self, bbox: str = "-118.5,34.0,-118.2,34.2") -> Optional[Dict[str, Any]]:
        """Extract traffic incidents data from HERE API."""
        logger.info("Starting traffic incidents data extraction")
        data = self.api_client.get_traffic_incidents(bbox)
        
        if not data:
            logger.error("Failed to extract traffic incidents data")
            return None
        
        logger.info(f"Successfully extracted traffic incidents data")
        return data
    
    def transform(self, raw_data: Dict[str, Any]) -> List[TrafficIncident]:
        """Transform raw API data into TrafficIncident model instances (HERE API v7)."""
        logger.info("Starting traffic incidents data transformation (v7)")
        traffic_incidents = []
        try:
            results = raw_data.get('results', [])
            for idx, result in enumerate(results):
                location = result.get('location', {})
                incident_details = result.get('incidentDetails', {})
                
                # Extract incident type and description from incidentDetails
                incident_type = incident_details.get('type', 'UNKNOWN')
                description_obj = incident_details.get('description', {})
                description = description_obj.get('value', '') if description_obj else ''
                
                # Extract coordinates from location.shape.links[0].points[0]
                lat, lon = 37.7749, -122.4194  # San Francisco fallback
                here_road_name = location.get('description', 'Unknown Road')
                try:
                    shape = location.get('shape', {})
                    links = shape.get('links', [])
                    if links and len(links) > 0:
                        points = links[0].get('points', [])
                        if points and len(points) > 0:
                            first_point = points[0]
                            lat = first_point.get('lat', 34.0522)
                            lon = first_point.get('lng', -118.2437)
                except Exception as e:
                    logger.warning(f"Error extracting coordinates: {e}")
                
                # Lookup road name using OSM data
                road, line = None, None
                pt = Point(lon, lat)
                nearest = list(self.road_lookup.idx.nearest(pt.bounds, 5))
                min_dist = float('inf')
                best_road = None
                for i in nearest:
                    candidate_road, candidate_line = self.road_lookup.road_geoms[i]
                    dist = candidate_line.distance(pt)
                    if dist < min_dist:
                        min_dist = dist
                        best_road = candidate_road
                        line = candidate_line
                osm_name = best_road['name'] if best_road else 'Unknown Road'
                here_road_name = location.get('description', 'Unknown Road')
                # Try to extract intersection from description
                intersection = None
                if description:
                    match = re.search(r'[Aa]t ([^\-]+)\s*-', description)
                    if match:
                        intersection = match.group(1).strip()
                # Use OSM name at intersection if within 30 meters, else fallback
                if min_dist < 0.0003:
                    if intersection and osm_name not in intersection:
                        road_name = f"{osm_name} at {intersection}"
                    else:
                        road_name = osm_name
                else:
                    road_name = here_road_name
                if idx < 10:
                    print(f"Incident {idx+1}: HERE='{here_road_name}' | OSM='{road_name}' | Lat={lat}, Lon={lon}, Dist={min_dist:.6f}")
                logger.info(f"Incident at ({lat}, {lon}) matched to road: '{road_name}' (distance: {min_dist:.6f})")
                print(f"Incident at ({lat}, {lon}) matched to road: '{road_name}' (distance: {min_dist:.6f})")
                if min_dist > 0.0005:
                    logger.warning(f"Incident at ({lat}, {lon}) is more than ~50m from nearest road!")
                    print(f"WARNING: Incident at ({lat}, {lon}) is more than ~50m from nearest road!")
                # If TrafficIncident model does not have road_name, add as a comment for schema update
                traffic_incident = TrafficIncident(
                    type=incident_type,
                    description=description,
                    lat=lat,
                    lon=lon,
                    road_name=road_name,  # Now supported by schema
                    timestamp=datetime.utcnow()
                )
                traffic_incidents.append(traffic_incident)
            logger.info(f"Transformed {len(traffic_incidents)} traffic incident records (v7)")
            return traffic_incidents
        except Exception as e:
            logger.error(f"Error transforming traffic incidents data (v7): {str(e)}")
            return []
    
    def load(self, traffic_incidents: List[TrafficIncident]) -> int:
        """Load traffic incidents data into the database."""
        logger.info(f"Starting to load {len(traffic_incidents)} traffic incident records")
        
        db = SessionLocal()
        try:
            # Add all records to the session
            db.add_all(traffic_incidents)
            db.commit()
            
            logger.info(f"Successfully loaded {len(traffic_incidents)} traffic incident records")
            return len(traffic_incidents)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading traffic incidents data: {str(e)}")
            return 0
        finally:
            db.close()
    
    def run(self, bbox: str = "-118.5,34.0,-118.2,34.2") -> int:
        """Run the complete ETL pipeline for traffic incidents data."""
        logger.info("Starting traffic incidents ETL pipeline")
        
        # Extract
        raw_data = self.extract(bbox)
        if not raw_data:
            return 0
        
        # Transform
        traffic_incidents = self.transform(raw_data)
        if not traffic_incidents:
            return 0
        
        # Load
        loaded_count = self.load(traffic_incidents)
        
        logger.info(f"Traffic incidents ETL pipeline completed. Loaded {loaded_count} records")
        return loaded_count

def run_traffic_incidents_etl():
    """Convenience function to run the traffic incidents ETL pipeline."""
    etl = TrafficIncidentsETL()
    return etl.run()
