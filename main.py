# Runs the full process

from places import find_places
from routes import get_routes
from search import find_best_meeting_point

origins = [
    (35.3000, -120.6600),
    (35.2700, -120.6500),
    (35.2500, -120.6800),
]

# Get candidate meeting locations from Google.
candidates = find_places(
    query="coffee shops in San Luis Obispo, CA",
    max_results=10,
)

# This function will come from routes.py.
# from routes import get_routes

best = find_best_meeting_point(
    origins=origins,
    candidates=candidates,
    get_routes=get_routes,
)

print(best)
