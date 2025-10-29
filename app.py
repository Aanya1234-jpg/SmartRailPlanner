import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import joblib
from datetime import datetime, timedelta

# ---------------------- STYLING ----------------------
st.set_page_config(page_title="SmartRail Planner", page_icon="🚆", layout="centered")

st.markdown("""
<style>
/* Font Awesome for icons */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

[data-testid="stAppViewContainer"] {
    background-image: url("https://raw.githubusercontent.com/Aanya1234-jpg/SmartRailPlanner/refs/heads/main/images/train4.jpg"); /* NEW BACKGROUND */
    position: relative;
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    /* Adjusted overlay for better contrast, slightly darker white */
    background-color: rgba(255, 255, 255, 0.5); /* Was 1000,1000,1000,0.4 - changed to 255,255,255,0.5 */
    z-index: 0;
}

.block-container {
    position: relative;
    z-index: 1;
}

/* Remove default Streamlit padding so we can position freely */
main > div {
    padding-top: 0rem !important;
}

/* Make Streamlit header transparent */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* Title — positioned with margins, allowing it to scroll */
.title-container {
    margin-top: 25px;
    margin-left: 40px;
    text-align: left;
    padding-bottom: 20px;
}

.title {
    color: #4CAF50; /* Changed to a vibrant green */
    text-shadow: 2px 2px 5px rgba(0,0,0,0.8); /* Stronger shadow */
    font-family: 'Montserrat', sans-serif;
    font-size: 50px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin: 0;
}

.subtitle {
    color: #F0F0F0; /* Slightly lighter white for contrast */
    font-family: 'Raleway',Exo 2;
    font-size: 22px;
    font-weight: 400;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.7); /* Stronger shadow */
    margin-top: 4px;
}

/* Custom styling for Streamlit's selectbox and date_input labels */
.stSelectbox label, .stDateInput label {
    color: #333333 !important; /* Changed to dark grey for better readability against the light background of input box */
    font-weight: bold;
    text-shadow: none; /* Remove shadow on these labels if background is light */
}

/* Style for the dataframe headers and cells to blend better or stand out */
.stDataFrame {
    background-color: rgba(255, 255, 255, 0.95); /* Semi-transparent white for the table background */
    border-radius: 10px;
    padding: 10px;
    margin-top: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Added subtle shadow */
}
.stDataFrame .css-1dp5atx.e1tzin5v0 th { /* Target headers */
    background-color: #007bff; /* Blue header background */
    color: white; /* White header text */
    font-weight: bold;
    border-radius: 5px;
    padding: 8px;
}
.stDataFrame .css-1dp5atx.e1tzin5v0 td { /* Target cells */
    color: #333333; /* Darker text for cells */
    padding: 8px;
}

/* Additional styling for the "Plan Your Journey" container */
[data-testid="stVerticalBlock"] > div:first-child > div:first-child { /* Targets the container around "Plan Your Journey" */
    background-color: rgba(255, 255, 255, 0.95); /* More opaque for contrast */
    border-radius: 15px; /* Slightly more rounded */
    padding: 25px; /* Increased padding */
    margin-top: 30px;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25); /* Stronger shadow for depth */
}

/* Style for the 'Plan Your Journey' header itself */
.stMarkdown h3 { /* More specific selector to target H3 */
    color: #007bff !important; /* Changed to a strong blue */
    text-shadow: 1px 1px 3px rgba(0,0,0,0.4) !important; /* Softer shadow */
    font-family: 'Poppins', sans-serif;
    font-weight: 600; /* Slightly bolder */
}

/* Styling for other general markdown headers to improve visibility */
.stMarkdown h2 { /* For 'Available Route Options' */
    color: #333333; /* Dark grey */
    text-shadow: 1px 1px 2px rgba(255,255,255,0.7); /* Light shadow if background is dark */
    margin-top: 30px;
    margin-bottom: 20px;
    font-size: 1.8em;
}

.stMarkdown h3:not(.st-emotion-cache-1r6m9b6) { /* Target other H3s like 'Direct Route Found' */
    color: #28a745; /* Green for section titles */
    text-shadow: 1px 1px 2px rgba(255,255,255,0.7);
    margin-top: 25px;
    margin-bottom: 15px;
    font-size: 1.5em;
}

/* Styling for the 'Find Best Routes' button */
.stButton button {
    background-color: #007bff; /* Blue button */
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 10px 20px;
    border: none;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    transition: background-color 0.2s;
}
.stButton button:hover {
    background-color: #0056b3; /* Darker blue on hover */
}

/* Styling for the individual train detail boxes */
/* This is already inside your python code, but adding common styles here for consistency */
/* The inline styles will override these if more specific */
.train-detail-box {
    background-color: rgba(255, 255, 255, 0.98); /* Almost opaque white */
    border-radius: 12px;
    padding: 18px;
    margin-top: 12px;
    margin-bottom: 18px;
    border: 1px solid rgba(150,150,150,0.3);
    color: #212529; /* Darker font for details */
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15); /* Enhanced shadow */
}
.train-detail-box p {
    color: #212529; /* Ensure paragraph text is dark */
}
.train-detail-box p strong {
    color: #0056b3; /* Keep strong elements blue */
}
.train-detail-box i { /* Icons within the box */
    color: #28a745; /* Green icons for train details */
    margin-right: 5px;
}

/* Footer styling */
footer {
    color: #E0E0E0 !important; /* Lighter white for visibility */
    text-shadow: 1px 1px 2px rgba(0,0,0,0.6);
}

</style>
""", unsafe_allow_html=True)

