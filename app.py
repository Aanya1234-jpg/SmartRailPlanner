import streamlit as st
import pandas as pd
from datetime import datetime
from route_optimizer import find_routes
from fare_model import estimate_fare

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="SmartRail Planner", layout="wide")

# ------------------ CUSTOM STYLING ------------------
st.markdown(
    """
    <style>
    /* Remove Streamlit default padding and menu */
    #MainMenu, header, footer {visibility: hidden;}

    /* Body background */
    [data-testid="stAppViewContainer"] {
        background-color: #f4f6f9;
    }

    /* App title top-left */
    .title-container {
        position: absolute;
        top: 20px;
        left: 40px;
        font-size: 48px;
        font-weight: 800;
        color: #0078D7;
        font-family: 'Trebuchet MS', sans-serif;
        letter-spacing: 1px;
    }

    /* Subtitle centered */
    .subtitle {
        text-align: center;
        font-size: 22px;
        color: #333333;
        margin-top: 80px;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Input box styling */
    .input-box {
        background-color: white;
        border-radius: 20px;
        padding: 30px;
        width: 70%;
        margin: 40px auto;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    }

    /* Buttons */
    .stButton>button {
        background-color: #0078D7;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 45px;
        width: 100%;
    }

    .stButton>button:hover {
        background-color: #005fa3;
        color: #ffffff;
    }

    /* Results */
    .result-box {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ HEADER ------------------
st.markdown("<div class='title-container'>🚆 SmartRail Planner</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-Based Route Suggestion and Fare Estimation System</div>", unsafe_allow_html=True)

# ------------------ INPUT SECTION ------------------
st.markdown("<div class='input-box'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    source = st.selectbox("🚉 Source Station", ["Delhi", "Mumbai", "Bhopal", "Hyderabad", "Bangalore", "Kolkata"])
with col2:
    destination = st.selectbox("🎯 Destination Station", ["Delhi", "Mumbai", "Bhopal", "Hyderabad", "Bangalore", "Kolkata"])
with col3:
    date = st.date_input("📅 Boarding Date", datetime.today())

st.write("")
find_button = st.button("Find Best Routes 🚄")
st.markdown("</div>", unsafe_allow_html=True)

# ------------------ ROUTE DISPLAY ------------------
if find_button:
    if source == destination:
        st.warning("⚠️ Source and destination cannot be the same.")
    else:
        st.markdown("<h4 style='text-align:center; color:#0078D7;'>Available Route Options</h4>", unsafe_allow_html=True)

        try:
            routes = find_routes(source, destination)
            if not routes:
                st.error("No routes found. Please try another combination.")
            else:
                for i, route in enumerate(routes, 1):
                    fare = estimate_fare(route['distance'])
                    st.markdown(
                        f"""
                        <div class='result-box'>
                        <b>Route Option {i}:</b> {route['path']} <br>
                        🚄 <b>Distance:</b> {route['distance']} km |
                        💰 <b>Estimated Fare:</b> ₹{fare:.2f} |
                        ⏱️ <b>Duration:</b> {route['duration']} |
                        📅 <b>Arrival:</b> {route['arrival_date']}
                        </div><br>
                        """,
                        unsafe_allow_html=True
                    )
        except Exception as e:
            st.error(f"Error occurred: {e}")
