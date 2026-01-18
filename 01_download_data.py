#!/usr/bin/env python3
"""
Step 1: Download Data
======================
Downloads all required data files for the fire resource analysis.

Usage:
    python scripts/01_download_data.py

Output:
    raw_data/afd_incidents_2022_2024.csv
    raw_data/afd_incidents_2018_2021.csv
    raw_data/afd_response_areas.geojson
    raw_data/census_population.csv
    raw_data/census_housing.csv
    raw_data/census_year_built.csv
    raw_data/fire_stations.geojson
    raw_data/travis_county_tracts.geojson
"""

import os
import requests
import json

# Create directories
os.makedirs("raw_data", exist_ok=True)
os.makedirs("processed_data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

def download_file(url, filename, description):
    """Download a file with progress indication"""
    print(f"\n{'='*60}")
    print(f"Downloading: {description}")
    print(f"URL: {url}")
    print(f"Saving to: {filename}")
    print('='*60)
    
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        size_mb = len(response.content) / (1024 * 1024)
        print(f"✓ Downloaded {size_mb:.2f} MB")
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def download_census_api(table, variables, filename, description):
    """Download data from Census API"""
    print(f"\n{'='*60}")
    print(f"Downloading: {description}")
    print(f"Table: {table}")
    print('='*60)
    
    base_url = "https://api.census.gov/data/2022/acs/acs5"
    var_string = ",".join(variables)
    
    url = f"{base_url}?get={var_string}&for=tract:*&in=state:48&in=county:453"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert to CSV format
        import csv
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)
        
        print(f"✓ Downloaded {len(data)-1} records")
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def main():
    print("\n" + "#"*60)
    print("# FIRE RESOURCE ANALYSIS - DATA DOWNLOAD")
    print("#"*60)
    
    results = {}
    
    # 1. Fire Incidents 2022-2024
    results['incidents_recent'] = download_file(
        "https://data.austintexas.gov/api/views/v5hh-nyr8/rows.csv?accessType=DOWNLOAD",
        "raw_data/afd_incidents_2022_2024.csv",
        "AFD Fire Incidents 2022-2024"
    )
    
    # 2. Fire Incidents 2018-2021
    results['incidents_historical'] = download_file(
        "https://data.austintexas.gov/api/views/j9w8-x2vu/rows.csv?accessType=DOWNLOAD",
        "raw_data/afd_incidents_2018_2021.csv",
        "AFD Fire Incidents 2018-2021"
    )
    
    # 3. AFD Response Areas
    results['response_areas'] = download_file(
        "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/BOUNDARIES_afd_response_areas/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson",
        "raw_data/afd_response_areas.geojson",
        "AFD Response Area Boundaries"
    )
    
    # 4. Census Population
    results['census_population'] = download_census_api(
        "B01003",
        ["B01003_001E", "NAME"],
        "raw_data/census_population.csv",
        "Census Population by Tract (Travis County)"
    )
    
    # 5. Census Housing Units by Type
    housing_vars = ["B25024_001E"]  # Total
    housing_vars += [f"B25024_{str(i).zfill(3)}E" for i in range(2, 12)]  # Breakdown
    housing_vars += ["NAME"]
    
    results['census_housing'] = download_census_api(
        "B25024",
        housing_vars,
        "raw_data/census_housing.csv",
        "Census Housing Units by Type (Travis County)"
    )

    # 6. Census Year Structure Built (B25034)
    year_built_vars = [
        "B25034_001E",  # Total
        "B25034_002E",  # Built 2020 or later
        "B25034_003E",  # Built 2010-2019
        "B25034_004E",  # Built 2000-2009
        "B25034_005E",  # Built 1990-1999
        "B25034_006E",  # Built 1980-1989
        "B25034_007E",  # Built 1970-1979
        "B25034_008E",  # Built 1960-1969
        "B25034_009E",  # Built 1950-1959
        "B25034_010E",  # Built 1940-1949
        "B25034_011E",  # Built 1939 or earlier
        "NAME"
    ]

    results['census_year_built'] = download_census_api(
        "B25034",
        year_built_vars,
        "raw_data/census_year_built.csv",
        "Census Year Structure Built (Travis County)"
    )

    # 7. Fire Station Locations (from ArcGIS)
    results['fire_stations'] = download_file(
        "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/LOCATION_fire_stations/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=geojson",
        "raw_data/fire_stations.geojson",
        "Fire Station Locations"
    )

    # 8. Census Tract Boundaries (try Census Reporter first, then TIGER)
    results['tract_boundaries'] = download_file(
        "https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_48_tract.zip",
        "raw_data/tl_2023_48_tract.zip",
        "Census Tract Boundaries (Texas)"
    )
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    for name, success in results.items():
        status = "✓ OK" if success else "✗ FAILED"
        print(f"  {name}: {status}")
    
    # Next steps
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. If tract boundaries downloaded as ZIP, unzip:
   unzip raw_data/tl_2023_48_tract.zip -d raw_data/

2. Filter Texas tracts to Travis County only (in QGIS or Python):
   Keep only COUNTYFP = '453'

3. Run the next script:
   python scripts/02_clean_incidents.py
""")
    
    return all(results.values())


if __name__ == "__main__":
    main()
