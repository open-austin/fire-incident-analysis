#!/usr/bin/env python3
"""
Step 3: Create Spatial Crosswalk
=================================
Creates a simple crosswalk between census tracts and AFD response incidents using the recorded lat/long.
For boundary incidents (points touching multiple tracts), all touching tracts are stored in an array.

Input:
    raw_data/tl_2023_48_tract.shp (or similar census tract shapefile for Austin-area counties)
    raw_data/census_population.csv
    raw_data/census_housing.csv
    raw_data/census_year_built.csv

Output:
    processed_data/incident_to_tract_crosswalk.csv
"""

import pandas as pd
import geopandas as gpd

def join_census_to_incidents(incident_data_path, tract_shapefile_path, output_path):
    # Load incident data
    incidents = pd.read_csv(incident_data_path)
    incidents = incidents[incidents['is_structure_fire'] == True]  # All structure fires (confined + non-confined)
    
    # Removing unneeded columns
    incidents.drop(columns=['call_type','prioritydescription','jurisdiction','is_structure_fire','is_nonconfined_structure_fire','is_confined_structure_fire','is_vehicle_fire','is_outdoor_fire','is_trash_fire','incident_category'], inplace=True, errors='ignore')
    
    # Cleaning out missing lat/long values
    incidents_clean = incidents.dropna(subset=['latitude', 'longitude']).reset_index(drop=True)

    print("Mapping incidents to census tracts using lat/long coordinates...")
    print(f"Number of structure fire incidents without lat/long: {len(incidents) - len(incidents_clean)}")
    print(f"Number of structure fire incidents after cleaning: {len(incidents_clean)}")

    # Load census tract shapefile
    tracts = gpd.read_file(tract_shapefile_path)
    
    # Ensure the coordinate reference systems match
    tracts = tracts.to_crs(epsg=4326)  # WGS 84
    tracts = tracts.rename(columns={'NAME': 'Census Tract', 'TRACTCE': 'Tract Code'})


    incidents_gdf = gpd.GeoDataFrame(
        incidents_clean, 
        geometry=gpd.points_from_xy(incidents_clean['longitude'], incidents_clean['latitude']),
        crs='EPSG:4326'
    )
    
    # For each incident, find all census tracts it touches (including boundary tracts)
    tract_arrays = []
    tract_code_arrays = []
    boundary_count = 0
    
    for idx, incident in incidents_gdf.iterrows():
        point = incident.geometry
        
        # Find all tracts that touch this point (within or on boundary)
        touching_tracts = tracts[tracts.geometry.touches(point) | tracts.geometry.contains(point)]
        
        if len(touching_tracts) > 0:
            tract_list = touching_tracts['Census Tract'].tolist()
            tract_code_list = touching_tracts['Tract Code'].tolist()
            if len(tract_list) > 1:
                boundary_count += 1
        else:
            tract_list = [None]
            tract_code_list = [None]
        
        tract_arrays.append(tract_list)
        tract_code_arrays.append(tract_code_list)
    
    # Add the tract array to the dataframe
    incidents_gdf['census_tracts'] = tract_arrays
    incidents_gdf['tract_codes'] = tract_code_arrays
    
    # Select relevant columns
    output_cols = incidents.columns.to_list() + ['census_tracts', 'tract_codes']
    result_gdf = incidents_gdf[output_cols].copy()
    
    # Count incidents with tract assignments
    has_tract = result_gdf['census_tracts'].apply(lambda x: x != [None])
    print(f"\nIncidents with tract assignment: {has_tract.sum()} / {len(result_gdf)}")
    print(f"Boundary incidents (touching multiple tracts): {boundary_count}")
    
    # Save the results to CSV
    result_gdf.to_csv(output_path, index=False)
    print(f"\nSpatial join complete. Output saved to: {output_path}")
    print(f"Size of output dataset: {len(result_gdf)}")


if __name__ == "__main__":
    incident_data_path = 'processed_data/incidents_clean.csv'
    tract_shapefile_path = 'raw_data/tl_2023_48_tract.shp'  # Update with actual path to census tract shapefile
    output_path = 'processed_data/sf_incidents_with_tracts.csv'
    
    join_census_to_incidents(incident_data_path, tract_shapefile_path, output_path)