"""
Austin Fire Department Resource Allocation Analysis
=====================================================
Research Question: Do suburban areas utilize disproportionate fire resources 
per capita compared to urban areas?

Author: Research Hub - Austin Housing/Land Use Working Group
"""

import pandas as pd
import geopandas as gpd
import requests
import json
from shapely.geometry import Point
import numpy as np

# =============================================================================
# DATA SOURCE CONFIGURATION
# =============================================================================

SOURCES = {
    # Austin Open Data Portal (Socrata API)
    "fire_incidents_2022_2024": {
        "url": "https://data.austintexas.gov/resource/v5hh-nyr8.json",
        "csv_url": "https://data.austintexas.gov/api/views/v5hh-nyr8/rows.csv?accessType=DOWNLOAD",
        "description": "AFD Fire Incidents 2022-2024",
        "fields": ["incident_number", "calendaryear", "month", "incdate", 
                   "call_type", "problem", "responsearea", "jurisdiction",
                   "prioritydescription", "council_district", "location"]
    },
    "fire_incidents_2018_2021": {
        "url": "https://data.austintexas.gov/resource/j9w8-x2vu.json",
        "csv_url": "https://data.austintexas.gov/api/views/j9w8-x2vu/rows.csv?accessType=DOWNLOAD",
        "description": "AFD Fire Incidents 2018-2021"
    },
    "fire_stations": {
        "url": "https://data.austintexas.gov/resource/szku-46rx.json",
        "description": "Austin Fire Station Locations"
    },
    
    # ArcGIS FeatureServer (City of Austin GIS)
    "afd_response_areas": {
        "url": "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/BOUNDARIES_afd_response_areas/FeatureServer/0",
        "query_url": "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/BOUNDARIES_afd_response_areas/FeatureServer/0/query",
        "description": "AFD Response Area Boundaries"
    },
    
    # Census API
    "census_population": {
        "base_url": "https://api.census.gov/data/2022/acs/acs5",
        "table": "B01003",  # Total Population
        "description": "ACS 5-Year Population Estimates by Tract"
    },
    "census_housing_units": {
        "base_url": "https://api.census.gov/data/2022/acs/acs5",
        "table": "B25024",  # Units in Structure
        "description": "Housing Units by Type (SF, MF, etc.) by Tract"
    }
}


# =============================================================================
# DATA FETCHING FUNCTIONS
# =============================================================================

def fetch_socrata_data(resource_url, limit=50000):
    """Fetch data from Austin Open Data Portal via Socrata API"""
    params = {"$limit": limit}
    response = requests.get(resource_url, params=params)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")


def fetch_arcgis_features(query_url, where="1=1", out_fields="*", out_sr=4326):
    """Fetch features from ArcGIS REST API as GeoJSON"""
    params = {
        "where": where,
        "outFields": out_fields,
        "outSR": out_sr,
        "f": "geojson"
    }
    response = requests.get(query_url, params=params)
    if response.status_code == 200:
        return gpd.GeoDataFrame.from_features(response.json()["features"])
    else:
        raise Exception(f"Failed to fetch ArcGIS data: {response.status_code}")


def fetch_census_data(table, variables, state="48", county="453"):
    """
    Fetch Census ACS data for Travis County, TX
    State FIPS: 48 (Texas)
    County FIPS: 453 (Travis County)
    """
    base_url = f"https://api.census.gov/data/2022/acs/acs5"
    
    # Build variable list
    var_string = ",".join(variables)
    
    # Query at tract level for Travis County
    url = f"{base_url}?get={var_string}&for=tract:*&in=state:{state}&in=county:{county}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0])
        return df
    else:
        raise Exception(f"Census API error: {response.status_code}")


# =============================================================================
# DATA PROCESSING FUNCTIONS
# =============================================================================

