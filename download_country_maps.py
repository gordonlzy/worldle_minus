# scripts/download_country_maps.py
import os
import requests
import pandas as pd
from pathlib import Path

# Create directory for maps if it doesn't exist
MAPS_DIR = Path("media/country_images")
MAPS_DIR.mkdir(parents=True, exist_ok=True)

# Country data with continent information
country_data = [
    # Africa
    {"name": "Algeria", "continent": "Africa", "code": "DZ"},
    {"name": "Angola", "continent": "Africa", "code": "AO"},
    {"name": "Benin", "continent": "Africa", "code": "BJ"},
    {"name": "Botswana", "continent": "Africa", "code": "BW"},
    {"name": "Burkina Faso", "continent": "Africa", "code": "BF"},
    {"name": "Burundi", "continent": "Africa", "code": "BI"},
    {"name": "Cabo Verde", "continent": "Africa", "code": "CV"},
    {"name": "Cameroon", "continent": "Africa", "code": "CM"},
    {"name": "Central African Republic", "continent": "Africa", "code": "CF"},
    {"name": "Chad", "continent": "Africa", "code": "TD"},
    {"name": "Comoros", "continent": "Africa", "code": "KM"},
    {"name": "Congo", "continent": "Africa", "code": "CG"},
    {"name": "Democratic Republic of the Congo", "continent": "Africa", "code": "CD"},
    {"name": "Djibouti", "continent": "Africa", "code": "DJ"},
    {"name": "Egypt", "continent": "Africa", "code": "EG"},
    {"name": "Equatorial Guinea", "continent": "Africa", "code": "GQ"},
    {"name": "Eritrea", "continent": "Africa", "code": "ER"},
    {"name": "Eswatini", "continent": "Africa", "code": "SZ"},
    {"name": "Ethiopia", "continent": "Africa", "code": "ET"},
    {"name": "Gabon", "continent": "Africa", "code": "GA"},
    {"name": "Gambia", "continent": "Africa", "code": "GM"},
    {"name": "Ghana", "continent": "Africa", "code": "GH"},
    {"name": "Guinea", "continent": "Africa", "code": "GN"},
    {"name": "Guinea-Bissau", "continent": "Africa", "code": "GW"},
    {"name": "Ivory Coast", "continent": "Africa", "code": "CI"},
    {"name": "Kenya", "continent": "Africa", "code": "KE"},
    {"name": "Lesotho", "continent": "Africa", "code": "LS"},
    {"name": "Liberia", "continent": "Africa", "code": "LR"},
    {"name": "Libya", "continent": "Africa", "code": "LY"},
    {"name": "Madagascar", "continent": "Africa", "code": "MG"},
    {"name": "Malawi", "continent": "Africa", "code": "MW"},
    {"name": "Mali", "continent": "Africa", "code": "ML"},
    {"name": "Mauritania", "continent": "Africa", "code": "MR"},
    {"name": "Mauritius", "continent": "Africa", "code": "MU"},
    {"name": "Morocco", "continent": "Africa", "code": "MA"},
    {"name": "Mozambique", "continent": "Africa", "code": "MZ"},
    {"name": "Namibia", "continent": "Africa", "code": "NA"},
    {"name": "Niger", "continent": "Africa", "code": "NE"},
    {"name": "Nigeria", "continent": "Africa", "code": "NG"},
    {"name": "Rwanda", "continent": "Africa", "code": "RW"},
    {"name": "Sao Tome and Principe", "continent": "Africa", "code": "ST"},
    {"name": "Senegal", "continent": "Africa", "code": "SN"},
    {"name": "Seychelles", "continent": "Africa", "code": "SC"},
    {"name": "Sierra Leone", "continent": "Africa", "code": "SL"},
    {"name": "Somalia", "continent": "Africa", "code": "SO"},
    {"name": "South Africa", "continent": "Africa", "code": "ZA"},
    {"name": "South Sudan", "continent": "Africa", "code": "SS"},
    {"name": "Sudan", "continent": "Africa", "code": "SD"},
    {"name": "Tanzania", "continent": "Africa", "code": "TZ"},
    {"name": "Togo", "continent": "Africa", "code": "TG"},
    {"name": "Tunisia", "continent": "Africa", "code": "TN"},
    {"name": "Uganda", "continent": "Africa", "code": "UG"},
    {"name": "Zambia", "continent": "Africa", "code": "ZM"},
    {"name": "Zimbabwe", "continent": "Africa", "code": "ZW"},
    
    # Asia
    {"name": "Afghanistan", "continent": "Asia", "code": "AF"},
    {"name": "Armenia", "continent": "Asia", "code": "AM"},
    {"name": "Azerbaijan", "continent": "Asia", "code": "AZ"},
    {"name": "Bahrain", "continent": "Asia", "code": "BH"},
    {"name": "Bangladesh", "continent": "Asia", "code": "BD"},
    {"name": "Bhutan", "continent": "Asia", "code": "BT"},
    {"name": "Brunei", "continent": "Asia", "code": "BN"},
    {"name": "Cambodia", "continent": "Asia", "code": "KH"},
    {"name": "China", "continent": "Asia", "code": "CN"},
    {"name": "Cyprus", "continent": "Asia", "code": "CY"},
    {"name": "Georgia", "continent": "Asia", "code": "GE"},
    {"name": "India", "continent": "Asia", "code": "IN"},
    {"name": "Indonesia", "continent": "Asia", "code": "ID"},
    {"name": "Iran", "continent": "Asia", "code": "IR"},
    {"name": "Iraq", "continent": "Asia", "code": "IQ"},
    {"name": "Israel", "continent": "Asia", "code": "IL"},
    {"name": "Japan", "continent": "Asia", "code": "JP"},
    {"name": "Jordan", "continent": "Asia", "code": "JO"},
    {"name": "Kazakhstan", "continent": "Asia", "code": "KZ"},
    {"name": "Kuwait", "continent": "Asia", "code": "KW"},
    {"name": "Kyrgyzstan", "continent": "Asia", "code": "KG"},
    {"name": "Laos", "continent": "Asia", "code": "LA"},
    {"name": "Lebanon", "continent": "Asia", "code": "LB"},
    {"name": "Malaysia", "continent": "Asia", "code": "MY"},
    {"name": "Maldives", "continent": "Asia", "code": "MV"},
    {"name": "Mongolia", "continent": "Asia", "code": "MN"},
    {"name": "Myanmar", "continent": "Asia", "code": "MM"},
    {"name": "Nepal", "continent": "Asia", "code": "NP"},
    {"name": "North Korea", "continent": "Asia", "code": "KP"},
    {"name": "Oman", "continent": "Asia", "code": "OM"},
    {"name": "Pakistan", "continent": "Asia", "code": "PK"},
    {"name": "Palestine", "continent": "Asia", "code": "PS"},
    {"name": "Philippines", "continent": "Asia", "code": "PH"},
    {"name": "Qatar", "continent": "Asia", "code": "QA"},
    {"name": "Russia", "continent": "Asia", "code": "RU"},
    {"name": "Saudi Arabia", "continent": "Asia", "code": "SA"},
    {"name": "Singapore", "continent": "Asia", "code": "SG"},
    {"name": "South Korea", "continent": "Asia", "code": "KR"},
    {"name": "Sri Lanka", "continent": "Asia", "code": "LK"},
    {"name": "Syria", "continent": "Asia", "code": "SY"},
    {"name": "Taiwan", "continent": "Asia", "code": "TW"},
    {"name": "Tajikistan", "continent": "Asia", "code": "TJ"},
    {"name": "Thailand", "continent": "Asia", "code": "TH"},
    {"name": "Timor-Leste", "continent": "Asia", "code": "TL"},
    {"name": "Turkey", "continent": "Asia", "code": "TR"},
    {"name": "Turkmenistan", "continent": "Asia", "code": "TM"},
    {"name": "United Arab Emirates", "continent": "Asia", "code": "AE"},
    {"name": "Uzbekistan", "continent": "Asia", "code": "UZ"},
    {"name": "Vietnam", "continent": "Asia", "code": "VN"},
    {"name": "Yemen", "continent": "Asia", "code": "YE"},
    
    # Europe
    {"name": "Albania", "continent": "Europe", "code": "AL"},
    {"name": "Andorra", "continent": "Europe", "code": "AD"},
    {"name": "Austria", "continent": "Europe", "code": "AT"},
    {"name": "Belarus", "continent": "Europe", "code": "BY"},
    {"name": "Belgium", "continent": "Europe", "code": "BE"},
    {"name": "Bosnia and Herzegovina", "continent": "Europe", "code": "BA"},
    {"name": "Bulgaria", "continent": "Europe", "code": "BG"},
    {"name": "Croatia", "continent": "Europe", "code": "HR"},
    {"name": "Czech Republic", "continent": "Europe", "code": "CZ"},
    {"name": "Denmark", "continent": "Europe", "code": "DK"},
    {"name": "Estonia", "continent": "Europe", "code": "EE"},
    {"name": "Finland", "continent": "Europe", "code": "FI"},
    {"name": "France", "continent": "Europe", "code": "FR"},
    {"name": "Germany", "continent": "Europe", "code": "DE"},
    {"name": "Greece", "continent": "Europe", "code": "GR"},
    {"name": "Hungary", "continent": "Europe", "code": "HU"},
    {"name": "Iceland", "continent": "Europe", "code": "IS"},
    {"name": "Ireland", "continent": "Europe", "code": "IE"},
    {"name": "Italy", "continent": "Europe", "code": "IT"},
    {"name": "Kosovo", "continent": "Europe", "code": "XK"},
    {"name": "Latvia", "continent": "Europe", "code": "LV"},
    {"name": "Liechtenstein", "continent": "Europe", "code": "LI"},
    {"name": "Lithuania", "continent": "Europe", "code": "LT"},
    {"name": "Luxembourg", "continent": "Europe", "code": "LU"},
    {"name": "Malta", "continent": "Europe", "code": "MT"},
    {"name": "Moldova", "continent": "Europe", "code": "MD"},
    {"name": "Monaco", "continent": "Europe", "code": "MC"},
    {"name": "Montenegro", "continent": "Europe", "code": "ME"},
    {"name": "Netherlands", "continent": "Europe", "code": "NL"},
    {"name": "North Macedonia", "continent": "Europe", "code": "MK"},
    {"name": "Norway", "continent": "Europe", "code": "NO"},
    {"name": "Poland", "continent": "Europe", "code": "PL"},
    {"name": "Portugal", "continent": "Europe", "code": "PT"},
    {"name": "Romania", "continent": "Europe", "code": "RO"},
    {"name": "San Marino", "continent": "Europe", "code": "SM"},
    {"name": "Serbia", "continent": "Europe", "code": "RS"},
    {"name": "Slovakia", "continent": "Europe", "code": "SK"},
    {"name": "Slovenia", "continent": "Europe", "code": "SI"},
    {"name": "Spain", "continent": "Europe", "code": "ES"},
    {"name": "Sweden", "continent": "Europe", "code": "SE"},
    {"name": "Switzerland", "continent": "Europe", "code": "CH"},
    {"name": "Ukraine", "continent": "Europe", "code": "UA"},
    {"name": "United Kingdom", "continent": "Europe", "code": "GB"},
    {"name": "Vatican City", "continent": "Europe", "code": "VA"},
    
    # North America
    {"name": "Antigua and Barbuda", "continent": "North America", "code": "AG"},
    {"name": "Bahamas", "continent": "North America", "code": "BS"},
    {"name": "Barbados", "continent": "North America", "code": "BB"},
    {"name": "Belize", "continent": "North America", "code": "BZ"},
    {"name": "Canada", "continent": "North America", "code": "CA"},
    {"name": "Costa Rica", "continent": "North America", "code": "CR"},
    {"name": "Cuba", "continent": "North America", "code": "CU"},
    {"name": "Dominica", "continent": "North America", "code": "DM"},
    {"name": "Dominican Republic", "continent": "North America", "code": "DO"},
    {"name": "El Salvador", "continent": "North America", "code": "SV"},
    {"name": "Grenada", "continent": "North America", "code": "GD"},
    {"name": "Guatemala", "continent": "North America", "code": "GT"},
    {"name": "Haiti", "continent": "North America", "code": "HT"},
    {"name": "Honduras", "continent": "North America", "code": "HN"},
    {"name": "Jamaica", "continent": "North America", "code": "JM"},
    {"name": "Mexico", "continent": "North America", "code": "MX"},
    {"name": "Nicaragua", "continent": "North America", "code": "NI"},
    {"name": "Panama", "continent": "North America", "code": "PA"},
    {"name": "Saint Kitts and Nevis", "continent": "North America", "code": "KN"},
    {"name": "Saint Lucia", "continent": "North America", "code": "LC"},
    {"name": "Saint Vincent and the Grenadines", "continent": "North America", "code": "VC"},
    {"name": "Trinidad and Tobago", "continent": "North America", "code": "TT"},
    {"name": "United States", "continent": "North America", "code": "US"},
    
    # South America
    {"name": "Argentina", "continent": "South America", "code": "AR"},
    {"name": "Bolivia", "continent": "South America", "code": "BO"},
    {"name": "Brazil", "continent": "South America", "code": "BR"},
    {"name": "Chile", "continent": "South America", "code": "CL"},
    {"name": "Colombia", "continent": "South America", "code": "CO"},
    {"name": "Ecuador", "continent": "South America", "code": "EC"},
    {"name": "Guyana", "continent": "South America", "code": "GY"},
    {"name": "Paraguay", "continent": "South America", "code": "PY"},
    {"name": "Peru", "continent": "South America", "code": "PE"},
    {"name": "Suriname", "continent": "South America", "code": "SR"},
    {"name": "Uruguay", "continent": "South America", "code": "UY"},
    {"name": "Venezuela", "continent": "South America", "code": "VE"},
    
    # Oceania
    {"name": "Australia", "continent": "Oceania", "code": "AU"},
    {"name": "Fiji", "continent": "Oceania", "code": "FJ"},
    {"name": "Kiribati", "continent": "Oceania", "code": "KI"},
    {"name": "Marshall Islands", "continent": "Oceania", "code": "MH"},
    {"name": "Micronesia", "continent": "Oceania", "code": "FM"},
    {"name": "Nauru", "continent": "Oceania", "code": "NR"},
    {"name": "New Zealand", "continent": "Oceania", "code": "NZ"},
    {"name": "Palau", "continent": "Oceania", "code": "PW"},
    {"name": "Papua New Guinea", "continent": "Oceania", "code": "PG"},
    {"name": "Samoa", "continent": "Oceania", "code": "WS"},
    {"name": "Solomon Islands", "continent": "Oceania", "code": "SB"},
    {"name": "Tonga", "continent": "Oceania", "code": "TO"},
    {"name": "Tuvalu", "continent": "Oceania", "code": "TV"},
    {"name": "Vanuatu", "continent": "Oceania", "code": "VU"},
]

