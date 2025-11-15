from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
from main import load_and_prepare, find_nearest
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env (if present). This allows using a
# local .env file containing GEMINI_KEY during development without having to
# set OS-level environment variables manually.
load_dotenv()

app = Flask(__name__)

# --------------------------
# LOAD EV STATION DATA
# --------------------------
DATA_CSV = "Electric_Vehicle_Charging_Stations.csv"
df = load_and_prepare(DATA_CSV)
print("DEBUG: Loaded stations count:", len(df))

geolocator = Nominatim(user_agent="ev_finder_app")


# --------------------------
# HOME PAGE
# --------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# --------------------------
# RESULTS PAGE
# --------------------------
@app.route("/results", methods=["POST"])
def results():
    address = request.form.get("address", "").strip()
    lat_input = request.form.get("latitude", "").strip()
    lon_input = request.form.get("longitude", "").strip()
    k = int(request.form.get("k", 5))

    query_lat = None
    query_lon = None
    error = None

    # Prefer numeric lat/lon if provided
    if lat_input and lon_input:
        try:
            query_lat = float(lat_input)
            query_lon = float(lon_input)
        except ValueError:
            error = "Latitude/Longitude must be numeric."

    # Otherwise geocode address
    elif address:
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                query_lat = location.latitude
                query_lon = location.longitude
            else:
                # Geocoding failed — as a fallback, attempt to match the
                # address string against the station dataset (name/address/city)
                # so queries like "EV Charging Station Finder" or partial
                # station names still return useful results from the CSV.
                q = address.strip()
                if q:
                    mask = (
                        df['station_name'].str.contains(q, case=False, na=False)
                        | df['street_address'].str.contains(q, case=False, na=False)
                        | df['city'].str.contains(q, case=False, na=False)
                    )
                    matched = df[mask].head(k)
                    if not matched.empty:
                        stations = [
                            {
                                "name": r['station_name'],
                                "address": r['street_address'],
                                "city": r['city'],
                                "lat": r['latitude'],
                                "lon": r['longitude'],
                                "distance": 0.0
                            }
                            for _, r in matched.iterrows()
                        ]
                        return render_template(
                            "results.html",
                            stations=stations,
                            query_lat=None,
                            query_lon=None,
                            error=None
                        )
                error = f"Could not geocode address: {address}"
        except Exception as e:
            error = f"Geocoding error: {e}"

    else:
        error = "Please provide address or latitude & longitude."

    if error:
        # Always pass stations and query coordinates to the template to avoid
        # Jinja trying to tojson an undefined value (which causes a 500 error).
        return render_template("results.html", error=error, stations=[], query_lat=None, query_lon=None)

    # Find nearest stations
    nearest = find_nearest(df, query_lat, query_lon, k=k)

    # Prepare station data for Leaflet
    stations = [
        {
            "name": s["station_name"],
            "address": s["street_address"],
            "city": s["city"],
            "lat": s["latitude"],
            "lon": s["longitude"],
            "distance": s["distance_km"]
        }
        for s in nearest
    ]

    return render_template(
        "results.html",
        stations=stations,
        query_lat=query_lat,
        query_lon=query_lon,
        error=None
    )


# ==========================================================
#  🔥  CHATBOT BACKEND — FIXES YOUR GEMINI ERRORS 100%
# ==========================================================
# This makes Gemini API calls from SERVER (no browser issues)
# ==========================================================

