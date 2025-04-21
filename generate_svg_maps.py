# scripts/generate_svg_maps.py
import os
import json
import requests
from pathlib import Path

# Create SVG maps directory
SVG_DIR = Path("media/country_svg")
SVG_DIR.mkdir(parents=True, exist_ok=True)

# Natural Earth data for country boundaries (simplified for better performance)
GEOJSON_URL = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"

def download_geojson():
    """Download the GeoJSON file with country boundaries"""
    print("Downloading country boundary data...")
    response = requests.get(GEOJSON_URL)
    if response.status_code == 200:
        data = response.json()
        # Save a local copy for reference
        with open("countries.geojson", "w") as f:
            json.dump(data, f)
        print("Downloaded country boundaries")
        return data
    else:
        print("Failed to download country boundaries")
        return None

def create_svg_from_geojson(geojson_data):
    """Create SVG files for each country"""
    if not geojson_data:
        return
    
    features = geojson_data.get("features", [])
    print(f"Creating SVG maps for {len(features)} countries...")
    
    for feature in features:
        properties = feature.get("properties", {})
        name = properties.get("ADMIN", "Unknown")
        geometry = feature.get("geometry", {})
        
        if geometry["type"] == "Polygon":
            polygons = [geometry["coordinates"][0]]
        elif geometry["type"] == "MultiPolygon":
            polygons = [poly[0] for poly in geometry["coordinates"]]
        else:
            print(f"Skipping {name}: unsupported geometry type {geometry['type']}")
            continue
        
        # Create SVG content
        svg_content = create_svg(name, polygons)
        
        # Save SVG file
        safe_name = name.lower().replace(" ", "_")
        svg_path = SVG_DIR / f"{safe_name}.svg"
        
        with open(svg_path, "w") as f:
            f.write(svg_content)
        
        print(f"Created SVG for {name}")

def create_svg(country_name, polygons):
    """Generate SVG content for a country"""
    # Find the bounding box
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    for polygon in polygons:
        for point in polygon:
            x, y = point
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
    
    # Add padding (5%)
    width = max_x - min_x
    height = max_y - min_y
    padding_x = width * 0.05
    padding_y = height * 0.05
    
    min_x -= padding_x
    min_y -= padding_y
    max_x += padding_x
    max_y += padding_y
    
    width = max_x - min_x
    height = max_y - min_y
    
    # Create SVG paths
    paths = []
    for polygon in polygons:
        path = "M " + " L ".join([f"{(p[0]-min_x)/width*500} {(p[1]-min_y)/height*500}" for p in polygon]) + " Z"
        paths.append(path)
    
    # Build the SVG
    svg = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="500" height="500" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
    <title>{country_name}</title>
    <g>
        {''.join([f'<path d="{path}" fill="#2B60DE" stroke="#000" stroke-width="0.5"/>' for path in paths])}
    </g>
</svg>"""
    
    return svg

def create_import_script():
    """Create a script to import SVGs into Django"""
    with open("import_svg_maps.py", "w") as f:
        f.write("""
# Script to import SVG maps to Django database
# Run with: python manage.py shell < import_svg_maps.py

import os
from django.core.files import File
from quiz.models import Country

# Directory with SVG files
svg_dir = 'media/country_svg'

# Get all countries
countries = Country.objects.all()

for country in countries:
    # Format filename
    safe_name = country.name.lower().replace(' ', '_')
    svg_path = f"{svg_dir}/{safe_name}.svg"
    
    # Check if SVG exists
    if os.path.exists(svg_path):
        with open(svg_path, 'rb') as svg_file:
            # Update country with SVG
            country.image.save(f"{safe_name}.svg", File(svg_file), save=True)
        print(f"Updated {country.name} with SVG map")
    else:
        print(f"No SVG found for {country.name}")

print("SVG import complete!")
""")

# Main execution
geojson_data = download_geojson()
create_svg_from_geojson(geojson_data)
create_import_script()

print("""
SVG map files have been created in the media/country_svg directory.
Import script has been created.

To import SVG maps into your Django project:
1. Copy the 'media' directory to your Django project root
2. Run: python manage.py shell < import_svg_maps.py
""")