#!/usr/bin/env python3
"""
Quick Start: Test Data Access
==============================
Run this script to verify you can access all required datasets.

Usage:
    python quick_start.py
"""

import requests
import json

def test_endpoint(name, url, params=None):
    """Test an API endpoint and show sample data"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*60)
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                print(f"Records returned: {len(data)}")
                if len(data) > 0:
                    print(f"\nSample record keys: {list(data[0].keys())[:10]}")
                    print(f"\nFirst record preview:")
                    for k, v in list(data[0].items())[:5]:
                        print(f"  {k}: {v}")
            elif isinstance(data, dict):
                if "features" in data:
                    print(f"Features returned: {len(data['features'])}")
                    if len(data['features']) > 0:
                        props = data['features'][0].get('properties', {})
                        print(f"\nSample feature properties: {list(props.keys())}")
                else:
                    print(f"Response keys: {list(data.keys())}")
            
            return True
        else:
            print(f"Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False


def main():
    print("\n" + "#"*60)
    print("# AUSTIN FIRE RESOURCE ANALYSIS - DATA ACCESS TEST")
    print("#"*60)
    
    results = {}
    
    # Test 1: Fire Incidents (Socrata)
    results["fire_incidents"] = test_endpoint(
        "AFD Fire Incidents 2022-2024",
        "https://data.austintexas.gov/resource/v5hh-nyr8.json",
        params={"$limit": 5}
    )
    
    # Test 2: Fire Stations (Socrata)
    results["fire_stations"] = test_endpoint(
        "Fire Stations",
        "https://data.austintexas.gov/resource/szku-46rx.json",
        params={"$limit": 5}
    )
    
    # Test 3: Response Areas (ArcGIS)
    results["response_areas"] = test_endpoint(
        "AFD Response Areas (ArcGIS)",
        "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/BOUNDARIES_afd_response_areas/FeatureServer/0/query",
        params={
            "where": "1=1",
            "outFields": "*",
            "resultRecordCount": 3,
            "f": "json"
        }
    )
    
    # Test 4: Census API
    results["census"] = test_endpoint(
        "Census ACS Population (Travis County)",
        "https://api.census.gov/data/2022/acs/acs5",
        params={
            "get": "B01003_001E,NAME",
            "for": "tract:*",
            "in": "state:48 county:453"
        }
    )
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, success in results.items():
        status = "✓ OK" if success else "✗ FAILED"
        print(f"  {name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'All tests passed!' if all_passed else 'Some tests failed.'}")
    
    return all_passed


if __name__ == "__main__":
    main()
