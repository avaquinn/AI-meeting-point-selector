import os
import sys

import requests
from dotenv import load_dotenv

MATRIX_URL = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
FIELD_MASK = (
    "originIndex,destinationIndex,duration,distanceMeters,status,condition"
)

ORIGINS = [
    ("Cal Poly", "1 Grand Ave, San Luis Obispo, CA 93407"),
    ("Mission Plaza", "751 Palm St, San Luis Obispo, CA 93401"),
]
DESTINATIONS = [
    ("Madonna Inn", "100 Madonna Rd, San Luis Obispo, CA 93405"),
    ("SLO Airport", "901 Airport Dr, San Luis Obispo, CA 93401"),
    ("Laguna Lake Park", "504 Madonna Rd, San Luis Obispo, CA 93405"),
]

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    sys.exit("GOOGLE_API_KEY is missing. Copy .env.example to .env and fill it in.")

request_body = {
    "origins": [{"waypoint": {"address": address}} for _, address in ORIGINS],
    "destinations": [{"waypoint": {"address": address}} for _, address in DESTINATIONS],
    "travelMode": "DRIVE",
    "routingPreference": "TRAFFIC_AWARE",
}

response = requests.post(
    MATRIX_URL,
    headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    },
    json=request_body,
    timeout=30,
)

if response.status_code != 200:
    print(f"Request failed: HTTP {response.status_code}")
    print(response.text)
    sys.exit(1)

elements = {
    (element.get("originIndex"), element.get("destinationIndex")): element
    for element in response.json()
}

for origin_index, (origin_label, _) in enumerate(ORIGINS):
    for destination_index, (destination_label, _) in enumerate(DESTINATIONS):
        element = elements.get((origin_index, destination_index), {})
        label = f"{origin_label} -> {destination_label}"

        # "ROUTE_EXISTS" is the only condition that carries a usable duration.
        if element.get("condition") != "ROUTE_EXISTS":
            print(f"{label}: no route ({element.get('condition', 'missing element')})")
            print(f"  element: {element}")
            continue

        # Durations come back as a protobuf duration string, e.g. "412s".
        seconds = float(element["duration"].rstrip("s"))
        print(f"{label}: {seconds / 60:.1f} min ({element['distanceMeters']} m)")
    print()
