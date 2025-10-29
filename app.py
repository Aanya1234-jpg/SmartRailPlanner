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
    /* Removed position: relative, top, left, z-index */
    margin-top: 25px; /* Use margin for spacing from the top */
    margin-left: 40px; /* Use margin for spacing from the left */
    text-align: left;
    /* You might want a background or padding here if it conflicts with content */
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
.block-container {
    padding-top: 20px; /* Adjust if your content is too close to the subtitle */
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
model = joblib.load('model/fare_model.pkl')
routes_df = pd.read_csv('data/routes.csv')
train_data = pd.read_csv('data/train_schedule.csv')

# ---------------------- HELPER FUNCTIONS ----------------------
def predict_fare(model, distance, train_type, class_type):
    features = np.array([[distance, train_type, class_type]])
    return model.predict(features)[0]

def find_all_routes(source, destination):
    G = nx.Graph()
    for _, row in routes_df.iterrows():
        G.add_edge(row['source'], row['destination'], weight=row['distance'])
    return list(nx.all_simple_paths(G, source=source, target=destination, cutoff=5)), G

# ---------------------- INPUT SECTION ----------------------
with st.container():
    st.markdown("<h3 style='color:#5BC0EB; text-shadow: 2px 2px 5px #0A0A0A; font-family:Poppins, sans-serif;'>📍 Plan Your Journey</h3>", unsafe_allow_html=True)

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
                st.error("No route found between these stations.")
            else:
                st.markdown("## 🧭 Available Route Options")

                # Direct route
                direct_route_name = f"{source}-{destination}"
                direct_trains = train_data[train_data['route_name'].str.lower() == direct_route_name.lower()]

                if not direct_trains.empty:
                    st.markdown("### 🚄 Direct Route Found")
                    # Removed the outer div here, as each train will have its own div now

                    for _, train in direct_trains.iterrows():
                        distance = nx.shortest_path_length(G, source, destination, weight='weight')
                        fare = predict_fare(model, distance, train['train_type'], train['class_type'])
                        time_hours = distance / train['avg_speed']
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
                           ">
                               <p style="margin-bottom: 5px; font-weight: bold; color: #0056b3;">
                                   <i class="fas fa-train"></i> Train: {train['train_name']} | Type: {'Express' if train['train_type']==1 else ('Superfast' if train['train_type']==2 else 'Rajdhani')} | Class: {'Sleeper' if train['class_type']==1 else 'AC'}
                               </p>
                               <p style="margin-top: 0; margin-bottom: 0;">
                                   <i class="fas fa-dollar-sign"></i> Fare: ₹{round(fare,2)} |
                                   <i class="fas fa-clock"></i> Duration: {days}d {int(time_hours%24)}h |
                                   <i class="fas fa-calendar-alt"></i> Arrival: {arrival_date.strftime('%d %b %Y')}
                               </p>
                           </div>
                        """, unsafe_allow_html=True)
                        # End of the individual train detail box

                    st.markdown("---") # Separator for the next section if any
                # Indirect routes
                route_rows = []
                for path in all_paths:
                    if len(path) <= 2:
                        continue
                    total_distance = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
                    avg_speed = 80
                    hours = total_distance / avg_speed
                    days = int(hours // 24)
                    arrival_date = journey_date + timedelta(days=days)
                    total_fare = predict_fare(model, total_distance, 2, 2)
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
                    st.info("No indirect routes available.")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:white;'>© 2025 SmartRail Planner | Designed by Aanya Sinha</div>",
    unsafe_allow_html=True
)










