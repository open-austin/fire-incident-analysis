#!/usr/bin/env python3
"""
Step 5: Visualization
======================
Creates maps and charts for the fire resource analysis.

Usage:
    python scripts/05_visualize.py

Input:
    processed_data/response_areas_final.geojson
    outputs/summary_by_urban_class.csv
    outputs/summary_by_housing_type.csv

Output:
    outputs/map_incidents_per_capita.html
    outputs/map_urban_classification.html
    outputs/map_housing_typology.html
    outputs/map_building_age.html
    outputs/map_fire_stations.html
    outputs/chart_urban_comparison.png
    outputs/chart_housing_correlation.png
    outputs/chart_incident_types.png
    outputs/chart_building_age.png
    outputs/chart_time_series.png
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# Try to import folium for interactive maps
try:
    import folium
    from folium import plugins
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    print("Note: Install folium for interactive maps: pip install folium")


def load_data():
    """Load processed data"""
    print("\nLoading data...")
    
    ra = gpd.read_file("processed_data/response_areas_final.geojson")
    print(f"  Response areas: {len(ra)}")
    
    summary_urban = pd.read_csv("outputs/summary_by_urban_class.csv")
    summary_housing = pd.read_csv("outputs/summary_by_housing_type.csv")
    
    return ra, summary_urban, summary_housing


def create_choropleth_map(gdf, column, title, filename, colormap='YlOrRd'):
    """Create an interactive choropleth map with folium"""
    if not HAS_FOLIUM:
        print(f"  Skipping {filename} (folium not installed)")
        return
    
    print(f"  Creating: {filename}")
    
    # Center on Austin
    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='cartodbpositron')
    
    # Filter out invalid values
    valid_gdf = gdf[gdf[column].notna() & (gdf[column] > 0)].copy()
    
    if len(valid_gdf) == 0:
        print(f"    Warning: No valid data for {column}")
        return
    
    # Create choropleth
    folium.Choropleth(
        geo_data=valid_gdf.__geo_interface__,
        data=valid_gdf,
        columns=['response_area_id', column],
        key_on='feature.properties.response_area_id',
        fill_color=colormap,
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=title,
        nan_fill_color='white'
    ).add_to(m)
    
    # Add tooltips
    style_function = lambda x: {'fillColor': '#ffffff', 'color': '#000000', 'fillOpacity': 0, 'weight': 0.1}
    highlight_function = lambda x: {'fillColor': '#000000', 'color': '#000000', 'fillOpacity': 0.3, 'weight': 1}
    
    tooltip = folium.GeoJsonTooltip(
        fields=['response_area_id', column, 'population', 'urban_class'],
        aliases=['Response Area:', f'{title}:', 'Population:', 'Classification:'],
        localize=True
    )
    
    folium.GeoJson(
        valid_gdf,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=tooltip
    ).add_to(m)
    
    m.save(f"outputs/{filename}")
    print(f"    ✓ Saved: outputs/{filename}")


def create_categorical_map(gdf, column, title, filename, colors=None):
    """Create a categorical choropleth map"""
    if not HAS_FOLIUM:
        print(f"  Skipping {filename} (folium not installed)")
        return
    
    print(f"  Creating: {filename}")
    
    # Center on Austin
    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='cartodbpositron')
    
    # Default colors
    if colors is None:
        colors = {
            'urban_core': '#d62728',       # Red
            'inner_suburban': '#ff7f0e',   # Orange
            'outer_suburban': '#2ca02c',   # Green
            'unknown': '#7f7f7f'           # Gray
        }
    
    # Style function
    def style_function(feature):
        category = feature['properties'].get(column, 'unknown')
        return {
            'fillColor': colors.get(category, '#7f7f7f'),
            'color': '#000000',
            'weight': 0.5,
            'fillOpacity': 0.7
        }
    
    # Add GeoJson layer
    tooltip = folium.GeoJsonTooltip(
        fields=['response_area_id', column, 'population', 'incidents_per_1000_pop'],
        aliases=['Response Area:', 'Classification:', 'Population:', 'Incidents/1000:'],
        localize=True
    )
    
    folium.GeoJson(
        gdf,
        style_function=style_function,
        tooltip=tooltip
    ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                background-color: white; padding: 10px; border: 2px solid grey;
                border-radius: 5px; font-size: 14px;">
    <p><strong>Urban Classification</strong></p>
    <p><span style="background-color: #d62728; padding: 2px 10px;"></span> Urban Core</p>
    <p><span style="background-color: #ff7f0e; padding: 2px 10px;"></span> Inner Suburban</p>
    <p><span style="background-color: #2ca02c; padding: 2px 10px;"></span> Outer Suburban</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    m.save(f"outputs/{filename}")
    print(f"    ✓ Saved: outputs/{filename}")


def create_bar_chart(summary_df, filename):
    """Create bar chart comparing incident rates by urban classification"""
    print(f"  Creating: {filename}")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Order categories
    order = ['urban_core', 'inner_suburban', 'outer_suburban']
    summary_df['urban_class'] = pd.Categorical(summary_df['urban_class'], categories=order, ordered=True)
    summary_df = summary_df.sort_values('urban_class')
    
    # Labels
    labels = {
        'urban_core': 'Urban Core\n(>10k/sq mi)',
        'inner_suburban': 'Inner Suburban\n(3-10k/sq mi)',
        'outer_suburban': 'Outer Suburban\n(<3k/sq mi)'
    }
    x_labels = [labels.get(c, c) for c in summary_df['urban_class']]
    
    # Colors
    colors = ['#d62728', '#ff7f0e', '#2ca02c']
    
    # Plot 1: Incidents per 1,000 population
    ax1 = axes[0]
    bars1 = ax1.bar(x_labels, summary_df['incidents_per_1000_pop'], color=colors, edgecolor='black')
    ax1.set_ylabel('Fire Incidents per 1,000 Population', fontsize=12)
    ax1.set_title('Per-Capita Fire Incident Rate', fontsize=14, fontweight='bold')
    ax1.tick_params(axis='x', rotation=0)
    
    # Add value labels
    for bar, val in zip(bars1, summary_df['incidents_per_1000_pop']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Plot 2: % Single-Family Housing
    ax2 = axes[1]
    bars2 = ax2.bar(x_labels, summary_df['pct_single_family'], color=colors, edgecolor='black')
    ax2.set_ylabel('% Single-Family Housing', fontsize=12)
    ax2.set_title('Housing Typology', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='x', rotation=0)
    
    # Add value labels
    for bar, val in zip(bars2, summary_df['pct_single_family']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.0f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_scatter_plot(gdf, filename):
    """Create scatter plot of % single-family vs incident rate"""
    print(f"  Creating: {filename}")
    
    # Filter to valid data
    valid = gdf[
        (gdf['population'] > 100) &
        (gdf['pct_single_family'].notna()) &
        (gdf['incidents_per_1000_pop'].notna()) &
        (gdf['urban_class'] != 'unknown')
    ].copy()
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Color by urban class
    colors = {
        'urban_core': '#d62728',
        'inner_suburban': '#ff7f0e',
        'outer_suburban': '#2ca02c'
    }
    
    for urban_class, color in colors.items():
        subset = valid[valid['urban_class'] == urban_class]
        ax.scatter(
            subset['pct_single_family'],
            subset['incidents_per_1000_pop'],
            c=color,
            label=urban_class.replace('_', ' ').title(),
            alpha=0.6,
            s=subset['population'] / 100,  # Size by population
            edgecolors='black',
            linewidth=0.5
        )
    
    # Add trend line
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        valid['pct_single_family'],
        valid['incidents_per_1000_pop']
    )
    
    x_line = [0, 100]
    y_line = [intercept, intercept + slope * 100]
    ax.plot(x_line, y_line, 'k--', alpha=0.5, label=f'Trend (r={r_value:.2f})')
    
    ax.set_xlabel('% Single-Family Housing', fontsize=12)
    ax.set_ylabel('Fire Incidents per 1,000 Population', fontsize=12)
    ax.set_title('Fire Incident Rate vs Housing Typology\n(bubble size = population)', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_xlim(-5, 105)
    ax.set_ylim(bottom=0)
    
    # Add correlation annotation
    ax.annotate(
        f'Correlation: r = {r_value:.3f}\np-value = {p_value:.4f}',
        xy=(0.95, 0.95),
        xycoords='axes fraction',
        ha='right',
        va='top',
        fontsize=11,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )
    
    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_summary_table_image(summary_df, filename):
    """Create a formatted summary table as an image"""
    print(f"  Creating: {filename}")
    
    # Select and rename columns for display
    display_cols = {
        'urban_class': 'Classification',
        'population': 'Population',
        'total_incidents': 'Total Incidents',
        'incidents_per_1000_pop': 'Rate per 1,000 Pop',
        'pct_single_family': '% Single-Family'
    }
    
    table_df = summary_df[[c for c in display_cols.keys() if c in summary_df.columns]].copy()
    table_df.columns = [display_cols[c] for c in table_df.columns]
    
    # Format numbers
    if 'Population' in table_df.columns:
        table_df['Population'] = table_df['Population'].apply(lambda x: f'{x:,.0f}')
    if 'Total Incidents' in table_df.columns:
        table_df['Total Incidents'] = table_df['Total Incidents'].apply(lambda x: f'{x:,.0f}')
    if 'Rate per 1,000 Pop' in table_df.columns:
        table_df['Rate per 1,000 Pop'] = table_df['Rate per 1,000 Pop'].apply(lambda x: f'{x:.2f}')
    if '% Single-Family' in table_df.columns:
        table_df['% Single-Family'] = table_df['% Single-Family'].apply(lambda x: f'{x:.1f}%')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.axis('off')
    
    table = ax.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        cellLoc='center',
        loc='center',
        colColours=['#f0f0f0'] * len(table_df.columns)
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    
    plt.title('Fire Incident Rates by Urban Classification', fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_incident_type_chart(filename):
    """Create grouped bar chart of incident rates by type × urban class with yearly breakdown"""
    print(f"  Creating: {filename}")

    # Load incident type summary
    if not os.path.exists("outputs/summary_by_incident_type.csv"):
        print(f"    Warning: summary_by_incident_type.csv not found")
        return

    df = pd.read_csv("outputs/summary_by_incident_type.csv")

    # Prepare data
    incident_types = ['structure', 'vehicle', 'outdoor', 'trash', 'other']
    urban_classes = ['urban_core', 'inner_suburban', 'outer_suburban']
    labels = ['Urban Core', 'Inner Suburban', 'Outer Suburban']

    fig, ax = plt.subplots(figsize=(12, 6))

    x = range(len(incident_types))
    width = 0.25
    colors = ['#d62728', '#ff7f0e', '#2ca02c']

    for i, (uc, label, color) in enumerate(zip(urban_classes, labels, colors)):
        row = df[df['urban_class'] == uc]
        if len(row) > 0:
            rates = [row[f'{t}_per_1000'].values[0] for t in incident_types]
            bars = ax.bar([xi + i*width for xi in x], rates, width, label=label, color=color, edgecolor='black')

    ax.set_xlabel('Incident Type', fontsize=12)
    ax.set_ylabel('Incidents per 1,000 Population', fontsize=12)
    ax.set_title('Fire Incident Rates by Type and Urban Classification', fontsize=14, fontweight='bold')
    ax.set_xticks([xi + width for xi in x])
    ax.set_xticklabels(['Structure', 'Vehicle', 'Outdoor', 'Trash/Dumpster', 'Other'])
    ax.legend()

    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_incident_type_chart_yearly(filename):
    """Create grouped bar chart with yearly sub-colors showing 2022, 2023, 2024 breakdown"""
    print(f"  Creating: {filename}")

    # Load incidents data to get yearly breakdown
    if not os.path.exists("processed_data/incidents_clean.csv"):
        print(f"    Warning: incidents_clean.csv not found")
        return

    incidents = pd.read_csv("processed_data/incidents_clean.csv")
    ra_demo = gpd.read_file("processed_data/response_areas_final.geojson")

    # Join incidents with urban class
    incidents['response_area_id'] = incidents['responsearea'].astype(str)
    ra_demo['response_area_id'] = ra_demo['response_area_id'].astype(str)

    incidents = incidents.merge(
        ra_demo[['response_area_id', 'urban_class', 'population']],
        on='response_area_id', how='left'
    )

    # Filter valid
    incidents = incidents[incidents['urban_class'].isin(['urban_core', 'inner_suburban', 'outer_suburban'])]

    # Get population by urban class
    pop_by_class = ra_demo[ra_demo['urban_class'] != 'unknown'].groupby('urban_class')['population'].sum()

    # Count by year, urban class, and type
    years = [2022, 2023, 2024]
    urban_classes = ['urban_core', 'inner_suburban', 'outer_suburban']
    incident_types = ['is_structure_fire', 'is_vehicle_fire', 'is_outdoor_fire', 'is_trash_fire']
    type_labels = ['Structure', 'Vehicle', 'Outdoor', 'Trash']

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    year_colors = ['#1f77b4', '#2ca02c', '#ff7f0e']  # Blue=2022, Green=2023, Orange=2024
    year_labels = ['2022', '2023', '2024']

    for ax_idx, (uc, uc_label) in enumerate(zip(urban_classes, ['Urban Core', 'Inner Suburban', 'Outer Suburban'])):
        ax = axes[ax_idx]
        uc_data = incidents[incidents['urban_class'] == uc]
        pop = pop_by_class.get(uc, 1)

        x = range(len(incident_types))
        width = 0.25

        for yi, (year, year_color, year_label) in enumerate(zip(years, year_colors, year_labels)):
            year_data = uc_data[uc_data['calendaryear'] == year]
            rates = [(year_data[t].sum() / pop) * 1000 for t in incident_types]
            ax.bar([xi + yi*width for xi in x], rates, width, label=year_label if ax_idx == 0 else '',
                   color=year_color, edgecolor='black', alpha=0.8)

        ax.set_xlabel('Incident Type', fontsize=11)
        ax.set_title(uc_label, fontsize=12, fontweight='bold')
        ax.set_xticks([xi + width for xi in x])
        ax.set_xticklabels(type_labels, rotation=30, ha='right')

    axes[0].set_ylabel('Incidents per 1,000 Pop', fontsize=11)
    axes[0].legend(title='Year', loc='upper right')

    fig.suptitle('Fire Incident Rates by Type, Urban Class, and Year', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_building_age_chart(filename):
    """Create bar chart comparing incident rates by building age"""
    print(f"  Creating: {filename}")

    # Load building age summary
    if not os.path.exists("outputs/summary_by_building_age.csv"):
        print(f"    Warning: summary_by_building_age.csv not found")
        return

    df = pd.read_csv("outputs/summary_by_building_age.csv")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Chart 1: Incidents per 1,000 population
    ax1 = axes[0]
    colors = ['#2ca02c', '#d62728']  # Green for newer, red for older
    bars1 = ax1.bar(df['building_age'], df['incidents_per_1000_pop'], color=colors, edgecolor='black')
    ax1.set_ylabel('Incidents per 1,000 Population', fontsize=12)
    ax1.set_title('Total Incident Rate by Building Age', fontsize=14, fontweight='bold')
    ax1.tick_params(axis='x', rotation=15)

    for bar, val in zip(bars1, df['incidents_per_1000_pop']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f'{val:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Chart 2: Structure fires per 1,000 units
    ax2 = axes[1]
    bars2 = ax2.bar(df['building_age'], df['structure_per_1000_units'], color=colors, edgecolor='black')
    ax2.set_ylabel('Structure Fires per 1,000 Housing Units', fontsize=12)
    ax2.set_title('Structure Fire Rate by Building Age', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='x', rotation=15)

    for bar, val in zip(bars2, df['structure_per_1000_units']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{val:.2f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_building_age_chart_yearly(filename):
    """Create building age chart with yearly sub-colors showing 2022, 2023, 2024 breakdown"""
    print(f"  Creating: {filename}")

    # Load incidents data
    if not os.path.exists("processed_data/incidents_clean.csv"):
        print(f"    Warning: incidents_clean.csv not found")
        return

    incidents = pd.read_csv("processed_data/incidents_clean.csv")
    ra_demo = gpd.read_file("processed_data/response_areas_final.geojson")

    # Check for building age data
    if 'pct_built_2010_plus' not in ra_demo.columns:
        print(f"    Warning: building age data not available")
        return

    # Join incidents with response area data
    incidents['response_area_id'] = incidents['responsearea'].astype(str)
    ra_demo['response_area_id'] = ra_demo['response_area_id'].astype(str)

    incidents = incidents.merge(
        ra_demo[['response_area_id', 'pct_built_2010_plus', 'population']],
        on='response_area_id', how='left'
    )

    # Classify areas by building age
    incidents = incidents[incidents['pct_built_2010_plus'].notna()]
    incidents['age_class'] = incidents['pct_built_2010_plus'].apply(
        lambda x: 'Newer (50%+ post-2010)' if x >= 50 else 'Older (<50% post-2010)'
    )

    # Get population by age class
    ra_demo['age_class'] = ra_demo['pct_built_2010_plus'].apply(
        lambda x: 'Newer (50%+ post-2010)' if pd.notna(x) and x >= 50 else 'Older (<50% post-2010)'
    )
    pop_by_age = ra_demo.groupby('age_class')['population'].sum()

    years = [2022, 2023, 2024]
    age_classes = ['Newer (50%+ post-2010)', 'Older (<50% post-2010)']
    year_colors = ['#1f77b4', '#2ca02c', '#ff7f0e']  # Blue=2022, Green=2023, Orange=2024
    year_labels = ['2022', '2023', '2024']

    fig, ax = plt.subplots(figsize=(10, 6))

    x = range(len(age_classes))
    width = 0.25

    for yi, (year, year_color, year_label) in enumerate(zip(years, year_colors, year_labels)):
        rates = []
        for ac in age_classes:
            year_ac_data = incidents[(incidents['calendaryear'] == year) & (incidents['age_class'] == ac)]
            pop = pop_by_age.get(ac, 1)
            rate = (len(year_ac_data) / pop) * 1000
            rates.append(rate)
        ax.bar([xi + yi*width for xi in x], rates, width, label=year_label,
               color=year_color, edgecolor='black', alpha=0.8)

    ax.set_xlabel('Building Age Classification', fontsize=12)
    ax.set_ylabel('Incidents per 1,000 Population', fontsize=12)
    ax.set_title('Fire Incident Rates by Building Age and Year', fontsize=14, fontweight='bold')
    ax.set_xticks([xi + width for xi in x])
    ax.set_xticklabels(age_classes)
    ax.legend(title='Year', loc='upper right')

    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_urban_comparison_yearly(filename):
    """Create urban comparison chart with yearly sub-colors showing 2022, 2023, 2024 breakdown"""
    print(f"  Creating: {filename}")

    # Load incidents data
    if not os.path.exists("processed_data/incidents_clean.csv"):
        print(f"    Warning: incidents_clean.csv not found")
        return

    incidents = pd.read_csv("processed_data/incidents_clean.csv")
    ra_demo = gpd.read_file("processed_data/response_areas_final.geojson")

    # Join incidents with urban class
    incidents['response_area_id'] = incidents['responsearea'].astype(str)
    ra_demo['response_area_id'] = ra_demo['response_area_id'].astype(str)

    incidents = incidents.merge(
        ra_demo[['response_area_id', 'urban_class', 'population']],
        on='response_area_id', how='left'
    )

    # Filter valid
    urban_classes = ['urban_core', 'inner_suburban', 'outer_suburban']
    incidents = incidents[incidents['urban_class'].isin(urban_classes)]

    # Get population by urban class
    pop_by_class = ra_demo[ra_demo['urban_class'].isin(urban_classes)].groupby('urban_class')['population'].sum()

    years = [2022, 2023, 2024]
    year_colors = ['#1f77b4', '#2ca02c', '#ff7f0e']  # Blue=2022, Green=2023, Orange=2024
    year_labels = ['2022', '2023', '2024']
    uc_labels = ['Urban Core\n(>10k/sq mi)', 'Inner Suburban\n(3-10k/sq mi)', 'Outer Suburban\n(<3k/sq mi)']

    fig, ax = plt.subplots(figsize=(10, 6))

    x = range(len(urban_classes))
    width = 0.25

    for yi, (year, year_color, year_label) in enumerate(zip(years, year_colors, year_labels)):
        rates = []
        for uc in urban_classes:
            year_uc_data = incidents[(incidents['calendaryear'] == year) & (incidents['urban_class'] == uc)]
            pop = pop_by_class.get(uc, 1)
            rate = (len(year_uc_data) / pop) * 1000
            rates.append(rate)
        ax.bar([xi + yi*width for xi in x], rates, width, label=year_label,
               color=year_color, edgecolor='black', alpha=0.8)

    ax.set_xlabel('Urban Classification', fontsize=12)
    ax.set_ylabel('Incidents per 1,000 Population', fontsize=12)
    ax.set_title('Fire Incident Rates by Urban Class and Year', fontsize=14, fontweight='bold')
    ax.set_xticks([xi + width for xi in x])
    ax.set_xticklabels(uc_labels)
    ax.legend(title='Year', loc='upper right')

    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_incident_type_by_building_age_chart(filename):
    """Create grouped bar chart of incident types by building age"""
    print(f"  Creating: {filename}")

    # Load and process data
    incidents = pd.read_csv("processed_data/incidents_clean.csv")
    ra = gpd.read_file("processed_data/response_areas_final.geojson")

    if 'pct_built_2010_plus' not in ra.columns:
        print(f"    Warning: building age data not available")
        return

    # Join
    incidents['response_area_id'] = incidents['responsearea'].astype(str)
    ra['response_area_id'] = ra['response_area_id'].astype(str)
    incidents = incidents.merge(
        ra[['response_area_id', 'pct_built_2010_plus', 'total_units']],
        on='response_area_id', how='left'
    )
    incidents = incidents[incidents['pct_built_2010_plus'].notna()]

    # Classify
    incidents['age_class'] = incidents['pct_built_2010_plus'].apply(
        lambda x: 'Newer\n(50%+ post-2010)' if x >= 50 else 'Older\n(<50% post-2010)'
    )
    ra['age_class'] = ra['pct_built_2010_plus'].apply(
        lambda x: 'Newer\n(50%+ post-2010)' if pd.notna(x) and x >= 50 else 'Older\n(<50% post-2010)'
    )
    units_by_age = ra.groupby('age_class')['total_units'].sum()

    # Calculate rates
    incident_types = ['is_structure_fire', 'is_vehicle_fire', 'is_outdoor_fire', 'is_trash_fire']
    type_labels = ['Structure\nFire', 'Vehicle\nFire', 'Outdoor/\nVegetation', 'Trash/\nDumpster']
    age_classes = ['Newer\n(50%+ post-2010)', 'Older\n(<50% post-2010)']

    fig, ax = plt.subplots(figsize=(12, 6))

    x = range(len(incident_types))
    width = 0.35
    colors = ['#2ca02c', '#d62728']  # Green=newer, Red=older

    for ai, (age, color) in enumerate(zip(age_classes, colors)):
        age_data = incidents[incidents['age_class'] == age]
        units = units_by_age.get(age, 1)
        rates = [(age_data[it].sum() / units) * 1000 for it in incident_types]
        bars = ax.bar([xi + ai*width for xi in x], rates, width, label=age.replace('\n', ' '),
                      color=color, edgecolor='black', alpha=0.85)
        for bar, rate in zip(bars, rates):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                   f'{rate:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xlabel('Incident Type', fontsize=12)
    ax.set_ylabel('Incidents per 1,000 Housing Units', fontsize=12)
    ax.set_title('Fire Incident Rates by Type and Building Age\n(2006 Austin sprinkler code effect visible in structure fires)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks([xi + width/2 for xi in x])
    ax.set_xticklabels(type_labels)
    ax.legend(title='Building Age', loc='upper left')
    ax.set_ylim(bottom=0)

    # Add annotation for sprinkler code effect
    ax.annotate('141% higher\nin older buildings',
                xy=(0.17, 5.62), xytext=(0.5, 8),
                fontsize=10, ha='center',
                arrowprops=dict(arrowstyle='->', color='black'),
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_structure_fire_housing_trend_chart(filename):
    """Create grouped bar chart of structure fires by housing type and year"""
    print(f"  Creating: {filename}")

    if not os.path.exists("outputs/structure_fires_by_housing_trend.csv"):
        print(f"    Warning: structure_fires_by_housing_trend.csv not found")
        return

    df = pd.read_csv("outputs/structure_fires_by_housing_trend.csv")

    fig, ax = plt.subplots(figsize=(12, 6))

    housing_types = df['housing_type'].unique()
    years = sorted(df['year'].unique())
    year_colors = ['#1f77b4', '#2ca02c', '#ff7f0e']  # Blue, Green, Orange

    x = range(len(housing_types))
    width = 0.25

    for yi, (year, color) in enumerate(zip(years, year_colors)):
        year_data = df[df['year'] == year].set_index('housing_type')
        rates = [year_data.loc[ht, 'fires_per_1000_units'] if ht in year_data.index else 0
                 for ht in housing_types]
        bars = ax.bar([xi + yi*width for xi in x], rates, width, label=str(year),
                      color=color, edgecolor='black', alpha=0.85)
        # Add value labels
        for bar, rate in zip(bars, rates):
            if rate > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                       f'{rate:.2f}', ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('Housing Type', fontsize=12)
    ax.set_ylabel('Structure Fires per 1,000 Housing Units', fontsize=12)
    ax.set_title('Structure Fire Rates by Housing Type and Year\n(Housing fires only - excludes vehicle, trash, outdoor)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks([xi + width for xi in x])
    ax.set_xticklabels(housing_types, rotation=15, ha='right')
    ax.legend(title='Year', loc='upper right')
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_structure_fire_urban_trend_chart(filename):
    """Create grouped bar chart of structure fires by urban class and year"""
    print(f"  Creating: {filename}")

    if not os.path.exists("outputs/structure_fires_by_urban_trend.csv"):
        print(f"    Warning: structure_fires_by_urban_trend.csv not found")
        return

    df = pd.read_csv("outputs/structure_fires_by_urban_trend.csv")

    fig, ax = plt.subplots(figsize=(10, 6))

    urban_classes = ['urban_core', 'inner_suburban', 'outer_suburban']
    urban_labels = ['Urban Core\n(>10k/sq mi)', 'Inner Suburban\n(3-10k/sq mi)', 'Outer Suburban\n(<3k/sq mi)']
    years = sorted(df['year'].unique())
    year_colors = ['#1f77b4', '#2ca02c', '#ff7f0e']

    x = range(len(urban_classes))
    width = 0.25

    for yi, (year, color) in enumerate(zip(years, year_colors)):
        year_data = df[df['year'] == year].set_index('urban_class')
        rates = [year_data.loc[uc, 'fires_per_1000_units'] if uc in year_data.index else 0
                 for uc in urban_classes]
        bars = ax.bar([xi + yi*width for xi in x], rates, width, label=str(year),
                      color=color, edgecolor='black', alpha=0.85)
        for bar, rate in zip(bars, rates):
            if rate > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                       f'{rate:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xlabel('Urban Classification', fontsize=12)
    ax.set_ylabel('Structure Fires per 1,000 Housing Units', fontsize=12)
    ax.set_title('Structure Fire Rates by Urban Class and Year\n(Housing fires only - excludes vehicle, trash, outdoor)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks([xi + width for xi in x])
    ax.set_xticklabels(urban_labels)
    ax.legend(title='Year', loc='upper right')
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_time_series_chart(filename):
    """Create time series chart with code change annotation"""
    print(f"  Creating: {filename}")

    # Load time series data
    if not os.path.exists("outputs/time_series_analysis.csv"):
        print(f"    Warning: time_series_analysis.csv not found")
        return

    df = pd.read_csv("outputs/time_series_analysis.csv")

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot total incidents
    ax.plot(df['year'], df['total_incidents'], 'b-o', linewidth=2, markersize=8, label='Total Incidents')

    # Plot structure fires if available
    if 'structure_fires' in df.columns:
        ax.plot(df['year'], df['structure_fires'], 'r--s', linewidth=2, markersize=8, label='Structure Fires')

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Incidents', fontsize=12)
    ax.set_title('Fire Incidents Over Time (AFD)\n2006: Austin sprinkler code adopted (effect in 2010+ buildings)',
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')

    # Set integer x-ticks
    ax.set_xticks(df['year'].values)

    # Add annotation about code change
    ax.annotate(
        '2006 sprinkler code\n(visible in 2010+ construction)',
        xy=(df['year'].min(), df['total_incidents'].max()),
        xytext=(df['year'].min() + 0.3, df['total_incidents'].max() * 0.85),
        fontsize=10,
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7)
    )

    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_building_age_map(gdf, filename):
    """Create choropleth map of % post-2010 buildings"""
    if not HAS_FOLIUM:
        print(f"  Skipping {filename} (folium not installed)")
        return

    if 'pct_built_2010_plus' not in gdf.columns:
        print(f"  Skipping {filename} (building age data not available)")
        return

    print(f"  Creating: {filename}")

    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='cartodbpositron')

    valid_gdf = gdf[gdf['pct_built_2010_plus'].notna()].copy()

    folium.Choropleth(
        geo_data=valid_gdf.__geo_interface__,
        data=valid_gdf,
        columns=['response_area_id', 'pct_built_2010_plus'],
        key_on='feature.properties.response_area_id',
        fill_color='RdYlGn',  # Red=old, Green=new
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='% Housing Built 2010 or Later',
        nan_fill_color='white'
    ).add_to(m)

    tooltip = folium.GeoJsonTooltip(
        fields=['response_area_id', 'pct_built_2010_plus', 'pct_built_pre_1970', 'incidents_per_1000_pop'],
        aliases=['Response Area:', '% Built 2010+:', '% Built pre-1970:', 'Incidents/1000:'],
        localize=True
    )

    style_function = lambda x: {'fillColor': '#ffffff', 'color': '#000000', 'fillOpacity': 0, 'weight': 0.1}

    folium.GeoJson(
        valid_gdf,
        style_function=style_function,
        tooltip=tooltip
    ).add_to(m)

    m.save(f"outputs/{filename}")
    print(f"    ✓ Saved: outputs/{filename}")


def create_station_map(gdf, filename):
    """Create map with fire stations overlaid on population density"""
    if not HAS_FOLIUM:
        print(f"  Skipping {filename} (folium not installed)")
        return

    stations_path = "raw_data/fire_stations.geojson"
    if not os.path.exists(stations_path):
        print(f"  Skipping {filename} (fire stations data not available)")
        return

    print(f"  Creating: {filename}")

    stations = gpd.read_file(stations_path)

    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='cartodbpositron')

    # Add population density choropleth
    valid_gdf = gdf[gdf['pop_density'].notna() & (gdf['pop_density'] > 0)].copy()

    folium.Choropleth(
        geo_data=valid_gdf.__geo_interface__,
        data=valid_gdf,
        columns=['response_area_id', 'pop_density'],
        key_on='feature.properties.response_area_id',
        fill_color='YlOrRd',
        fill_opacity=0.5,
        line_opacity=0.2,
        legend_name='Population Density (per sq mi)',
        nan_fill_color='white'
    ).add_to(m)

    # Add fire stations as markers
    for idx, station in stations.iterrows():
        if station.geometry is not None:
            dept = station.get('DEPARTMENT', 'Unknown')
            name = station.get('NAME', station.get('STATION_NUMBER', 'Station'))

            # Color by department
            if dept and dept.upper() in ['AFD', 'AUSTIN', 'AUSTIN FIRE']:
                color = 'red'
                icon = 'fire'
            else:
                color = 'blue'
                icon = 'info-sign'

            folium.Marker(
                location=[station.geometry.y, station.geometry.x],
                popup=f"{name}<br>{dept}",
                icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
            ).add_to(m)

    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                background-color: white; padding: 10px; border: 2px solid grey;
                border-radius: 5px; font-size: 14px;">
    <p><strong>Fire Stations</strong></p>
    <p>🔴 AFD Stations</p>
    <p>🔵 Other Jurisdictions</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(f"outputs/{filename}")
    print(f"    ✓ Saved: outputs/{filename}")


def main():
    print("\n" + "#"*60)
    print("# FIRE RESOURCE ANALYSIS - VISUALIZATION")
    print("#"*60)
    
    # Load data
    ra, summary_urban, summary_housing = load_data()
    
    os.makedirs("outputs", exist_ok=True)
    
    # Create maps
    print("\nCreating maps...")
    
    if HAS_FOLIUM:
        create_choropleth_map(
            ra, 
            'incidents_per_1000_pop',
            'Fire Incidents per 1,000 Population',
            'map_incidents_per_capita.html'
        )
        
        create_categorical_map(
            ra,
            'urban_class',
            'Urban Classification',
            'map_urban_classification.html'
        )
        
        create_choropleth_map(
            ra,
            'pct_single_family',
            '% Single-Family Housing',
            'map_housing_typology.html',
            colormap='RdYlGn_r'
        )
    else:
        print("  Skipping interactive maps (install folium: pip install folium)")
    
    # Create charts - Original
    print("\nCreating charts...")

    create_bar_chart(summary_urban, 'chart_urban_comparison.png')
    create_scatter_plot(ra, 'chart_housing_correlation.png')
    create_summary_table_image(summary_urban, 'table_summary.png')

    # Create charts - New (per Tim's feedback)
    create_incident_type_chart('chart_incident_types.png')
    create_incident_type_chart_yearly('chart_incident_types_yearly.png')
    create_building_age_chart('chart_building_age.png')
    create_building_age_chart_yearly('chart_building_age_yearly.png')
    create_urban_comparison_yearly('chart_urban_comparison_yearly.png')
    create_time_series_chart('chart_time_series.png')

    # Structure fire trend charts (housing-only analysis)
    create_structure_fire_housing_trend_chart('chart_structure_fires_by_housing.png')
    create_structure_fire_urban_trend_chart('chart_structure_fires_by_urban.png')

    # Incident types by building age (sprinkler code effect)
    create_incident_type_by_building_age_chart('chart_incident_types_by_age.png')

    # Create maps - New
    print("\nCreating new maps...")
    if HAS_FOLIUM:
        create_building_age_map(ra, 'map_building_age.html')
        create_station_map(ra, 'map_fire_stations.html')
    
    # Summary
    print("\n" + "="*60)
    print("OUTPUTS CREATED")
    print("="*60)
    
    outputs = os.listdir("outputs")
    for f in sorted(outputs):
        print(f"  - outputs/{f}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Review the visualizations:
   - Open outputs/map_incidents_per_capita.html in a browser
   - Open outputs/map_urban_classification.html in a browser
   - Review the PNG charts

2. Prepare the findings brief:
   - Key finding: Do suburban areas have higher per-capita incident rates?
   - Statistical significance: Check outputs/statistical_tests.txt
   - Housing correlation: Does % single-family predict incident rates?

3. Share with Tim for review
""")


if __name__ == "__main__":
    main()
