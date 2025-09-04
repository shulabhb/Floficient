import sqlite3
import re

DB_PATH = './backend/test.db'

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Try to get both OSM and HERE names if available
cur.execute("SELECT id, lat, lon, road_name, description FROM traffic_incident LIMIT 1000")
rows = cur.fetchall()

print("Comparing OSM and HERE road names for incidents (showing mismatches):\n")
count = 0
for row in rows:
    incident_id, lat, lon, osm_name, description = row
    here_name = None
    if description:
        # Try 'At ... - ...' or 'at ... - ...'
        match = re.search(r'[Aa]t ([^\-]+)\s*-', description)
        if match:
            here_name = match.group(1).strip()
        # Try 'Between ... and ...'
        elif 'between' in description.lower() and 'and' in description.lower():
            match = re.search(r'[Bb]etween ([^a]+) and ([^\-]+)', description)
            if match:
                here_name = f"{match.group(1).strip()} and {match.group(2).strip()}"
        # Try '... at ...'
        elif ' at ' in description:
            parts = description.split(' at ')
            if len(parts) > 1:
                here_name = parts[1].split(' - ')[0].strip()
    if here_name and here_name != osm_name:
        print(f"ID={incident_id} | Lat={lat:.5f}, Lon={lon:.5f} | OSM='{osm_name}' | HERE='{here_name}' | Desc='{description}'")
        count += 1
    if count >= 40:
        break
if count == 0:
    print("No mismatches found or HERE name not extractable from description.")
conn.close() 