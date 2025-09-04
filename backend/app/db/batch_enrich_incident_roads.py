import sqlite3
import json
import re
from shapely.geometry import Point
from road_lookup import RoadLookup

DB_PATH = './backend/test.db'

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
lookup = RoadLookup()

cur.execute("SELECT id, lat, lon, description, road_name FROM traffic_incident")
rows = cur.fetchall()

updated = 0
for row in rows:
    incident_id, lat, lon, description, old_road_name = row
    pt = Point(lon, lat)
    nearest = list(lookup.idx.nearest(pt.bounds, 5))
    min_dist = float('inf')
    best_road = None
    best_line = None
    for i in nearest:
        candidate_road, candidate_line = lookup.road_geoms[i]
        dist = candidate_line.distance(pt)
        if dist < min_dist:
            min_dist = dist
            best_road = candidate_road
            best_line = candidate_line
    osm_name = best_road['name'] if best_road else 'Unknown Road'
    here_road_name = None
    intersection = None
    if description:
        match = re.search(r'[Aa]t ([^\-]+)\s*-', description)
        if match:
            intersection = match.group(1).strip()
        here_road_name = description.split(' at ')[-1].split(' - ')[0].strip() if ' at ' in description else None
    # Use OSM name at intersection if within 30 meters, else fallback
    if min_dist < 0.0003:
        if intersection and osm_name not in intersection:
            road_name = f"{osm_name} at {intersection}"
        else:
            road_name = osm_name
    else:
        road_name = here_road_name or osm_name
    if road_name != old_road_name:
        cur.execute("UPDATE traffic_incident SET road_name = ? WHERE id = ?", (road_name, incident_id))
        updated += 1
conn.commit()
print(f"Batch updated {updated} incidents with improved road names.")
conn.close() 