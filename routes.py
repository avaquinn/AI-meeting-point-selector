# Google Routes API wrapper


import os

import requests
from dotenv import load_dotenv

MATRIX_URL = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
FIELD_MASK = (
    "originIndex,destinationIndex,duration,distanceMeters,status,condition"
)

load_dotenv()


def get_routes(origins, candidate):
    """
    Calculate driving routes from all origins to one candidate.

    origins:
        List of (latitude, longitude) tuples.

    candidate:
        Dictionary containing:
        {
            "name": str,
            "id": str,
            "location": (latitude, longitude)
        }

    Returns:
        List of route dictionaries ordered by origin:
        [
            {"time": minutes, "distance": meters},
            ...
        ]

        Returns None if any origin has no valid route.
    """

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is missing. "
            "Copy .env.example to .env and fill it in."
        )

    if not origins:
        raise ValueError("At least one origin is required.")

    # Convert origin coordinates to Google waypoints.
    origin_waypoints = [
        {
            "waypoint": {
                "location": {
                    "latLng": {
                        "latitude": lat,
                        "longitude": lng,
                    }
                }
            }
        }
        for lat, lng in origins
    ]

    # Use the Google Place ID returned by places.py.
    destination_waypoints = [
        {
            "waypoint": {
                "placeId": candidate["id"]
            }
        }
    ]

    request_body = {
        "origins": origin_waypoints,
        "destinations": destination_waypoints,
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

    response.raise_for_status()

    elements = response.json()

    # Create an ordered list of routes.
    routes = [None] * len(origins)

    for element in elements:
        if element.get("condition") != "ROUTE_EXISTS":
            return None

        origin_index = element.get("originIndex")

        if (
            not isinstance(origin_index, int)
            or not 0 <= origin_index < len(origins)
        ):
            raise ValueError(
                "Invalid origin index in Routes API response."
            )

        duration = element.get("duration")
        distance = element.get("distanceMeters")

        if duration is None or distance is None:
            return None

        # Convert Google's duration string to minutes.
        seconds = float(duration.removesuffix("s"))

        routes[origin_index] = {
            "time": seconds / 60,
            "distance": distance,
        }

    # Ensure every traveler has a valid route.
    if any(route is None for route in routes):
        return None

    return routes


def main():
    # Example starting locations.
    origins = [
        (35.3000, -120.6600),
        (35.2700, -120.6500),
    ]

    # Fetch an actual Google Place ID.
    from places import find_places

    candidates = find_places(
        query="coffee shops in San Luis Obispo, CA",
        max_results=1,
    )

    if not candidates:
        print("No destinations found.")
        return

    candidate = candidates[0]

    print(f"Calculating routes to {candidate['name']}...\n")

    routes = get_routes(origins, candidate)

    if routes is None:
        print("One or more travelers cannot reach this location.")
        return

    for i, route in enumerate(routes):
        print(f"Traveler {i + 1}:")
        print(f"  Travel time: {route['time']:.1f} min")
        print(f"  Distance: {route['distance']} m")
        print()


if __name__ == "__main__":
    main()

