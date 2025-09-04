import json
import os

INPUT = 'sf_roads.json'
OUTPUT = 'sf_roads_lines.geojson'

with open(INPUT) as f:
    roads = json.load(f)

features = []
for road in roads:
    coords = road.get('geometry')
    name = road.get('name')
    if not coords or not name or len(coords) < 2:
        continue
    features.append({
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": coords},
        "properties": {"name": name}
    })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open(OUTPUT, 'w') as f:
    json.dump(geojson, f)

print(f"Exported {len(features)} road lines to {OUTPUT}") 