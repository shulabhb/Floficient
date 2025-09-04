#!/usr/bin/env python3
"""
Bay Area cities with bounding boxes for HERE API coverage
"""

BAY_AREA_CITIES = {
    # San Francisco Bay Area - Core Cities
    "San Francisco": "-122.52,37.70,-122.35,37.83",
    "Oakland": "-122.35,37.70,-122.12,37.89",
    "San Jose": "-122.05,37.20,-121.75,37.45",
    "Fremont": "-122.05,37.45,-121.85,37.65",
    "Hayward": "-122.15,37.55,-121.95,37.75",
    
    # Peninsula Cities
    "Palo Alto": "-122.20,37.35,-122.05,37.55",
    "Mountain View": "-122.15,37.35,-122.00,37.45",
    "Redwood City": "-122.25,37.45,-122.10,37.55",
    "San Mateo": "-122.35,37.50,-122.20,37.60",
    "Daly City": "-122.50,37.65,-122.35,37.75",
    
    # East Bay Cities
    "Berkeley": "-122.35,37.80,-122.20,37.95",
    "Richmond": "-122.45,37.85,-122.30,38.00",
    "Concord": "-122.05,37.90,-121.90,38.05",
    "Walnut Creek": "-122.15,37.85,-122.00,38.00",
    "Pleasanton": "-122.00,37.60,-121.85,37.75",
    
    # Additional Major Cities
    "Santa Clara": "-122.00,37.30,-121.85,37.40",
    "Sunnyvale": "-122.10,37.30,-121.95,37.40",
    "Cupertino": "-122.15,37.25,-122.00,37.35",
    "San Rafael": "-122.55,37.90,-122.40,38.05",
    "Vallejo": "-122.30,37.95,-122.15,38.10",
}

# Calculate API usage
def calculate_api_usage():
    num_cities = len(BAY_AREA_CITIES)
    calls_per_20min = num_cities * 2  # flow + incidents
    calls_per_hour = calls_per_20min * 3  # 3 times per hour
    calls_per_day = calls_per_hour * 24
    calls_per_month = calls_per_day * 30
    
    print(f"📊 API Usage Calculation for {num_cities} Bay Area Cities (20-min refresh):")
    print(f"   Cities: {num_cities}")
    print(f"   API calls per 20 minutes: {calls_per_20min}")
    print(f"   API calls per hour: {calls_per_hour}")
    print(f"   API calls per day: {calls_per_day:,}")
    print(f"   API calls per month: {calls_per_month:,}")
    print(f"   HERE Free Tier: 250,000 calls/month")
    print(f"   Usage percentage: {(calls_per_month/250000)*100:.1f}%")
    
    # Check if it fits in free tier
    if calls_per_month <= 250000:
        print(f"   ✅ FITS IN FREE TIER!")
    else:
        print(f"   ❌ EXCEEDS FREE TIER by {calls_per_month - 250000:,} calls")
    
    return calls_per_month

if __name__ == "__main__":
    calculate_api_usage() 