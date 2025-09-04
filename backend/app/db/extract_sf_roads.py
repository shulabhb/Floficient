import xml.etree.ElementTree as ET
import json

OSM_FILE = 'planet_-122.57,37.659_-122.293,37.858.osm'
OUTPUT_FILE = 'sf_roads.json'

# Step 1: Parse all nodes and build a lookup dict
print('Parsing nodes...')
node_coords = {}
for event, elem in ET.iterparse(OSM_FILE, events=('start', 'end')):
    if event == 'end' and elem.tag == 'node':
        node_id = int(elem.attrib['id'])
        lat = float(elem.attrib['lat'])
        lon = float(elem.attrib['lon'])
        node_coords[node_id] = (lon, lat)
        elem.clear()
print(f"Parsed {len(node_coords)} nodes.")

# Step 2: Parse ways and build road geometries
print('Parsing ways...')
roads = []
for event, elem in ET.iterparse(OSM_FILE, events=('start', 'end')):
    if event == 'end' and elem.tag == 'way':
        tags = {tag.attrib['k']: tag.attrib['v'] for tag in elem.findall('tag')}
        if 'highway' in tags:
            name = tags.get('name')
            if not name:
                elem.clear()
                continue  # skip unnamed roads for now
            node_refs = [int(nd.attrib['ref']) for nd in elem.findall('nd')]
            coords = [node_coords.get(ref) for ref in node_refs if ref in node_coords]
            if len(coords) >= 2:
                roads.append({
                    'osm_id': int(elem.attrib['id']),
                    'name': name,
                    'geometry': coords
                })
        elem.clear()
print(f"Extracted {len(roads)} named roads.")

# Step 3: Write to JSON
with open(OUTPUT_FILE, 'w') as f:
    json.dump(roads, f)
print(f"Wrote {len(roads)} roads to {OUTPUT_FILE}") 