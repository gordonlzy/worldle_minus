import os
import sys
import django
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from django.core.files import File

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordle_minus.settings')
django.setup()

from quiz.models import Country

def get_country_code(country_name):
    # Dictionary mapping country names to their ISO 3166-1 alpha-3 codes
    country_codes = {
        "Afghanistan": "AFG",
        "Albania": "ALB",
        "Algeria": "DZA",
        "Andorra": "AND",
        "Angola": "AGO",
        "Antigua and Barbuda": "ATG",
        "Argentina": "ARG",
        "Armenia": "ARM",
        "Australia": "AUS",
        "Austria": "AUT",
        "Azerbaijan": "AZE",
        "Bahamas": "BHS",
        "Bahrain": "BHR",
        "Bangladesh": "BGD",
        "Barbados": "BRB",
        "Belarus": "BLR",
        "Belgium": "BEL",
        "Belize": "BLZ",
        "Benin": "BEN",
        "Bhutan": "BTN",
        "Bolivia": "BOL",
        "Bosnia and Herzegovina": "BIH",
        "Botswana": "BWA",
        "Brazil": "BRA",
        "Brunei": "BRN",
        "Bulgaria": "BGR",
        "Burkina Faso": "BFA",
        "Burundi": "BDI",
        "Cabo Verde": "CPV",
        "Cambodia": "KHM",
        "Cameroon": "CMR",
        "Canada": "CAN",
        "Central African Republic": "CAF",
        "Chad": "TCD",
        "Chile": "CHL",
        "China": "CHN",
        "Colombia": "COL",
        "Comoros": "COM",
        "Congo": "COG",
        "Costa Rica": "CRI",
        "Côte d'Ivoire": "CIV",
        "Croatia": "HRV",
        "Cuba": "CUB",
        "Cyprus": "CYP",
        "Czechia": "CZE",
        "Democratic Republic of the Congo": "COD",
        "Denmark": "DNK",
        "Djibouti": "DJI",
        "Dominica": "DMA",
        "Dominican Republic": "DOM",
        "Ecuador": "ECU",
        "Egypt": "EGY",
        "El Salvador": "SLV",
        "Equatorial Guinea": "GNQ",
        "Eritrea": "ERI",
        "Estonia": "EST",
        "Eswatini": "SWZ",
        "Ethiopia": "ETH",
        "Fiji": "FJI",
        "Finland": "FIN",
        "France": "FRA",
        "Gabon": "GAB",
        "Gambia": "GMB",
        "Georgia": "GEO",
        "Germany": "DEU",
        "Ghana": "GHA",
        "Greece": "GRC",
        "Grenada": "GRD",
        "Guatemala": "GTM",
        "Guinea": "GIN",
        "Guinea-Bissau": "GNB",
        "Guyana": "GUY",
        "Haiti": "HTI",
        "Honduras": "HND",
        "Hungary": "HUN",
        "Iceland": "ISL",
        "India": "IND",
        "Indonesia": "IDN",
        "Iran": "IRN",
        "Iraq": "IRQ",
        "Ireland": "IRL",
        "Israel": "ISR",
        "Italy": "ITA",
        "Jamaica": "JAM",
        "Japan": "JPN",
        "Jordan": "JOR",
        "Kazakhstan": "KAZ",
        "Kenya": "KEN",
        "Kiribati": "KIR",
        "Kuwait": "KWT",
        "Kyrgyzstan": "KGZ",
        "Laos": "LAO",
        "Latvia": "LVA",
        "Lebanon": "LBN",
        "Lesotho": "LSO",
        "Liberia": "LBR",
        "Libya": "LBY",
        "Liechtenstein": "LIE",
        "Lithuania": "LTU",
        "Luxembourg": "LUX",
        "Madagascar": "MDG",
        "Malawi": "MWI",
        "Malaysia": "MYS",
        "Maldives": "MDV",
        "Mali": "MLI",
        "Malta": "MLT",
        "Marshall Islands": "MHL",
        "Mauritania": "MRT",
        "Mauritius": "MUS",
        "Mexico": "MEX",
        "Micronesia": "FSM",
        "Moldova": "MDA",
        "Monaco": "MCO",
        "Mongolia": "MNG",
        "Montenegro": "MNE",
        "Morocco": "MAR",
        "Mozambique": "MOZ",
        "Myanmar": "MMR",
        "Namibia": "NAM",
        "Nauru": "NRU",
        "Nepal": "NPL",
        "Netherlands": "NLD",
        "New Zealand": "NZL",
        "Nicaragua": "NIC",
        "Niger": "NER",
        "Nigeria": "NGA",
        "North Korea": "PRK",
        "North Macedonia": "MKD",
        "Norway": "NOR",
        "Oman": "OMN",
        "Pakistan": "PAK",
        "Palau": "PLW",
        "Panama": "PAN",
        "Papua New Guinea": "PNG",
        "Paraguay": "PRY",
        "Peru": "PER",
        "Philippines": "PHL",
        "Poland": "POL",
        "Portugal": "PRT",
        "Qatar": "QAT",
        "Romania": "ROU",
        "Russia": "RUS",
        "Rwanda": "RWA",
        "Saint Kitts and Nevis": "KNA",
        "Saint Lucia": "LCA",
        "Saint Vincent and the Grenadines": "VCT",
        "Samoa": "WSM",
        "San Marino": "SMR",
        "Sao Tome and Principe": "STP",
        "Saudi Arabia": "SAU",
        "Senegal": "SEN",
        "Serbia": "SRB",
        "Seychelles": "SYC",
        "Sierra Leone": "SLE",
        "Singapore": "SGP",
        "Slovakia": "SVK",
        "Slovenia": "SVN",
        "Solomon Islands": "SLB",
        "Somalia": "SOM",
        "South Africa": "ZAF",
        "South Korea": "KOR",
        "South Sudan": "SSD",
        "Spain": "ESP",
        "Sri Lanka": "LKA",
        "Sudan": "SDN",
        "Suriname": "SUR",
        "Sweden": "SWE",
        "Switzerland": "CHE",
        "Syria": "SYR",
        "Tajikistan": "TJK",
        "Tanzania": "TZA",
        "Thailand": "THA",
        "Timor-Leste": "TLS",
        "Togo": "TGO",
        "Tonga": "TON",
        "Trinidad and Tobago": "TTO",
        "Tunisia": "TUN",
        "Turkey": "TUR",
        "Turkmenistan": "TKM",
        "Tuvalu": "TUV",
        "Uganda": "UGA",
        "Ukraine": "UKR",
        "United Arab Emirates": "ARE",
        "United Kingdom": "GBR",
        "United States": "USA",
        "Uruguay": "URY",
        "Uzbekistan": "UZB",
        "Vanuatu": "VUT",
        "Vatican City": "VAT",
        "Venezuela": "VEN",
        "Vietnam": "VNM",
        "Yemen": "YEM",
        "Zambia": "ZMB",
        "Zimbabwe": "ZWE"
    }
    
    return country_codes.get(country_name)