# ---------------------- TITLE ----------------------
st.markdown("""
<div class="title-container">
  <div class="title">🚆 SmartRail Planner</div>
  <div class="subtitle">AI-Based Route Suggestion and Fare Estimation System</div>
</div>
""", unsafe_allow_html=True)

# ---------------------- LOAD DATA ----------------------
try:
    model = joblib.load('model/fare_model.pkl')
except FileNotFoundError:
    st.error("Error: 'fare_model.pkl' not found in 'model/' directory. Please check the path.")
    st.stop()

try:
    routes_df = pd.read_csv('data/routes.csv')
except FileNotFoundError:
    st.error("Error: 'routes.csv' not found in 'data/' directory. Please check the path.")
    st.stop()

try:
    train_data = pd.read_csv('data/train_schedule.csv')
except FileNotFoundError:
    st.error("Error: 'train_schedule.csv' not found in 'data/' directory. Please check the path.")
    st.stop()

# ---------------------- HELPER FUNCTIONS ----------------------
def predict_fare(model, distance, train_type, class_type):
    features = np.array([[distance, train_type, class_type]])
    return model.predict(features)[0]

def find_all_routes(source, destination):
    G = nx.Graph()
    for _, row in routes_df.iterrows():
        G.add_edge(row['source'], row['destination'], weight=row['distance'])
    
    if source not in G or destination not in G:
        return [], G

    return list(nx.all_simple_paths(G, source=source, target=destination, cutoff=5)), G