def parse_incident_locations(df, location_col="location"):
    """Convert location strings to Point geometries"""
    def parse_loc(loc_str):
        if pd.isna(loc_str):
            return None
        try:
            # Format: "(-97.xxx, 30.xxx)"
            coords = loc_str.strip("()").split(",")
            lon, lat = float(coords[0]), float(coords[1])
            return Point(lon, lat)
        except:
            return None
    
    df["geometry"] = df[location_col].apply(parse_loc)
    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")


def classify_urban_suburban(gdf, density_col="pop_density"):
    """
    Classify areas as urban core, inner suburban, or outer suburban
    Based on population density thresholds (people per sq mile)
    """
    def classify(density):
        if density >= 10000:
            return "urban_core"
        elif density >= 3000:
            return "inner_suburban"
        else:
            return "outer_suburban"
    
    gdf["urban_class"] = gdf[density_col].apply(classify)
    return gdf


def calculate_housing_typology_mix(census_df):
    """
    Calculate housing mix from Census B25024 (Units in Structure)
    
    B25024_002E: 1, detached
    B25024_003E: 1, attached
    B25024_004E: 2 units
    B25024_005E: 3 or 4 units
    B25024_006E: 5 to 9 units
    B25024_007E: 10 to 19 units
    B25024_008E: 20 to 49 units
    B25024_009E: 50 or more units
    B25024_010E: Mobile home
    B25024_011E: Boat, RV, van, etc.
    """
    df = census_df.copy()
    
    # Convert to numeric
    numeric_cols = [c for c in df.columns if c.startswith("B25024")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Calculate categories
    df["single_family"] = df["B25024_002E"] + df["B25024_003E"]
    df["small_multifamily"] = df["B25024_004E"] + df["B25024_005E"]  # 2-4 units
    df["medium_multifamily"] = df["B25024_006E"] + df["B25024_007E"]  # 5-19 units
    df["large_multifamily"] = df["B25024_008E"] + df["B25024_009E"]   # 20+ units
    df["other"] = df["B25024_010E"] + df["B25024_011E"]
    
    df["total_units"] = df["B25024_001E"]
    
    # Calculate percentages
    df["pct_single_family"] = df["single_family"] / df["total_units"] * 100
    df["pct_multifamily"] = (df["small_multifamily"] + df["medium_multifamily"] + 
                            df["large_multifamily"]) / df["total_units"] * 100
    
    return df


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def calculate_incidents_per_capita(incidents_gdf, response_areas_gdf, population_df):
    """
    Spatial join incidents to response areas, then calculate per-capita rates
    """
    # Spatial join: which response area does each incident fall in?
    incidents_with_area = gpd.sjoin(
        incidents_gdf, 
        response_areas_gdf, 
        how="left", 
        predicate="within"
    )
    
    # Aggregate incidents by response area
    incident_counts = incidents_with_area.groupby("response_area_id").size()
    incident_counts = incident_counts.reset_index(name="incident_count")
    
    # Merge with population
    merged = response_areas_gdf.merge(incident_counts, on="response_area_id", how="left")
    merged = merged.merge(population_df, on="response_area_id", how="left")
    
    # Calculate rate per 1,000 population
    merged["incidents_per_1000"] = (merged["incident_count"] / merged["population"]) * 1000
    
    return merged


def analyze_by_urban_class(merged_gdf):
    """Aggregate metrics by urban classification"""
    summary = merged_gdf.groupby("urban_class").agg({
        "population": "sum",
        "incident_count": "sum",
        "total_units": "sum",
        "single_family": "sum",
        "area_sq_miles": "sum"
    }).reset_index()
    
    # Calculate per-capita metrics
    summary["incidents_per_1000_pop"] = (summary["incident_count"] / summary["population"]) * 1000
    summary["incidents_per_1000_units"] = (summary["incident_count"] / summary["total_units"]) * 1000
    summary["pop_density"] = summary["population"] / summary["area_sq_miles"]
    summary["pct_single_family"] = summary["single_family"] / summary["total_units"] * 100
    
    return summary


def analyze_by_housing_type(merged_gdf):
    """
    Correlate fire incident rates with housing typology
    """
    # Create bins for single-family percentage
    merged_gdf["sf_category"] = pd.cut(
        merged_gdf["pct_single_family"],
        bins=[0, 25, 50, 75, 100],
        labels=["<25% SF", "25-50% SF", "50-75% SF", ">75% SF"]
    )
    
    summary = merged_gdf.groupby("sf_category").agg({
        "incidents_per_1000": "mean",
        "population": "sum",
        "incident_count": "sum"
    }).reset_index()
    
    return summary


# =============================================================================
# MAIN ANALYSIS PIPELINE
# =============================================================================

def run_full_analysis():
    """
    Execute the complete analysis pipeline
    """
    print("=" * 60)
    print("AUSTIN FIRE RESOURCE ALLOCATION ANALYSIS")
    print("=" * 60)
    
    # Step 1: Fetch fire incidents
    print("\n[1/6] Fetching fire incident data...")
    incidents_recent = fetch_socrata_data(SOURCES["fire_incidents_2022_2024"]["url"])
    print(f"      Retrieved {len(incidents_recent)} incidents (2022-2024)")
    
    # Step 2: Fetch response area boundaries
    print("\n[2/6] Fetching AFD response area boundaries...")
    response_areas = fetch_arcgis_features(
        SOURCES["afd_response_areas"]["query_url"]
    )
    print(f"      Retrieved {len(response_areas)} response areas")
    
    # Step 3: Fetch census data
    print("\n[3/6] Fetching Census population data...")
    pop_vars = ["B01003_001E", "NAME"]
    population = fetch_census_data("B01003", pop_vars)
    print(f"      Retrieved population for {len(population)} tracts")
    
    print("\n[4/6] Fetching Census housing typology data...")
    housing_vars = [f"B25024_{str(i).zfill(3)}E" for i in range(1, 12)] + ["NAME"]
    housing = fetch_census_data("B25024", housing_vars)
    housing = calculate_housing_typology_mix(housing)
    print(f"      Retrieved housing data for {len(housing)} tracts")
    
    # Step 4: Process incident locations
    print("\n[5/6] Processing incident locations...")
    incidents_gdf = parse_incident_locations(incidents_recent)
    valid_locations = incidents_gdf.geometry.notna().sum()
    print(f"      {valid_locations} incidents with valid coordinates")
    
    # Step 5: Spatial analysis
    print("\n[6/6] Performing spatial analysis...")
    # (This would require more work to spatially join census tracts to response areas)
    
    print("\n" + "=" * 60)
    print("DATA RETRIEVAL COMPLETE")
    print("=" * 60)
    
    return {
        "incidents": incidents_gdf,
        "response_areas": response_areas,
        "population": population,
        "housing": housing
    }


# =============================================================================
# VISUALIZATION HELPERS
# =============================================================================

def create_choropleth_map(gdf, column, title):
    """Create a folium choropleth map (requires folium)"""
    try:
        import folium
        
        m = folium.Map(location=[30.2672, -97.7431], zoom_start=11)
        
        folium.Choropleth(
            geo_data=gdf.__geo_interface__,
            data=gdf,
            columns=["response_area_id", column],
            key_on="feature.properties.response_area_id",
            fill_color="YlOrRd",
            legend_name=title
        ).add_to(m)
        
        return m
    except ImportError:
        print("Install folium for map visualization: pip install folium")
        return None


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Run the analysis
    data = run_full_analysis()
    
    # Print sample of incident types
    if "incidents" in data:
        print("\n--- Fire Incident Types (sample) ---")
        print(data["incidents"]["problem"].value_counts().head(15))
    
    # Print housing mix summary  
    if "housing" in data:
        print("\n--- Housing Typology Summary ---")
        housing = data["housing"]
        print(f"Total units in Travis County: {housing['total_units'].sum():,.0f}")
        print(f"Single-family: {housing['single_family'].sum():,.0f}")
        print(f"Multifamily: {(housing['small_multifamily'].sum() + housing['medium_multifamily'].sum() + housing['large_multifamily'].sum()):,.0f}")
