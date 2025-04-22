#!/usr/bin/env python
import os
import sys
import django
import pandas as pd
import shutil
from pathlib import Path
from django.core.files import File

# Get the project root directory and add it to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordle_minus.settings')
django.setup()

from quiz.models import Country, Continent

def import_countries():
    # Load country data
    df = pd.read_csv(PROJECT_ROOT / 'country_continent_data.csv')

    # Create a mapping of continent names to codes
    continent_codes = dict(Continent.get_default_continents())
    continent_codes_reverse = {name: code for code, name in continent_codes.items()}

    # Get or create continents
    continents = {}
    for continent_name in df['continent'].unique():
        # Get the continent code
        continent_code = continent_codes_reverse.get(continent_name)
        if not continent_code:
            print(f"Warning: No code found for continent {continent_name}, skipping...")
            continue

        continent, created = Continent.objects.get_or_create(
            name=continent_name,
            defaults={'code': continent_code}
        )
        continents[continent_name] = continent
        if created:
            print(f"Created continent: {continent_name} with code {continent_code}")

    # Import countries
    for _, row in df.iterrows():
        country_name = row['name']
        continent_name = row['continent']
        
        # Skip if continent wasn't created
        if continent_name not in continents:
            print(f"Skipping {country_name} due to missing continent {continent_name}")
            continue
        
        # Create or get country
        country, created = Country.objects.get_or_create(
            name=country_name,
            defaults={
                'latitude': row.get('latitude', 0.0),  # Default to 0 if not provided
                'longitude': row.get('longitude', 0.0)  # Default to 0 if not provided
            }
        )
        
        # Update latitude and longitude if they exist in the data
        if 'latitude' in row and pd.notna(row['latitude']):
            country.latitude = row['latitude']
        if 'longitude' in row and pd.notna(row['longitude']):
            country.longitude = row['longitude']
        
        # Add continent
        country.continents.add(continents[continent_name])
        
        # Add flag image if available
        safe_name = country_name.lower().replace(' ', '_')
        flag_path = PROJECT_ROOT / "media/country_images" / f"{safe_name}.png"
        map_path = PROJECT_ROOT / "media/maps" / f"{safe_name}.png"
        
        if flag_path.exists():
            # Only copy if the file doesn't already exist in the target location
            target_flag_path = PROJECT_ROOT / "media" / "country_images" / f"{safe_name}.png"
            if not target_flag_path.exists():
                shutil.copy2(flag_path, target_flag_path)
            # Update the model to point to the file
            country.image = f"country_images/{safe_name}.png"
            print(f"Added flag for {country_name}")
        
        # Add country map if available
        if map_path.exists():
            # Only copy if the file doesn't already exist in the target location
            target_map_path = PROJECT_ROOT / "media" / "maps" / f"{safe_name}.png"
            if not target_map_path.exists():
                shutil.copy2(map_path, target_map_path)
            # Update the model to point to the file
            country.map = f"maps/{safe_name}.png"
            print(f"Added map for {country_name}")
        
        if not flag_path.exists() and not map_path.exists():
            print(f"Warning: No flag or map found for {country_name}")
        
        country.save()
        print(f"{'Created' if created else 'Updated'} country: {country_name}")
    
    print("Import complete!")

if __name__ == '__main__':
    import_countries()