# ---------------------- INPUT SECTION ----------------------
with st.container():
    # Adjusted the H3 style here to match the new global H3 style in CSS
    st.markdown("<h3 style='font-family:Poppins, sans-serif;'>📍 Plan Your Journey</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        source = st.selectbox("🏁 Source Station", routes_df['source'].unique())
    with col2:
        destination = st.selectbox("🎯 Destination Station", routes_df['destination'].unique())
    with col3:
        journey_date = st.date_input("📅 Boarding Date", datetime.today())

st.markdown("")
find_btn = st.button("Find Best Routes 🚄")

# ---------------------- MAIN LOGIC ----------------------
if find_btn:
    if source == destination:
        st.warning("Source and destination cannot be the same.")
    else:
        try:
            all_paths, G = find_all_routes(source, destination)
            if not all_paths:
                st.error(f"No route found between {source} and {destination}. Please check station names.")
            else:
                st.markdown("## 🧭 Available Route Options") # H2 style from CSS

                # Direct route
                direct_trains = train_data[
                    ((train_data['source'] == source) & (train_data['destination'] == destination)) |
                    ((train_data['destination'] == source) & (train_data['source'] == destination))
                ].copy()

                if not direct_trains.empty:
                    st.markdown("<h3>🚄 Direct Route Found</h3>", unsafe_allow_html=True) # H3 style from CSS
                    cols_direct_trains = st.columns(len(direct_trains))

                    for i, (_, train) in enumerate(direct_trains.iterrows()):
                        with cols_direct_trains[i]:
                            calculated_distance = nx.shortest_path_length(G, source, destination, weight='weight')
                            
                            # Ensure train_type and class_type are numerical for prediction
                            # You might need to adjust these mappings based on your actual model training
                            train_type_numeric = train['train_type'] if isinstance(train['train_type'], int) else 1 # Default to 1 (Express)
                            class_type_numeric = train['class_type'] if isinstance(train['class_type'], int) else 1 # Default to 1 (Sleeper)

                            fare = predict_fare(model, calculated_distance, train_type_numeric, class_type_numeric)
                            time_hours = calculated_distance / train['avg_speed']
                            days = int(time_hours // 24)
                            arrival_date = journey_date + timedelta(days=days)

                            st.markdown(f"""
                               <div class="train-detail-box"> <!-- Using a class from CSS now -->
                                   <p style="margin-bottom: 5px; font-weight: bold; font-size: 1.1em;">
                                       <i class="fas fa-train"></i> Train: {train['train_name']} | Type: {'Express' if train_type_numeric==1 else ('Superfast' if train_type_numeric==2 else 'Rajdhani')} | Class: {'Sleeper' if class_type_numeric==1 else 'AC'}
                                   </p>
                                   <p style="margin-top: 0; margin-bottom: 0; font-size: 1em;">
                                       <i class="fas fa-dollar-sign"></i> Fare: ₹{round(fare,2)} |
                                       <i class="fas fa-clock"></i> Duration: {days}d {int(time_hours%24)}h |
                                       <i class="fas fa-calendar-alt"></i> Arrival: {arrival_date.strftime('%d %b %Y')}
                                   </p>
                               </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info(f"No direct trains found for the route {source} to {destination}.")

                st.markdown("---")

                # Indirect routes
                route_rows = []
                for path in all_paths:
                    if len(path) <= 2:
                        continue
                    
                    total_distance = 0
                    try:
                        total_distance = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
                    except KeyError as e:
                        st.warning(f"Could not find edge data for path segment: {e}. Skipping route {path}.")
                        continue

                    avg_speed = 80
                    hours = total_distance / avg_speed
                    days = int(hours // 24)
                    arrival_date = journey_date + timedelta(days=days)
                    
                    # Assuming a generic train_type (e.g., Superfast=2) and class (e.g., AC=2) for indirect routes
                    indirect_train_type_numeric = 2
                    indirect_class_type_numeric = 2
                    total_fare = predict_fare(model, total_distance, indirect_train_type_numeric, indirect_class_type_numeric)
                    
                    route_rows.append({
                        "Route Option": " → ".join(path),
                        "Total Distance (km)": total_distance,
                        "Approx Fare (₹)": round(total_fare, 2),
                        "Estimated Time": f"{days}d {int(hours % 24)}h",
                        "Arrival Date": arrival_date.strftime("%d %b %Y")
                    })

                if route_rows:
                    st.markdown("<h3>🚉 Indirect Routes</h3>", unsafe_allow_html=True) # H3 style from CSS
                    route_df = pd.DataFrame(route_rows)
                    st.dataframe(route_df, use_container_width=True)
                else:
                    st.info("No indirect routes available for this journey.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}. Please try again or check your inputs.")

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:white;'>© 2025 SmartRail Planner | Designed by Aanya Sinha</div>",
    unsafe_allow_html=True
)










