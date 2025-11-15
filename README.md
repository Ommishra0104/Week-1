EV Vehicle Charging Station Finder Web App

The EV Vehicle Charging Station Finder Web App is an advanced Python + Flask-based application designed to help electric vehicle (EV) users quickly find the nearest charging stations.
This updated version introduces an integrated AI chatbot, enhanced user interface, improved backend logic, and optimized geolocation processing for faster and more accurate results.

Users can enter their address or GPS coordinates, get the nearest charging stations instantly, and see them on an interactive map generated automatically.

🌍 Project Overview

As EV adoption continues to grow, easy access to charging stations is essential.
This upgraded system provides a smart, automated, and user-friendly web platform that uses:

Geospatial analysis

AI chatbot assistance

Clean UI/UX

Flask backend processing

to help users locate EV charging stations effortlessly.

With the updated version, users can:

Enter address or latitude/longitude

View nearest charging stations

Access chatbot assistance

See real-time map visualization

Experience faster and smoother search operations

🧠 New & Updated Features
✅ AI Chatbot Integration

Provides help, guidance, FAQs, and user support.

✅ Improved Geolocation Search

More accurate address → coordinate conversion.

✅ Nearest Station Finder

Displays the closest EV charging stations using optimized logic.

✅ Interactive Map (Folium)

Shows station details, markers, and distance.

✅ Enhanced UI

Modern and mobile-friendly user interface.

✅ CSV Dataset Integration

Reads and analyzes EV dataset for nearest station matching.

✅ Error-Free Backend

Strong exception handling across all processes.

🛠️ Technologies Used
Category	Tools / Libraries
Backend	Python, Flask
Data Handling	Pandas
Geolocation	Geopy
Mapping	Folium
Frontend	HTML, CSS
Chatbot	Custom AI Chatbot Integration
Environment	Python venv
Version Control	Git & GitHub
📁 Folder Structure
EV_VEHICLES/
│
├── app.py                          # Flask main application (with chatbot)
├── main.py                         # Core logic: dataset load + nearest station
├── Electric_Vehicle_Charging_Stations.csv   # Dataset
│
├── templates/
│   ├── index.html                  # Homepage UI
│   ├── map.html                    # Map display page
│   └── results.html                # Results display
│
└── static/
    ├── style.css                   # Styling
    └── assets/                     # Images / icons

⚙️ How to Run Locally
1️⃣ Clone the Repository
git clone https://github.com/Ommishra0104/EV-Vehicle-Charging-Station-Finder-Web-App.git

cd EV-Vehicle-Charging-Station-Finder-Web-App

2️⃣ Create a Virtual Environment
python -m venv ev_env
ev_env\Scripts\activate     # For Windows

3️⃣ Install Required Libraries
pip install -r requirements.txt


Or manually:

pip install flask pandas geopy folium scikit-learn

4️⃣ Start the Flask Server
python app.py

5️⃣ Open in Browser
http://127.0.0.1:5000

📊 Dataset Information

Dataset used: Electric_Vehicle_Charging_Stations.csv

Includes:

Station Name

Address

City

Latitude, Longitude

Charger Levels (Level 1 / Level 2 / DC Fast)

Location metadata

The system performs nearest-station detection using geographic distance calculations.

🚀 Future Enhancements

Real-time station availability

Google Maps or Mapbox integration

Voice-enabled chatbot

User login and personalized dashboard

Filters for distance and charger type

Mobile app version

Advanced EV route planning

Charging price comparison

👨‍💻 Author

Om Mishra
B.Tech (ECE) | Developer & Innovator
🔥 Passionate about EV technology, automation, AI, and smart mobility solutions.
