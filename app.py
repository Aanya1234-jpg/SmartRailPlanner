import streamlit as st
from route_optimizer import find_shortest_route
from fare_model import load_model, predict_fare
import pandas as pd

st.set_page_config(page_title="SmartRail Planner", layout="centered")
st.title("SmartRail Planner — AI Route & Fare Estimator")

# Load model
model = load_model('model/fare_model.pkl')

# Load station list from routes.csv
df_routes = pd.read_csv('data/routes.csv')
stations = sorted(list(set(df_routes['source']).union(set(df_routes['destination']))))

with st.form("route_form"):
    source = st.selectbox("Source Station", stations)
    destination = st.selectbox("Destination Station", stations, index=stations.index(stations[-1]) if len(stations)>1 else 0)
    train_type = st.selectbox("Train Type", [("Express",1), ("Superfast",2), ("Premium",3)], format_func=lambda x: x[0])
    class_type = st.selectbox("Class", [("Sleeper",1), ("AC",2)], format_func=lambda x: x[0])
    submitted = st.form_submit_button("Find Route")

if submitted:
    if source == destination:
        st.warning("Source and destination cannot be the same.")
    else:
        route, distance = find_shortest_route(source, destination, 'data/routes.csv')
        if route is None:
            st.error("No route found between the selected stations.")
        else:
            st.success("Route found!")
            st.write("**Route:**", " → ".join(route))
            st.write("**Total Distance (km):**", distance)
            fare = predict_fare(model, distance, train_type[1], class_type[1])
            st.write("**Estimated Fare (₹):**", fare)
