import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import joblib
from route_optimizer import find_best_routes

# ============================
# PAGE CONFIGURATION
# ============================
st.set_page_config(page_title="SmartRail Planner", layout="wide")

# ============================
# BACKGROUND STYLING
# ============================
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://raw.githubusercontent.com/Aanya1234-jpg/SmartRailPlanner/main/images/train3.jpeg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    .main-title {
        text-align: center;
        color: #00BFFF;
        font-size: 60px;
        font-weight: 800;
        text-shadow: 2px 2px 10px #001f3f;
    }

    .sub-title {
        text-align: center;
        color: #E0FFFF;
        font-size: 22px;
        margin-bottom: 30px;
    }

    .section {
        background: rgba(255,255,255,0.85);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.2);
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================
# HEADER
# ============================
st.markdown("<h1 class='main-title'>🚆 SmartRail Planner</h1>", unsafe_allow_html=True)
st.markdown("<h4 class='sub-title'>AI-Based Route Suggestion and Fare Estimation System</h4>", unsafe_allow_html=True)

# ============================
# DATA LOADING
# ============================
@st.cache_data
def load_data():
    try:
        df_routes = pd.read_csv("data/train_schedule.csv")
        model = joblib.load("model/fare_model.pkl")
        return df_routes, model
    except Exception as e:
        st.error(f"Error loading data or model: {e}")
        return None, None

df_routes, model = load_data()

if df_routes is not None:
    stations = sorted(df_routes["source"].unique())

    # ============================
    # INPUT SECTION
    # ============================
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🧭 Plan Your Journey")

    col1, col2, col3 = st.columns(3)
    with col1:
        source = st.selectbox("🚉 Source", stations)
    with col2:
        destination = st.selectbox("🎯 Destination", stations)
    with col3:
        date = st.date_input("📅 Boarding Date", min_value=datetime.today())

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ============================
    # FIND ROUTES BUTTON
    # ============================
    if st.button("Find Best Routes 🚄"):
        st.markdown("<h3 style='color:#00BFFF;'>Available Route Options</h3>", unsafe_allow_html=True)
        
        best_routes = find_best_routes(df_routes, source, destination)
        if best_routes:
            direct_routes = [r for r in best_routes if len(r["stops"]) == 0]
            indirect_routes = [r for r in best_routes if len(r["stops"]) > 0]

            # -----------------
            # Direct Route Display
            # -----------------
            if direct_routes:
                st.success("✅ Direct Route Found")
                for r in direct_routes:
                    arrival_date = (date + timedelta(hours=r["time_hours"])).strftime("%d %b %Y")
                    st.markdown(
                        f"""
                        **Train:** {r['train_name']}  
                        **Type:** {r['type']} | **Class:** {r['class']}  
                        💰 **Fare:** ₹{r['fare']:.2f}  
                        🕒 **Duration:** {r['time_hours']}h  
                        📅 **Arrival:** {arrival_date}
                        """)
            else:
                st.warning("No direct route found.")

            # -----------------
            # Indirect Routes
            # -----------------
            if indirect_routes:
                st.markdown("<h4 style='color:#00BFFF;'>🚉 Indirect Route Options</h4>", unsafe_allow_html=True)
                indirect_data = []
                for r in indirect_routes:
                    arrival_date = (date + timedelta(hours=r["time_hours"])).strftime("%d %b %Y")
                    indirect_data.append({
                        "Route Option": " → ".join(r["path"]),
                        "Total Distance (km)": r["distance"],
                        "Approx Fare (₹)": round(r["fare"], 2),
                        "Estimated Time": f"{r['time_hours']}h",
                        "Arrival": arrival_date
                    })
                df_display = pd.DataFrame(indirect_data)
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("No indirect routes found.")
        else:
            st.error("No route options found between these stations.")
else:
    st.error("Dataset or model could not be loaded. Check your GitHub folder paths.")

# ============================
# FOOTER
# ============================
st.markdown(
    """
    <hr style="border:1px solid #00BFFF;">
    <p style="text-align:center; color:#dfe6e9;">
    © 2025 SmartRail Planner | Powered by AI & Streamlit
    </p>
    """,
    unsafe_allow_html=True
)
