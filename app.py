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
    background-image: url("https://raw.githubusercontent.com/Aanya1234-jpg/SmartRailPlanner/refs/heads/main/images/train3.png");
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
    background-color: rgba(255, 255, 255, 0.4); /* adjust opacity */
    z-index: 0;
}

/* Ensure block-container doesn't interfere with top positioning */
.block-container {
    position: relative;
    z-index: 1;
    /* Adjust top padding if needed, but title-container handles its own margin */
    /* padding-top: 20px;  - Removed this from .block-container for now to let title be higher */
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
    margin-top: 25px; /* Pushes it down from the very top */
    margin-left: 40px; /* Pushes it right from the very left */
    text-align: left;
    padding-bottom: 20px; /* Space below subtitle */
}

.title {
    color: #FFD700;
    text-shadow: 2px 2px 5px #000;
    font-family: 'Montserrat', sans-serif;
    font-size: 50px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin: 0;
}

.subtitle {
    color: #E0E0E0;
    font-family: 'Raleway',Exo 2;
    font-size: 22px;
    font-weight: 400;
    text-shadow: 1px 1px 3px #000;
    margin-top: 4px;
}

/* Custom styling for Streamlit's selectbox and date_input labels */
.stSelectbox label, .stDateInput label {
    color: white !important; /* Makes labels white */
    font-weight: bold;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
}

/* Style for the dataframe headers and cells to blend better or stand out */
.stDataFrame {
    background-color: rgba(255, 255, 255, 0.95); /* Semi-transparent white for the table background */
    border-radius: 10px;
    padding: 10px;
    margin-top: 20px; /* Add margin to separate from content above */
}
.stDataFrame .css-1dp5atx.e1tzin5v0 th { /* Target headers */
    background-color: #007bff; /* Blue header background */
    color: white; /* White header text */
    font-weight: bold;
    border-radius: 5px;
    padding: 8px; /* Add padding to headers */
}
.stDataFrame .css-1dp5atx.e1tzin5v0 td { /* Target cells */
    color: #333333; /* Darker text for cells */
    padding: 8px; /* Add padding to cells */
}

/* Additional styling for the "Plan Your Journey" container */
[data-testid="stVerticalBlock"] > div:first-child > div:first-child { /* Targets the container around "Plan Your Journey" */
    background-color: rgba(255, 255, 255, 0.9); /* A slightly less transparent white */
    border-radius: 10px;
    padding: 20px;
    margin-top: 30px; /* Space from content above, will cause input section to scroll */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

/* Style for the 'Plan Your Journey' header itself */
h3 {
    text-shadow: 2px 2px 5px rgba(0,0,0,0.7) !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------- TITLE ----------------------
# This is correctly structured to scroll with content when margins are used.
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
    # Mapping logic for train_type and class_type
    train_type_map = {1: 'Express', 2: 'Superfast', 3: 'Rajdhani'}
    class_type_map = {1: 'Sleeper', 2: 'AC'}

    # If your model was trained on numerical labels, convert them back for display
    # This function is for prediction, so it should take numerical if model expects it
    # Assuming the 'train_type' and 'class_type' passed to this function are already numerical (1, 2, 3)
    features = np.array([[distance, train_type, class_type]])
    return model.predict(features)[0]

def find_all_routes(source, destination):
    G = nx.Graph()
    for _, row in routes_df.iterrows():
        G.add_edge(row['source'], row['destination'], weight=row['distance'])
    
    if source not in G or destination not in G:
        return [], G # Return empty paths if either node is missing

    return list(nx.all_simple_paths(G, source=source, target=destination, cutoff=5)), G

# ---------------------- INPUT SECTION ----------------------
# This `st.container()` will now have the additional styling from the CSS above
with st.container():
    st.markdown("<h3 style='color:#00E0FF; text-shadow: 2px 2px 5px #0A0A0A; font-family:Poppins, sans-serif;'>📍 Plan Your Journey</h3>", unsafe_allow_html=True)

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
                st.markdown("## 🧭 Available Route Options")

                # Direct route
                # Filter train_data for routes that match source-destination exactly
                direct_trains = train_data[
                    ((train_data['source'] == source) & (train_data['destination'] == destination)) |
                    ((train_data['destination'] == source) & (train_data['source'] == destination)) # Also check reverse route
                ].copy() # Use .copy() to avoid SettingWithCopyWarning


                if not direct_trains.empty:
                    st.markdown("### 🚄 Direct Route Found")
                    # Use a Streamlit column layout for side-by-side display if multiple direct trains
                    cols_direct_trains = st.columns(len(direct_trains))

                    for i, (_, train) in enumerate(direct_trains.iterrows()):
                        with cols_direct_trains[i]: # Place each train detail in its own column
                            calculated_distance = nx.shortest_path_length(G, source, destination, weight='weight')

                            # Assuming 'train_type' and 'class_type' columns in your CSV are already numerical
                            # If they are strings, you'll need to map them here before passing to predict_fare
                            train_type_numeric = train['train_type'] # Assuming 'train_type' column in CSV is 1, 2, or 3
                            class_type_numeric = train['class_type'] # Assuming 'class_type' column in CSV is 1 or 2

                            fare = predict_fare(model, calculated_distance, train_type_numeric, class_type_numeric)
                            time_hours = calculated_distance / train['avg_speed']
                            days = int(time_hours // 24)
                            arrival_date = journey_date + timedelta(days=days)

                            # Start of the individual train detail box
                            st.markdown(f"""
                               <div style="
                                   background-color: rgba(255, 255, 255, 0.95); /* Adjusted for better visibility */
                                   border-radius: 10px;
                                   padding: 15px;
                                   margin-top: 10px; /* Adjust spacing between rows of direct trains */
                                   margin-bottom: 15px;
                                   border: 1px solid rgba(200,200,200,0.5);
                                   color: #333333; /* Darker text for readability */
                                   box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
                               ">
                                   <p style="margin-bottom: 5px; font-weight: bold; color: #0056b3; font-size: 1.1em;">
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

                st.markdown("---") # Separator after direct routes

                # Indirect routes
                route_rows = []
                for path in all_paths:
                    if len(path) <= 2: # Skip direct paths, as they are handled above
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
                    
                    indirect_train_type_numeric = 2 # Superfast for indirect example
                    indirect_class_type_numeric = 2 # AC for indirect example
                    total_fare = predict_fare(model, total_distance, indirect_train_type_numeric, indirect_class_type_numeric)
                    
                    route_rows.append({
                        "Route Option": " → ".join(path),
                        "Total Distance (km)": total_distance,
                        "Approx Fare (₹)": round(total_fare, 2),
                        "Estimated Time": f"{days}d {int(hours % 24)}h",
                        "Arrival Date": arrival_date.strftime("%d %b %Y")
                    })

                if route_rows:
                    st.markdown("### 🚉 Indirect Routes")
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
