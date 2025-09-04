#!/usr/bin/env python3
"""
Test script for HERE Traffic API v7 client
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.api_client import HereAPIClient
from app.utils.logger import get_logger

logger = get_logger(__name__)

def test_api_client():
    """Test the HERE API client with the correct v7 endpoints."""
    
    print("🚀 Testing HERE Traffic API v7 Client")
    print("=" * 50)
    
    # Initialize API client
    client = HereAPIClient()
    
    # Test bounding box for San Francisco Bay Area (west,south,east,north)
    bbox = "-122.5,37.7,-122.4,37.8"  # Correct format for v7
    
    print(f"📍 Testing with bounding box: {bbox}")
    print(f"🔑 API Key: {client.api_key[:10]}...")
    print(f"🌐 Base URL: {client.base_url}")
    print()
    
    # Test traffic flow endpoint
    print("🛣️  Testing Traffic Flow API...")
    flow_data = client.get_traffic_flow(bbox)
    
    if flow_data:
        print("✅ Traffic Flow API call successful!")
        print(f"📊 Response keys: {list(flow_data.keys())}")
        
        # Check for flow data
        flows = flow_data.get('flow', [])
        print(f"🛣️  Number of flow records: {len(flows)}")
        
        if flows:
            # Show first flow record structure
            first_flow = flows[0]
            print(f"📋 First flow record keys: {list(first_flow.keys())}")
            
            location = first_flow.get('location', {})
            current_flow = first_flow.get('currentFlow', {})
            
            print(f"📍 Location keys: {list(location.keys())}")
            print(f"🚦 Current flow keys: {list(current_flow.keys())}")
            
            # Show some sample data
            speed = current_flow.get('speed', 0)
            jam_factor = current_flow.get('jamFactor', 0)
            print(f"⚡ Speed: {speed} m/s")
            print(f"🚧 Jam Factor: {jam_factor}")
    else:
        print("❌ Traffic Flow API call failed!")
    
    print()
    
    # Test traffic incidents endpoint
    print("🚨 Testing Traffic Incidents API...")
    incidents_data = client.get_traffic_incidents(bbox)
    
    if incidents_data:
        print("✅ Traffic Incidents API call successful!")
        print(f"📊 Response keys: {list(incidents_data.keys())}")
        
        # Check for incidents data
        incidents = incidents_data.get('incidents', [])
        print(f"🚨 Number of incident records: {len(incidents)}")
        
        if incidents:
            # Show first incident record structure
            first_incident = incidents[0]
            print(f"📋 First incident record keys: {list(first_incident.keys())}")
            
            location = first_incident.get('location', {})
            incident_details = first_incident.get('incidentDetails', {})
            
            print(f"📍 Location keys: {list(location.keys())}")
            print(f"🚨 Incident details keys: {list(incident_details.keys())}")
            
            # Show some sample data
            incident_type = incident_details.get('type', 'unknown')
            description = incident_details.get('description', 'No description')
            print(f"🚨 Type: {incident_type}")
            print(f"📝 Description: {description[:100]}...")
    else:
        print("❌ Traffic Incidents API call failed!")
    
    print()
    print("🏁 API testing completed!")

if __name__ == "__main__":
    test_api_client() 