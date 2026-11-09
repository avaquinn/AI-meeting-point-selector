# Google Places API wrapper


import os

import requests
from dotenv import load_dotenv

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = "places.displayName,places.id,places.location"

load_dotenv()


def find_places(query="coffee shops in San Luis Obispo, CA", max_results=10):
    """
    Search Google Places for candidate meeting locations.

    Returns a list of dictionaries containing:
        name: Place name
        id: Google Place ID
        location: (latitude, longitude)
    """

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is missing. "
            "Copy .env.example to .env and fill it in."
        )

    response = requests.post(
        SEARCH_URL,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        },
        json={
            "textQuery": query,
            "maxResultCount": max_results,
        },
        timeout=15,
    )

    # Raise an exception if the request fails.
    response.raise_for_status()

    places = response.json().get("places", [])

    candidates = []

    for place in places:
        location = place.get("location", {})

        lat = location.get("latitude")
        lng = location.get("longitude")

        if lat is None or lng is None:
            continue

        candidates.append({
            "name": place.get("displayName", {}).get(
                "text", "(no name)"
            ),
            "id": place.get("id"),
            "location": (lat, lng),
        })

    return candidates
