import json
from shapely.geometry import LineString, Point
from rtree import index
import os

ROADS_FILE = os.path.join(os.path.dirname(__file__), 'sf_roads.json')

class RoadLookup:
    def __init__(self, roads_file=ROADS_FILE):
        with open(roads_file) as f:
            self.roads = json.load(f)
        self.road_geoms = []
        self.idx = index.Index()
        for i, road in enumerate(self.roads):
            line = LineString(road['geometry'])
            self.road_geoms.append((road, line))
            self.idx.insert(i, line.bounds)

    def find_nearest_road(self, lat, lon, max_results=5):
        pt = Point(lon, lat)
        nearest = list(self.idx.nearest(pt.bounds, max_results))
        min_dist = float('inf')
        best_road = None
        for i in nearest:
            road, line = self.road_geoms[i]
            dist = line.distance(pt)
            if dist < min_dist:
                min_dist = dist
                best_road = road
        return best_road['name'] if best_road else None

# Example usage:
if __name__ == '__main__':
    lookup = RoadLookup()
    # Example: San Francisco City Hall
    lat, lon = 37.7793, -122.4193
    print('Nearest road:', lookup.find_nearest_road(lat, lon)) 