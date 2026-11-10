# AI Meeting Point Selector

A Python application that finds a convenient and fair meeting location for a group of people based on their starting addresses and a user-defined search query.

The application uses Google Maps APIs to identify candidate venues, estimate travel times, and recommend a meeting location using a weighted multi-objective cost function.

## Algorithm

The goal is to minimize total group travel time while keeping individual travel times relatively balanced.

We use the following weighted objective function:

```text
J = T + α(N × MAD) + β(N × M)
```

Where:

- **J** = Total weighted cost
- **T** = Sum of all participants' travel times
- **N** = Number of participants
- **MAD** = Mean Absolute Deviation of travel times
- **M** = Maximum individual travel time
- **α** = Weight controlling travel-time fairness
- **β** = Weight penalizing the longest travel time

The algorithm uses **greedy best-first search** to prioritize candidate meeting locations based on their estimated weighted cost.

1. Retrieve candidate meeting locations from the Google Places API.
2. Estimate travel times using straight-line distances (Haversine formula).
3. Calculate an estimated weighted cost for each candidate.
4. Insert candidates into a min-priority queue.
5. Evaluate candidates in order of estimated cost using the Google Routes API.
6. Calculate the actual weighted cost and track the best meeting location.

The algorithm supports limiting the number of evaluated candidates to reduce API usage. Evaluating all candidates finds the lowest-cost location among the returned candidates, while limiting evaluations does not guarantee the optimal result.

## Project Structure

```text
AI-meeting-point-selector/
├── app.py             # Flask web application
├── places.py          # Google Places API integration
├── routes.py          # Google Routes API integration
├── search.py          # Greedy best-first search
├── selector.py        # Weighted objective function
├── tests/             # Test APIs
│   ├── test_places.py
│   ├── test_routes.py
│   └── test_geocoding.py
├── requirements.txt   # Python dependencies
├── .env.example       # Example environment configuration
├── .env               # Local API key (not committed)
├── .gitignore
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/avaquinn/AI-meeting-point-selector.git
cd AI-meeting-point-selector
```

### 2. Create a virtual environment

Python 3 is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

The application uses:

- `requests` — HTTP requests to Google APIs
- `python-dotenv` — Local environment variable management
- `flask` — Web application framework

### 3. Configure Google Maps APIs

Create a project in [Google Cloud Console](https://console.cloud.google.com/) and enable billing.

Enable the following APIs:

| API | Purpose |
|---|---|
| Geocoding API | Convert user-provided addresses into coordinates |
| Places API (New) | Search for candidate meeting locations |
| Routes API | Calculate driving times and distances |

Create an API key under **APIs & Services → Credentials**.

Ensure the API key is authorized to access all three services and that the APIs are enabled in the project.

**Note:** Google Maps Platform uses usage-based billing. Set appropriate API quotas and billing alerts to control costs. Billing alerts alone do not automatically stop charges.

#### API Tests

The `tests/` directory contains standalone scripts for verifying
Google Maps API functionality.

- `test_places.py` — Tests candidate location searches.
- `test_routes.py` — Tests driving-time and distance calculations.
- `test_geocoding.py` — Tests address-to-coordinate conversion.

Run tests individually using:

python3 tests/test_places.py  
python3 tests/test_routes.py  
python3 tests/test_geocoding.py  

### 4. Configure environment variables

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Add your Google API key:

```dotenv
GOOGLE_API_KEY=your_api_key_here
```

Do not commit `.env` or API keys to the repository.

### 5. Run the application

Start the Flask server:

```bash
python3 app.py
```

Navigate to:

http://127.0.0.1:4242

The default port can be changed in `app.py`.

To stop the server, press `Ctrl+C`.

To deactivate the virtual environment:

```bash
deactivate
```

## Usage

1. Enter 2–5 starting addresses, one per line.
2. Enter a search query (e.g., `coffee shops in San Luis Obispo, CA`).
3. Click **Find Meeting Point**.
4. View the recommended location, weighted score, and individual travel times and distances.

The current implementation uses driving routes.

## Configuration

The search behavior can be adjusted using the following parameters:

| Parameter | Default | Description |
|---|---|---|
| `fairness_weight` | `0.7` | Weight applied to travel-time MAD |
| `worst_weight` | `0.3` | Weight applied to the longest travel time |
| `max_evaluations` | `5` (web app) | Maximum candidates evaluated using actual routing data |
| `max_results` | `10` | Maximum venues requested from Places API |

These parameters can be adjusted in `app.py` and passed to the search function.

## Contributors

- Nithyasri Palanisamy
- Ava Quinn
- Rucha Ranade
