import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordle_minus.settings')
django.setup()

from quiz.models import Continent, Country

# Pacific Islands
pacific_islands = [
    'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru', 'Palau',
    'Papua New Guinea', 'Samoa', 'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu'
]

# Caribbean Islands
caribbean_islands = [
    'Antigua and Barbuda', 'Bahamas', 'Barbados', 'Cuba', 'Dominica',
    'Dominican Republic', 'Grenada', 'Haiti', 'Jamaica', 'Saint Kitts and Nevis',
    'Saint Lucia', 'Saint Vincent and the Grenadines', 'Trinidad and Tobago'
]

def update_continents():
    # Create or update continents
    for code, name in Continent.get_default_continents():
        Continent.objects.get_or_create(code=code, defaults={'name': name})

    # Get continent instances
    pacific = Continent.objects.get(code='PA')
    caribbean = Continent.objects.get(code='CB')

    # Update Pacific Islands
    for country_name in pacific_islands:
        try:
            country = Country.objects.get(name=country_name)
            country.continents.add(pacific)
            print(f"Added {country_name} to Pacific Islands")
        except Country.DoesNotExist:
            print(f"Country not found: {country_name}")

    # Update Caribbean Islands
    for country_name in caribbean_islands:
        try:
            country = Country.objects.get(name=country_name)
            country.continents.add(caribbean)
            print(f"Added {country_name} to Caribbean Islands")
        except Country.DoesNotExist:
            print(f"Country not found: {country_name}")

if __name__ == '__main__':
    update_continents() 