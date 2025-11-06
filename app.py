from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from main import load_and_prepare, find_nearest

app = Flask(__name__)

DATA_CSV = "Electric_Vehicle_Charging_Stations.csv"
df = load_and_prepare(DATA_CSV)
print("DEBUG: Loaded stations count:", len(df))

geolocator = Nominatim(user_agent="ev_finder_app")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

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
    elif address:
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                query_lat = location.latitude
                query_lon = location.longitude
            else:
                error = f"Could not geocode address: {address}"
        except Exception as e:
            error = f"Geocoding error: {e}"
    else:
        error = "Please provide address or latitude & longitude."

    if error:
        return render_template("results.html", error=error)

    # Find nearest stations
    nearest = find_nearest(df, query_lat, query_lon, k=k)

    # Prepare station data for Leaflet map
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

if __name__ == "__main__":
    print("Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True)
