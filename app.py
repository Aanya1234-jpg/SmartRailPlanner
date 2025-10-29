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
    background-image: url("https://i.ibb.co/dfSR6Sg/train-bg.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Add dark overlay for readability */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.55); /* dark layer */
    z-index: -1;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* Title Styling */
.title {
    text-align: left;
    color: #00C8FF;
    font-size: 70px;
    font-weight: 900;
    text-shadow: 4px 4px 10px black;
    margin-left: 50px;
    margin-top: 25px;
}

/* Subtitle */
.subtitle {
    text-align: left;
    color: #f0f0f0;
    font-size: 22px;
    margin-left: 50px;
    margin-bottom: 40px;
}

/* Card-like sections for readability */
.block-container {
    background-color: rgba(255, 255, 255, 0.12);
    padding: 20px;
    border-radius: 15px;
}

/* Buttons */
.stButton>button {
    background-color: #00C8FF;
    color: white;
    font-size: 18px;
    font-weight: 600;
    border-radius: 12px;
    border: none;
}
.stButton>button:hover {
    background-color: #0086c3;
}

/* Route Cards */
.route-card {
    background-color: rgba(255, 255, 255, 0.8);
    padding: 18px;
    border-radius: 15px;
    margin-bottom: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.4);
}
</style>
""", unsafe_allow_html=True)


# ---------------------- TITLE ----------------------
st.markdown('<div class="title">🚆 SmartRail Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Based Route Suggestion and Fare Estimation System</div>', unsafe_allow_html=True)

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
    st.markdown("### 📍 Plan Your Journey")
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
                    st.markdown('<div class="route-card">', unsafe_allow_html=True)
                    st.markdown("### 🚄 Direct Route Found")
                    for _, train in direct_trains.iterrows():
                        distance = nx.shortest_path_length(G, source, destination, weight='weight')
                        fare = predict_fare(model, distance, train['train_type'], train['class_type'])
                        time_hours = distance / train['avg_speed']
                        days = int(time_hours // 24)
                        arrival_date = journey_date + timedelta(days=days)
                        st.write(f"**Train:** {train['train_name']} | "
                                 f"**Type:** {'Express' if train['train_type']==1 else ('Superfast' if train['train_type']==2 else 'Rajdhani')} | "
                                 f"**Class:** {'Sleeper' if train['class_type']==1 else 'AC'}")
                        st.write(f"💰 Fare: ₹{round(fare,2)} | ⏱ Duration: {days}d {int(time_hours%24)}h | 📅 Arrival: {arrival_date.strftime('%d %b %Y')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")

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