# Read GEMINI API key from environment variable named GEMINI_KEY
GEMINI_KEY = os.environ.get("GEMINI_KEY")
# Optional: allow overriding the model used via GEMINI_MODEL env var
GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
# IMPORTANT: do NOT hardcode API keys in source. Set GEMINI_KEY in your environment
# Example (PowerShell): $env:GEMINI_KEY = 'YOUR_KEY_HERE'


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "invalid_json_or_no_body"}), 400

        message = data.get("message", "")

        if not message:
            return jsonify({"error": "no message"}), 400

        if not GEMINI_KEY:
            # GEMINI_KEY is not configured. Return a safe local stub so the UI still
            # works in offline/demo mode instead of returning 501.
            app.logger.warning("GEMINI_KEY not set — returning local stub for /chat")
            stub_reply = {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        "Demo mode: chat is running locally because no GEMINI_KEY is set. "
                                        "I can answer simple questions about the app or how to use it. "
                                        "Set the GEMINI_KEY environment variable to enable live AI responses."
                                    )
                                }
                            ]
                        }
                    }
                ]
            }
            return jsonify(stub_reply), 200

        # Choose model: prefer GEMINI_MODEL env override, otherwise default
        model = GEMINI_MODEL or "gemini-1.5-flash"

        # Normalize model path: some model names returned by ListModels are already
        # prefixed with 'models/', while env var may contain a short name. Build
        # the correct REST path accordingly.
        def model_path(name: str) -> str:
            return name if name.startswith("models/") else f"models/{name}"

        # Try the generateContent endpoint (used by some Gemini models).
        url = f"https://generativelanguage.googleapis.com/v1/{model_path(model)}:generateContent?key={GEMINI_KEY}"

        body = {
            "contents": [
                {"parts": [{"text": message}]}
            ]
        }

        try:
            r = requests.post(url, json=body, timeout=10)
            r.raise_for_status()
            return jsonify(r.json())

        except requests.HTTPError as e:
            # Include response content when available for easier debugging
            resp_text = e.response.text if e.response is not None else ""
            status_code = e.response.status_code if e.response is not None else 500
            app.logger.error("HTTPError calling Gemini API: %s %s", e, resp_text)

            # If the model/endpoint is not found (404), call ListModels to surface
            # available models for this key and return them back to the client so
            # a proper model can be selected.
            if status_code == 404:
                try:
                    list_url = f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_KEY}"
                    lm = requests.get(list_url, timeout=10)
                    lm.raise_for_status()
                    models_info = lm.json()
                    app.logger.info("ListModels returned %s", models_info)

                    # Try to pick a supported model automatically: prefer the first
                    # model that advertises support for generateContent.
                    models_list = models_info.get("models", [])
                    candidate = None
                    for m in models_list:
                        # different providers/versions may use different field names
                        methods = m.get("supportedGenerationMethods") or m.get("supportedMethods") or []
                        if "generateContent" in methods:
                            candidate = m
                            break

                    if candidate is not None:
                        chosen = candidate.get("name")
                        app.logger.info("Auto-selected model %s and retrying generateContent", chosen)
                        try:
                            retry_url = f"https://generativelanguage.googleapis.com/v1/{model_path(chosen)}:generateContent?key={GEMINI_KEY}"
                            rr = requests.post(retry_url, json=body, timeout=10)
                            rr.raise_for_status()
                            return jsonify(rr.json())
                        except requests.RequestException:
                            app.logger.exception("Retry with auto-selected model failed")

                    # If auto-selection failed, return the list so the user can choose
                    return jsonify({
                        "error": "model_not_found",
                        "details": "Requested model or method not found. See available models.",
                        "available_models": models_info
                    }), 404

                except requests.RequestException:
                    app.logger.exception("Failed to call ListModels after 404")
                    # Fall through to return original error info if list models fails

            return jsonify({
                "error": "http_error",
                "details": str(e),
                "resp_text": resp_text
            }), status_code

        except requests.RequestException as e:
            app.logger.exception("RequestException calling Gemini API")
            return jsonify({
                "error": "request_failed",
                "details": str(e)
            }), 500

    except Exception as e:
        # Catch-all to avoid unhandled 500s and provide a consistent JSON response
        app.logger.exception("Unhandled exception in /chat handler")
        return jsonify({"error": "server_error", "details": str(e)}), 500


# --------------------------
# RUN SERVER
# --------------------------
if __name__ == "__main__":
    print("Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True)
