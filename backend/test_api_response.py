#!/usr/bin/env python3
"""
Test script to see the actual HERE API response structure
"""
import sys
import os
sys.path.append('.')

from app.utils.api_client import HereAPIClient
import json

def test_api_response():
    client = HereAPIClient()
    
    # Test with San Francisco bbox
    bbox = "-122.52,37.70,-122.35,37.83"
    
    print("Testing traffic flow API...")
    flow_data = client.get_traffic_flow(bbox)
    
    if flow_data:
        print("✅ Got flow response!")
        print(f"Flow response keys: {list(flow_data.keys())}")
        
        if 'results' in flow_data:
            results = flow_data['results']
            print(f"Number of flow results: {len(results)}")
            
            if results:
                print("\n🔍 First flow result structure:")
                first_result = results[0]
                print(f"Keys: {list(first_result.keys())}")
                
                if 'location' in first_result:
                    location = first_result['location']
                    print(f"Location keys: {list(location.keys())}")
                    print(f"Location: {json.dumps(location, indent=2)}")
                
                if 'currentFlow' in first_result:
                    current_flow = first_result['currentFlow']
                    print(f"CurrentFlow keys: {list(current_flow.keys())}")
                    print(f"CurrentFlow: {json.dumps(current_flow, indent=2)}")
    
    print("\n" + "="*50)
    print("Testing traffic incidents API...")
    incidents_data = client.get_traffic_incidents(bbox)
    
    if incidents_data:
        print("✅ Got incidents response!")
        print(f"Incidents response keys: {list(incidents_data.keys())}")
        
        if 'results' in incidents_data:
            results = incidents_data['results']
            print(f"Number of incident results: {len(results)}")
            
            if results:
                print("\n🔍 First incident result structure:")
                first_result = results[0]
                print(f"Keys: {list(first_result.keys())}")
                print(f"Full first incident: {json.dumps(first_result, indent=2)}")
    else:
        print("❌ No incidents data received")

if __name__ == "__main__":
    test_api_response() 