def download_country_map(country):
    print(f"Processing {country.name}...")
    
    # Skip if map already exists
    if country.map and os.path.exists(country.map.path):
        print(f"Map for {country.name} already exists")
        return
    
    try:
        # Get the country code
        country_code = get_country_code(country.name)
        if not country_code:
            print(f"Could not find country code for {country.name}")
            return
        
        # Construct the GADM URL
        map_url = f"https://gadm.org/img/480/gadm/{country_code}/{country_code}.png"
        
        print(f"Downloading map for {country.name} ({country_code}) from {map_url}...")
        
        # Download the map
        map_response = requests.get(map_url, timeout=10)
        if map_response.status_code == 200:
            # Save the map
            map_path = f"media/maps/{country.name.lower().replace(' ', '_')}.png"
            with open(map_path, 'wb') as f:
                f.write(map_response.content)
            
            # Update the country model
            with open(map_path, 'rb') as f:
                country.map.save(f"{country.name.lower().replace(' ', '_')}.png", File(f), save=True)
            
            print(f"Successfully downloaded map for {country.name}")
        else:
            print(f"Failed to download map for {country.name}: HTTP {map_response.status_code}")
    
    except requests.exceptions.Timeout:
        print(f"Timeout while processing {country.name}")
    except requests.exceptions.RequestException as e:
        print(f"Request error for {country.name}: {str(e)}")
    except Exception as e:
        print(f"Error processing {country.name}: {str(e)}")

def download_country_maps():
    print("Starting map download process...")
    
    # Create media/maps directory if it doesn't exist
    os.makedirs('media/maps', exist_ok=True)
    print("Created media/maps directory")
    
    # Get all countries
    countries = Country.objects.all()
    print(f"Found {len(countries)} countries to process")
    
    # Process countries in parallel with 5 threads
    with ThreadPoolExecutor(max_workers=5) as executor:
        print("Starting parallel processing...")
        executor.map(download_country_map, countries)
    
    print("Map download process completed")

if __name__ == "__main__":
    download_country_maps() 