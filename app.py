
import os

import requests
from dotenv import load_dotenv
from flask import Flask, request, render_template_string

from places import find_places
from routes import get_routes
from search import find_best_meeting_point

load_dotenv()
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MeetPoint</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 60px auto;
            padding: 0 20px;
            background: #f6f7f9;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        input, textarea, button {
            width: 100%;
            padding: 12px;
            margin: 8px 0 18px;
            box-sizing: border-box;
            font: inherit;
        }
        button {
            background: #2563eb;
            color: white;
            border: 0;
            border-radius: 6px;
            cursor: pointer;
        }
        .error { color: #b91c1c; }
        .result { background: #e9f7ee; }
    </style>
</head>
<body>
    <h1>MeetPoint</h1>
    <p>Find the best meeting location for your group.</p>

    <div class="card">
        <form method="POST">
            <label>Starting addresses (one per line)</label>
            <textarea name="origins" rows="5" required
                placeholder="1 Grand Ave, San Luis Obispo, CA&#10;751 Palm St, San Luis Obispo, CA">{{ origin_text }}</textarea>

            <label>Search query</label>
            <input name="query" value="{{ query }}" required>

            <button type="submit">Find Meeting Point</button>
        </form>
    </div>

    {% if error %}
        <div class="card error">{{ error }}</div>
    {% endif %}

    {% if result %}
        <div class="card result">
            <h2>{{ result.candidate.name }}</h2>
            <p>Weighted score: {{ "%.2f"|format(result.score) }}</p>

            <h3>Individual Travel</h3>
            <ul>
            {% for time, distance in travels %}
                <li>
                    Person {{ loop.index }}:
                    {{ "%.1f"|format(time) }} min,
                    {{ "%.2f"|format(distance / 1000) }} km
                </li>
            {% endfor %}
            </ul>
        </div>
    {% endif %}
</body>
</html>
"""


def geocode(address):
    """Convert an address into (latitude, longitude)."""
    response = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params={
            "address": address,
            "key": os.environ["GOOGLE_API_KEY"],
        },
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()

    if data.get("status") != "OK":
        raise ValueError(
            f"Could not geocode '{address}': "
            f"{data.get('error_message', data.get('status'))}"
        )

    location = data["results"][0]["geometry"]["location"]
    return (location["lat"], location["lng"])


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    travels = []

    origin_text = ""
    query = "coffee shops in San Luis Obispo, CA"

    if request.method == "POST":
        origin_text = request.form.get("origins", "")
        query = request.form.get("query", "").strip()

        addresses = [
            address.strip()
            for address in origin_text.splitlines()
            if address.strip()
        ]

        try:
            if not 2 <= len(addresses) <= 5:
                raise ValueError("Enter 2 to 5 starting addresses.")
            if not query:
                raise ValueError("Enter a search query.")

            origins = [geocode(address) for address in addresses]
            candidates = find_places(query=query, max_results=10)

            if not candidates:
                raise ValueError("No meeting locations found.")

            result = find_best_meeting_point(
                origins=origins,
                candidates=candidates,
                get_routes=get_routes,
                fairness_weight=0.7,
                worst_weight=0.3,
                max_evaluations=5,
            )

            if result is None:
                raise ValueError("No reachable meeting point found.")

            travels = list(zip(
                result["times"],
                result["distances"],
            ))

        except (ValueError, requests.RequestException) as exc:
            error = str(exc)

    return render_template_string(
        HTML,
        result=result,
        error=error,
        travels=travels,
        origin_text=origin_text,
        query=query,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=4242)

