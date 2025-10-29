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
    background-image: url("https://raw.githubusercontent.com/Aanya1234-jpg/SmartRailPlanner/refs/heads/main/images/train4.jpg");
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

.block-container {
    position: relative;
    z-index: 1;
}

/* Remove default Streamlit padding so we can position freely */
main > div {
    padding-top: 0rem !important; /* Keep this to control overall top padding */
}

/* Make Streamlit header transparent */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* Title — now uses margin/padding to position it, allowing it to scroll */
.title-container {
    margin-top: 25px; /* Use margin for spacing from the top */
    margin-left: 40px; /* Use margin for spacing from the left */
    text-align: left;
    padding-bottom: 20px; /* Add some space below the subtitle */
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

/* Add a bit of top padding to the content area itself if needed */
/* This will affect all .block-container elements, including your input fields */
.block-container {
    padding-top: 20px; /* Adjust if your content is too close to the subtitle */
}

/* Custom styling for Streamlit's selectbox and date_input labels */
.stSelectbox label, .stDateInput label {
    color: white !important; /* Makes labels white */
    font-weight: bold;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
}

/* Style for the dataframe headers and cells to blend better or stand out */
/* Target the dataframe container directly */
.stDataFrame {
    background-color: rgba(255, 255, 255, 0.95); /* Semi-transparent white for the table background */
    border-radius: 10px;
    padding: 10px;
}
/* Style for dataframe headers */
.stDataFrame .css-1dp5atx.e1tzin5v0 th {
    background-color: #007bff; /* Blue header background */
    color: white; /* White header text */
    font-weight: bold;
    border-radius: 5px;
}
/* Style for dataframe cells */
.stDataFrame .css-1dp5atx.e1tzin5v0 td {
    color: #333333; /* Darker text for cells */
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
# Ensure your model and data paths are correct relative to where you run the script
try:
    model = joblib.load('model/fare_model.pkl')
except FileNotFoundError:
    st.error("Error: 'fare_model.pkl' not found in 'model/' directory. Please check the path.")
    st.stop() # Stop execution if model is not found

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
    # Map train_type and class_type strings to numerical values if your model expects them
    # Assuming 'Express': 1, 'Superfast': 2, 'Rajdhani': 3
    # Assuming 'Sleeper': 1, 'AC': 2
    # Your predict_fare function in the original code seems to assume numerical inputs directly
    # Adjust if your actual model expects string categories
    if isinstance(train_type, str):
        train_type_map = {'Express': 1, 'Superfast': 2, 'Rajdhani': 3}
        train_type_val = train_type_map.get(train_type, 1) # Default to Express if not found
    else:
        train_type_val = train_type

    if isinstance(class_type, str):
        class_type_map = {'Sleeper': 1, 'AC': 2}
        class_type_val = class_type_map.get(class_type, 1) # Default to Sleeper if not found
    else:
        class_type_val = class_type

    features = np.array([[distance, train_type_val, class_type_val]])
    return model.predict(features)[0]

def find_all_routes(source, destination):
    G = nx.Graph()
    for _, row in routes_df.iterrows():
        G.add_edge(row['source'], row['destination'], weight=row['distance'])
    
    # Check if source and destination exist in the graph
    if source not in G or destination not in G:
        return [], G # Return empty paths if either node is missing

    return list(nx.all_simple_paths(G, source=source, target=destination, cutoff=5)), G

# ---------------------- INPUT SECTION ----------------------
with st.container():
    st.markdown("<h3 style='color:#00E0FF; font-family:Poppins, sans-serif;'>📍 Plan Your Journey</h3>", unsafe_allow_html=True)

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
                direct_route_name = f"{source}-{destination}"
                # Filter train_data for routes that match source-destination exactly
                direct_trains = train_data[
                    ((train_data['source'] == source) & (train_data['destination'] == destination)) |
                    ((train_data['source'] == destination) & (train_data['destination'] == source)) # Also check reverse route
                ]


                if not direct_trains.empty:
                    st.markdown("### 🚄 Direct Route Found")
                    # Removed the outer div here, as each train will have its own div now

                    for _, train in direct_trains.iterrows():
                        # Ensure distance calculation uses the correct source/destination order if route is reversed
                        calculated_distance = nx.shortest_path_length(G, source, destination, weight='weight')

                        # Pass numerical values to predict_fare based on your model's training
                        # Assuming train_type: Express=1, Superfast=2, Rajdhani=3 (your current code suggests this)
                        # Assuming class_type: Sleeper=1, AC=2 (your current code suggests this)
                        train_type_numeric = 1 # Default to Express
                        if 'Express' in train['train_name']: # Simple heuristic, adjust as needed
                             train_type_numeric = 1
                        elif 'Superfast' in train['train_name']:
                             train_type_numeric = 2
                        elif 'Rajdhani' in train['train_name']:
                             train_type_numeric = 3
                        # Use train['train_type'] directly if it's already numeric in your CSV

                        class_type_numeric = 1 # Default to Sleeper
                        if 'AC' in train['train_name'] or 'AC' in train['class_type']: # Check both columns for 'AC'
                            class_type_numeric = 2
                        # Use train['class_type'] directly if it's already numeric in your CSV


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
                               margin-top: 10px;
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
                        # End of the individual train detail box

                    st.markdown("---") # Separator for the next section if any
                else:
                    st.info(f"No direct trains found for the route {source} to {destination}.")


                # Indirect routes
                route_rows = []
                for path in all_paths:
                    if len(path) <= 2: # Skip direct paths, as they are handled above
                        continue
                    
                    # Calculate total distance for indirect paths
                    total_distance = 0
                    try:
                        total_distance = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
                    except KeyError as e:
                        st.warning(f"Could not find edge data for path segment: {e}. Skipping route {path}.")
                        continue


                    avg_speed = 80 # You might want to make this dynamic or average from train_data
                    hours = total_distance / avg_speed
                    days = int(hours // 24)
                    arrival_date = journey_date + timedelta(days=days)
                    
                    # For indirect routes, assuming a generic train_type (e.g., Express) and class (e.g., AC)
                    # Adjust these default values if you have a way to determine them for indirect segments
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
                    # The st.dataframe styling is in the <style> block now
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
