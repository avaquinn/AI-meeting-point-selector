
import os
import sys

import requests
from dotenv import load_dotenv

GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

ADDRESSES = [
    "1 Grand Ave, San Luis Obispo, CA",
    "751 Palm St, San Luis Obispo, CA",
]

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    sys.exit("GOOGLE_API_KEY is missing. Check your .env file.")

for address in ADDRESSES:
    response = requests.get(
        GEOCODING_URL,
        params={
            "address": address,
            "key": api_key,
        },
        timeout=15,
    )

    if response.status_code != 200:
        print(f"Request failed: HTTP {response.status_code}")
        print(response.text)
        continue

    data = response.json()

    if data.get("status") != "OK":
        print(f"{address}: {data.get('status')}")
        print(data.get("error_message", "No additional details"))
        continue

    result = data["results"][0]
    location = result["geometry"]["location"]

    print(f"{address}")
    print(f"  Formatted address: {result['formatted_address']}")
    print(f"  Latitude: {location['lat']}")
    print(f"  Longitude: {location['lng']}")
    print()

