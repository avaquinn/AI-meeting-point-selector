import os
import sys

import requests
from dotenv import load_dotenv

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
QUERY = "coffee shops in San Luis Obispo, CA"
FIELD_MASK = "places.displayName,places.id,places.location"

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    sys.exit("GOOGLE_API_KEY is missing. Copy .env.example to .env and fill it in.")

response = requests.post(
    SEARCH_URL,
    headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    },
    json={"textQuery": QUERY, "maxResultCount": 10},
    timeout=15,
)

if response.status_code != 200:
    print(f"Request failed: HTTP {response.status_code}")
    print(response.text)
    sys.exit(1)

places = response.json().get("places", [])
print(f"{QUERY} -> {len(places)} result(s)\n")

for place in places:
    name = place.get("displayName", {}).get("text", "(no name)")
    location = place.get("location", {})
    print(name)
    print(f"  place ID: {place.get('id')}")
    print(f"  lat, lng: {location.get('latitude')}, {location.get('longitude')}")
    print()
