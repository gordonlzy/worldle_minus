from django.core.management.base import BaseCommand
from django.core.files import File
from quiz.models import Country, Continent
import os
import glob

class Command(BaseCommand):
    help = 'Import countries and continents'

    def handle(self, *args, **kwargs):
        # Define continents
        continents = {
            "Africa": Continent.objects.get_or_create(name="Africa")[0],
            "Asia": Continent.objects.get_or_create(name="Asia")[0],
            "Europe": Continent.objects.get_or_create(name="Europe")[0],
            "North America": Continent.objects.get_or_create(name="North America")[0],
            "South America": Continent.objects.get_or_create(name="South America")[0],
            "Oceania": Continent.objects.get_or_create(name="Oceania")[0],
            "Antarctica": Continent.objects.get_or_create(name="Antarctica")[0],
        }
        
        # Path to country images
        country_images_dir = 'media/country_images'
        if not os.path.exists(country_images_dir):
            country_images_dir = 'quiz/media/country_images'
        
        # List all image files
        image_files = glob.glob(f"{country_images_dir}/*.png") + glob.glob(f"{country_images_dir}/*.svg")
        
        # Country to continent mapping (simplified version)
        country_continents = {
            # Africa
            "algeria": "Africa", "egypt": "Africa", "kenya": "Africa", "nigeria": "Africa", 
            "south_africa": "Africa", "morocco": "Africa", "ethiopia": "Africa",
            # Asia
            "china": "Asia", "india": "Asia", "japan": "Asia", "russia": "Asia", 
            "saudi_arabia": "Asia", "turkey": "Asia", "indonesia": "Asia",
            # Europe
            "france": "Europe", "germany": "Europe", "italy": "Europe", "spain": "Europe", 
            "united_kingdom": "Europe", "sweden": "Europe", "poland": "Europe",
            # North America
            "canada": "North America", "united_states": "North America", "mexico": "North America",
            # South America
            "brazil": "South America", "argentina": "South America", "peru": "South America",
            # Oceania
            "australia": "Oceania", "new_zealand": "Oceania",
            # Antarctica
            "antarctica": "Antarctica",
        }
        
        # Add all countries from image files
        for image_path in image_files:
            filename = os.path.basename(image_path)
            country_code = os.path.splitext(filename)[0]  # Remove extension
            country_name = country_code.replace('_', ' ').title()
            
            # Create the country
            country, created = Country.objects.get_or_create(name=country_name)
            
            # Add image to country
            with open(image_path, 'rb') as img_file:
                country.image.save(filename, File(img_file), save=True)
            
            # Set continent(s)
            continent_name = country_continents.get(country_code, None)
            if continent_name and continent_name in continents:
                country.continents.add(continents[continent_name])
            
            self.stdout.write(self.style.SUCCESS(f'Added {country_name}'))
            
        self.stdout.write(self.style.SUCCESS('Successfully imported countries'))
