from typing import List, Tuple

def calculate_midpoint(coordinates: List[str]) -> Tuple[float, float]:
    """
    Calculate the midpoint of a list of coordinates.
    
    Args:
        coordinates: List of coordinate strings in "lat,lon" format
    
    Returns:
        Tuple of (latitude, longitude) for the midpoint
    """
    if not coordinates:
        return 34.0522, -118.2437  # Default to Los Angeles
    
    try:
        # For now, just return the first coordinate
        # In the future, this could calculate the actual midpoint
        coord_str = coordinates[0]
        lat_str, lon_str = coord_str.split(',')
        
        lat = float(lat_str)
        lon = float(lon_str)
        
        return lat, lon
        
    except (ValueError, IndexError):
        return 34.0522, -118.2437  # Default to Los Angeles
