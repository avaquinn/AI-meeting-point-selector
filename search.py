
import heapq
from itertools import count
from math import radians, sin, cos, asin, sqrt

from selector import score


def haversine_km(a, b):
    """
    Calculate straight-line distance between
    two (latitude, longitude) coordinates.
    """
    lat1, lon1 = map(radians, a)
    lat2, lon2 = map(radians, b)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    h = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    return 6371.0 * 2 * asin(sqrt(h))


def estimate_times(origins, destination, speed_kmh=50):
    """
    Estimate travel times using straight-line distances.

    These estimates are only used for ordering
    candidates, not for calculating final scores.
    """
    return [
        haversine_km(origin, destination) / speed_kmh * 60
        for origin in origins
    ]


def find_best_meeting_point(
    origins,
    candidates,
    get_routes,
    fairness_weight=0.7,
    worst_weight=0.3,
    max_evaluations=None,
):
    """
    Greedy Best-First Search for meeting locations.

    origins:
        List of (lat, lng) coordinates.

    candidates:
        List of dictionaries:
        {"name": str, "location": (lat, lng)}

    get_routes:
        Function returning routes from all origins
        to one candidate.

        Expected format:
        [
            {"time": minutes, "distance": meters},
            ...
        ]

    max_evaluations:
        Optional limit on number of candidate evaluations.
        None evaluates every candidate.
    """

    if not origins:
        raise ValueError("At least one origin is required.")

    if max_evaluations is not None and max_evaluations < 0:
        raise ValueError("max_evaluations must be nonnegative.")

    queue = []
    counter = count()

    # Step 1: Calculate heuristic scores.
    for candidate in candidates:
        estimated_times = estimate_times(
            origins,
            candidate["location"]
        )

        estimated_score = score(
            estimated_times,
            fairness_weight=fairness_weight,
            worst_weight=worst_weight,
        )

        heapq.heappush(
            queue,
            (estimated_score, next(counter), candidate)
        )

    best = None
    best_score = float("inf")
    evaluations = 0

    # Step 2: Evaluate candidates in greedy order.
    while queue:
        if (
            max_evaluations is not None
            and evaluations >= max_evaluations
        ):
            break

        estimated_score, _, candidate = heapq.heappop(queue)

        print(
            f"Evaluating {candidate['name']} "
            f"(estimated score: {estimated_score:.2f})"
        )

        # Step 3: Get actual travel times from Google.
        routes = get_routes(origins, candidate)
        evaluations += 1

        # Skip candidates with unavailable routes.
        if routes is None:
            continue

        if len(routes) != len(origins):
            raise ValueError(
                "get_routes must return one route per origin."
            )

        times = [route["time"] for route in routes]
        distances = [route["distance"] for route in routes]

        # Step 4: Calculate actual weighted score.
        actual_score = score(
            times,
            fairness_weight=fairness_weight,
            worst_weight=worst_weight,
        )

        print(f"  Actual score: {actual_score:.2f}")

        # Step 5: Update best candidate.
        if actual_score < best_score:
            best_score = actual_score

            best = {
                "candidate": candidate,
                "score": actual_score,
                "estimated_score": estimated_score,
                "times": times,
                "distances": distances,
            }

            print("  New best meeting location!")

    return best


def main():
    origins = [
        (35.3000, -120.6600),
        (35.2700, -120.6500),
        (35.2500, -120.6800),
    ]

    candidates = [
        {"name": "Cafe A", "location": (35.2800, -120.6600)},
        {"name": "Cafe B", "location": (35.2700, -120.6700)},
        {"name": "Cafe C", "location": (35.2600, -120.6600)},
    ]

    # Mock route data for testing without API calls.
    mock_times = {
        "Cafe A": [10, 20, 30],
        "Cafe B": [17, 18, 19],
        "Cafe C": [5, 15, 35],
    }

    def mock_get_routes(origins, candidate):
        return [
            {"time": t, "distance": t * 500}
            for t in mock_times[candidate["name"]]
        ]

    best = find_best_meeting_point(
        origins,
        candidates,
        mock_get_routes,
    )

    if best:
        print("\nBest meeting location:")
        print(best["candidate"]["name"])
        print("Score:", round(best["score"], 2))
        print("Travel times:", best["times"])
        print("Travel distances:", best["distances"])
    else:
        print("No reachable meeting locations found.")


if __name__ == "__main__":
    main()

