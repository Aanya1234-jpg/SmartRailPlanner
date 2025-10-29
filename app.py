import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="SmartRail Planner", layout="wide")

# ---------------------- CUSTOM STYLES ----------------------
st.markdown(
    """
    <style>
    /* App background */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://raw.githubusercontent.com/Aanya1234-jpg/SmartRailPlanner/refs/heads/main/images/train3.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        filter: brightness(90%);
    }

    /* Top-left title */
    .main-title {
        position: absolute;
        top: 30px;
        left: 40px;
        font-size: 52px;
        font-weight: 800;
        font-family: 'Poppins', sans-serif;
        color: #00BFFF;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.5);
    }

    /* Subtitle below title */
    .sub-title {
        position: absolute;
        top: 95px;
        left: 45px;
        font-size: 20px;
        color: #E0E0E0;
        font-family: 'Open Sans', sans-serif;
        font-style: italic;
    }

    /* Section Headings */
    h3, h2 {
        color: #00BFFF !important;
        text-shadow: 1px 1px 2px black;
        font-family: 'Poppins', sans-serif;
    }

    /* Boxes for routes */
    .route-box {
        background: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 15px;
        margin-top: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }

    /* Table style */
    .dataframe {
        background: white;
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------- HEADER ----------------------
st.markdown("<div class='main-title'>🚆 SmartRail Planner</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>AI-Based Route Suggestion and Fare Estimation System</div>", unsafe_allow_html=True)

# ---------------------- INPUT SECTION ----------------------
st.markdown("<h3>📍 Plan Your Journey</h3>", unsafe_allow_html=True)

stations = ["Delhi", "Bhopal", "Mumbai", "Hyderabad", "Nagpur", "Jaipur", "Bangalore", "Chennai", "Kolkata", "Pune"]

col1, col2, col3 = st.columns(3)
with col1:
    source = st.selectbox("🚉 Source", stations)
with col2:
    destination = st.selectbox("🎯 Destination", stations)
with col3:
    date = st.date_input("📅 Boarding Date", datetime.today())

find_btn = st.button("Find Best Routes 🚄")

# ---------------------- ROUTE DISPLAY ----------------------
if find_btn:
    st.markdown("<h3>🧭 Available Route Options</h3>", unsafe_allow_html=True)

    if source == destination:
        st.warning("Source and destination cannot be the same!")
    else:
        # Simulate direct and indirect routes
        routes_data = {
            ("Delhi", "Bhopal"): [
                {"train": "Express Line", "type": "Express", "class": "Sleeper", "fare": 1398.96, "duration": "11h"},
                {"train": "Express Plus", "type": "Express", "class": "AC", "fare": 1108.24, "duration": "10h"}
            ],
            ("Delhi", "Bangalore"): [
                {"train": "SuperFast", "type": "Express", "class": "AC", "fare": 2550.25, "duration": "1d 4h"},
                {"train": "Raj Express", "type": "Express", "class": "Sleeper", "fare": 1985.75, "duration": "1d 6h"}
            ],
        }

        # Direct Route Box
        st.markdown("<h2>🚆 Direct Route Found</h2>", unsafe_allow_html=True)
        st.markdown("<div class='route-box'>", unsafe_allow_html=True)
        if (source, destination) in routes_data:
            for r in routes_data[(source, destination)]:
                arrival = (date + timedelta(hours=int(r['duration'].split('h')[0]))).strftime("%d %b %Y")
                st.write(f"**Train:** {r['train']} | **Type:** {r['type']} | **Class:** {r['class']}")
                st.write(f"💰 **Fare:** ₹{r['fare']} | ⏱️ **Duration:** {r['duration']} | 📅 **Arrival:** {arrival}")
                st.markdown("---")
        else:
            st.info("No direct routes found.")
        st.markdown("</div>", unsafe_allow_html=True)

        # Indirect Routes Box
        st.markdown("<h2>🚉 Indirect Routes</h2>", unsafe_allow_html=True)
        st.markdown("<div class='route-box'>", unsafe_allow_html=True)

        # Example Indirect Routes Table
        indirect_routes = pd.DataFrame({
            "Route Option": [
                f"{source} → Jaipur → Mumbai → Nagpur → {destination}",
                f"{source} → Hyderabad → {destination}"
            ],
            "Total Distance (km)": [2360, 1840],
            "Approx Fare (₹)": [3525.22, 2680.56],
            "Estimated Time": ["1d 5h", "1d 2h"],
            "Arrival Date": [
                (date + timedelta(days=1, hours=5)).strftime("%d %b %Y"),
                (date + timedelta(days=1, hours=2)).strftime("%d %b %Y")
            ]
        })

        st.dataframe(indirect_routes)
        st.markdown("</div>", unsafe_allow_html=True)