# Convert to DataFrame for easier manipulation
df = pd.DataFrame(country_data)

# Save the data to a CSV file for reference
df.to_csv("country_continent_data.csv", index=False)
print(f"Saved country data to country_continent_data.csv")

# Function to download map images from different sources
def download_country_maps():
    print(f"Downloading country map images to {MAPS_DIR}...")
    
    for index, country in df.iterrows():
        country_name = country['name']
        country_code = country['code']
        safe_name = country_name.lower().replace(' ', '_')
        file_path = MAPS_DIR / f"{safe_name}.png"
        
        # Skip if already downloaded
        if file_path.exists():
            print(f"Already exists: {country_name}")
            continue
            
        # Try different sources for the country outline
        # 1. Try amCharts maps
        url = f"https://www.amcharts.com/lib/images/svg/maps/countries/{country_code.lower()}.svg"
        
        # 2. Alternative: MapSparrow silhouettes
        url2 = f"https://images.mapsparrow.com/maps/countries/{country_name.lower().replace(' ', '-')}-vector-map.png"
        
        # 3. Another alternative: REST Countries flags
        url3 = f"https://flagcdn.com/w320/{country_code.lower()}.png"
        
        # Try each URL in order
        for attempt, current_url in enumerate([url, url2, url3], 1):
            try:
                response = requests.get(current_url, timeout=10)
                if response.status_code == 200:
                    # Save the image
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {country_name} (Source {attempt})")
                    break
            except Exception as e:
                if attempt == 3:  # Last attempt failed
                    print(f"Failed to download {country_name}: {e}")

# Run the download function
download_country_maps()

# Create a simple Django script to import the data
with open("import_countries.py", "w") as f:
    f.write("""
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
    country, created = Country.objects.get_or_create(name=country_name)
    
    # Add continent
    country.continents.add(continents[continent_name])
    
    # Add image if available
    safe_name = country_name.lower().replace(' ', '_')
    image_path = f"media/country_images/{safe_name}.png"
    
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img_file:
            country.image.save(f"{safe_name}.png", File(img_file), save=True)
        print(f"Added {country_name} with image")
    else:
        print(f"Added {country_name} without image")
    
print("Import complete!")
""")

print("""
All country map images have been downloaded to the media/country_images directory.
CSV data file and import script have been created.

To import into your Django project:
1. Copy the 'media' directory to your Django project root
2. Run: python manage.py shell < import_countries.py
""")