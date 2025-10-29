from datetime import date, timedelta
import pandas as pd
import streamlit as st
from route_optimizer import find_shortest_route
from fare_model import load_model, predict_fare

st.set_page_config(page_title="SmartRail Planner", layout="centered")
st.title("🚆 SmartRail Planner — AI Route & Fare Estimator")

model = load_model('model/fare_model.pkl')
df_routes = pd.read_csv('data/routes.csv')
stations = sorted(list(set(df_routes['source']).union(set(df_routes['destination']))))
train_data = pd.read_csv('data/train_schedule.csv')

with st.form("route_form"):
    source = st.selectbox("Source Station", stations)
    destination = st.selectbox("Destination Station", stations, index=stations.index(stations[-1]) if len(stations)>1 else 0)
    journey_date = st.date_input("Select Journey Date", min_value=date.today())
    arrival_date = st.date_input("Select Expected Arrival Date (manually)", min_value=journey_date)
    submitted = st.form_submit_button("Show Train Options")
if submitted:
    if source == destination:
        st.warning("Source and destination cannot be the same.")
    else:
        route, distance = find_shortest_route(source, destination, 'data/routes.csv')
        if route is None:
            st.error("No route found between the selected stations.")
        else:
            st.success("Available Train Options:")
            st.write(f"**Route:** {' → '.join(route)}")
            st.write(f"**Total Distance:** {distance} km")

            # Calculate estimated duration based on average speed (hours = distance/speed)
            table_data = []
            for _, train in train_data.iterrows():
                travel_hours = distance / train['avg_speed']
                travel_days = int(travel_hours // 24)
                travel_time_str = f"{int(travel_hours//24)}d {int(travel_hours%24)}h"

                fare = predict_fare(model, distance, train['train_type'], train['class_type'])
                table_data.append({
                    "Train Name": train['train_name'],
                    "Type": "Express" if train['train_type']==1 else ("Superfast" if train['train_type']==2 else "Rajdhani"),
                    "Class": "Sleeper" if train['class_type']==1 else "AC",
                    "Boarding Date": journey_date.strftime("%d %b %Y"),
                    "Arrival Date": arrival_date.strftime("%d %b %Y"),
                    "Duration": travel_time_str,
                    "Estimated Fare (₹)": round(fare, 2)
                })

            result_df = pd.DataFrame(table_data)
            st.dataframe(result_df)

