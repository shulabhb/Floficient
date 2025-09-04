from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import TrafficFlow
from app.utils.api_client import HereAPIClient
from app.utils.logger import get_logger
from app.utils.geo import calculate_midpoint
from app.db.road_lookup import RoadLookup
from shapely.geometry import LineString, Point

logger = get_logger(__name__)

class TrafficFlowETL:
    """ETL pipeline for traffic flow data from HERE API."""
    
    def __init__(self):
        self.api_client = HereAPIClient()
        self.road_lookup = RoadLookup()
        # Load all OSM roads for geometry extension
        self.osm_roads = self.road_lookup.roads
        self.osm_lines = [LineString(road['geometry']) for road in self.osm_roads]
    
    def extract(self, bbox: str = "-118.5,34.0,-118.2,34.2") -> Optional[Dict[str, Any]]:
        """Extract traffic flow data from HERE API."""
        logger.info("Starting traffic flow data extraction")
        data = self.api_client.get_traffic_flow(bbox)
        
        if not data:
            logger.error("Failed to extract traffic flow data")
            return None
        
        logger.info(f"Successfully extracted traffic flow data")
        return data
    
    def extend_congestion_geometry(self, geometry: list, extend_points: int = 3) -> list:
        if not geometry or len(geometry) < 2:
            return geometry
        # Use the midpoint to find the nearest OSM road
        mid_idx = len(geometry) // 2
        mid_point = Point(geometry[mid_idx])
        min_dist = float('inf')
        best_road = None
        best_line = None
        for road, line in zip(self.osm_roads, self.osm_lines):
            dist = line.distance(mid_point)
            if dist < min_dist:
                min_dist = dist
                best_road = road
                best_line = line
        if not best_line:
            return geometry
        # Find closest indices on the OSM road
        coords = list(best_line.coords)
        def closest_idx(pt):
            return min(range(len(coords)), key=lambda i: Point(coords[i]).distance(Point(pt)))
        start_idx = closest_idx(geometry[0])
        end_idx = closest_idx(geometry[-1])
        # Extend indices
        new_start = max(0, start_idx - extend_points)
        new_end = min(len(coords) - 1, end_idx + extend_points)
        extended_coords = coords[new_start:new_end+1]
        return extended_coords
    
    def transform(self, raw_data: Dict[str, Any]) -> List[TrafficFlow]:
        """Transform raw API data into TrafficFlow model instances (HERE API v7)."""
        logger.info("Starting traffic flow data transformation (v7)")
        traffic_flows = []
        try:
            results = raw_data.get('results', [])
            # Debug: print first 2 raw results
            for i, result in enumerate(results[:2]):
                logger.info(f"RAW API RESULT {i+1}: {result}")
            for idx, result in enumerate(results):
                location = result.get('location', {})
                current_flow = result.get('currentFlow', {})
                road_name = location.get('description', 'Unknown Road')
                speed = current_flow.get('speed', 0.0)
                jam_factor = current_flow.get('jamFactor', 0.0)
                # Extract coordinates from location.shape.links[0].points[0]
                lat, lon = 37.7749, -122.4194  # San Francisco fallback
                try:
                    shape = location.get('shape', {})
                    links = shape.get('links', [])
                    if links and len(links) > 0:
                        points = links[0].get('points', [])
                        if points and len(points) > 0:
                            first_point = points[0]
                            lat = first_point.get('lat', 37.7749)
                            lon = first_point.get('lng', -122.4194)
                            geometry = [[pt['lng'], pt['lat']] for pt in points]
                        else:
                            geometry = None
                    else:
                        geometry = None
                except Exception as e:
                    logger.warning(f"Error extracting coordinates: {e}")
                    geometry = None
                # NEW: Lookup road name using OSM data
                matched_road_name = self.road_lookup.find_nearest_road(lat, lon)
                if matched_road_name:
                    road_name = matched_road_name
                # Extend congestion geometry if possible
                if geometry and len(geometry) >= 2:
                    geometry = self.extend_congestion_geometry(geometry, extend_points=3)
                traffic_flow = TrafficFlow(
                    speed=speed,
                    congestion_level=jam_factor,
                    road_name=road_name,
                    lat=lat,
                    lon=lon,
                    geometry=geometry,
                    timestamp=datetime.utcnow()
                )
                # Debug: print first 2 transformed records
                if idx < 2:
                    logger.info(f"TRANSFORMED FLOW {idx+1}: road_name={road_name}, speed={speed}, jam_factor={jam_factor}, lat={lat}, lon={lon}")
                traffic_flows.append(traffic_flow)
            logger.info(f"Transformed {len(traffic_flows)} traffic flow records (v7)")
            return traffic_flows
        except Exception as e:
            logger.error(f"Error transforming traffic flow data (v7): {str(e)}")
            return []
    
    def _create_traffic_flow(self, cf: Dict[str, Any], tmc: Dict[str, Any], shape: List[str]) -> Optional[TrafficFlow]:
        """Create a TrafficFlow instance from extracted data."""
        try:
            # Extract speed and congestion level
            speed = cf.get('SU', 0.0)  # Speed Uncongested
            congestion_level = cf.get('JF', 0.0)  # Jam Factor
            
            # Extract road name
            road_name = tmc.get('DE', 'Unknown Road')
            
            # Calculate coordinates from shape
            lat, lon = self._extract_coordinates(shape)
            
            # Create TrafficFlow instance
            traffic_flow = TrafficFlow(
                speed=speed,
                congestion_level=congestion_level,
                road_name=road_name,
                lat=lat,
                lon=lon,
                timestamp=datetime.utcnow()
            )
            
            return traffic_flow
            
        except Exception as e:
            logger.error(f"Error creating traffic flow record: {str(e)}")
            return None
    
    def _extract_coordinates(self, shape: List[str]) -> tuple[float, float]:
        """Extract latitude and longitude from shape data."""
        if not shape:
            # Default to Los Angeles coordinates if no shape data
            return 34.0522, -118.2437
        
        try:
            # Take the first coordinate pair from the shape
            coord_str = shape[0]
            lat_str, lon_str = coord_str.split(',')
            
            lat = float(lat_str)
            lon = float(lon_str)
            
            return lat, lon
            
        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse coordinates from shape {shape}: {str(e)}")
            # Default to Los Angeles coordinates
            return 34.0522, -118.2437
    
    def load(self, traffic_flows: List[TrafficFlow]) -> int:
        """Load traffic flow data into the database."""
        logger.info(f"Starting to load {len(traffic_flows)} traffic flow records")
        
        db = SessionLocal()
        try:
            # Add all records to the session
            db.add_all(traffic_flows)
            db.commit()
            
            logger.info(f"Successfully loaded {len(traffic_flows)} traffic flow records")
            return len(traffic_flows)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading traffic flow data: {str(e)}")
            return 0
        finally:
            db.close()
    
    def run(self, bbox: str = "-118.5,34.0,-118.2,34.2") -> int:
        """Run the complete ETL pipeline for traffic flow data."""
        logger.info("Starting traffic flow ETL pipeline")
        
        # Extract
        raw_data = self.extract(bbox)
        if not raw_data:
            return 0
        
        # Transform
        traffic_flows = self.transform(raw_data)
        if not traffic_flows:
            return 0
        
        # Load
        loaded_count = self.load(traffic_flows)
        
        logger.info(f"Traffic flow ETL pipeline completed. Loaded {loaded_count} records")
        return loaded_count

def run_traffic_flow_etl():
    """Convenience function to run the traffic flow ETL pipeline."""
    etl = TrafficFlowETL()
    return etl.run()
