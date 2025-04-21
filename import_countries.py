# Script to import countries and continents to Django database
# Run with: python manage.py shell < import_countries.py

import os
import pandas as pd
from django.core.files import File
from quiz.models import Country, Continent

# Load country data
df = pd.read_csv('country_continent_data.csv')

# Get or create continents
continents = {}
for continent_name in df['continent'].unique():
    continent, created = Continent.objects.get_or_create(name=continent_name)
    continents[continent_name] = continent
    if created:
        print(f"Created continent: {continent_name}")

# Import countries
for _, row in df.iterrows():
    country_name = row['name']
    continent_name = row['continent']
    
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
    country.save()
    
    # Add continent
    country.continents.add(continents[continent_name])
    
    # Add image if available
    safe_name = country_name.lower().replace(' ', '_')
    image_path = f"media/country_images/{safe_name}.png"
    
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img_file:
            country.image.save(f"{safe_name}.png", File(img_file), save=True)
        print(f"Added {country_name} with image and coordinates ({country.latitude}, {country.longitude})")
    else:
        print(f"Added {country_name} without image, coordinates ({country.latitude}, {country.longitude})")
    
print("Import complete!")
