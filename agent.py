import streamlit as st
import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.google import Gemini
from datetime import datetime, date, timedelta
import json

st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide", initial_sidebar_state="expanded")
load_dotenv()

# ---------------- STYLE ----------------
st.markdown("""
    <style>
        .main-header { text-align: center; font-size: 48px; font-weight: bold; color: #ff6b35; margin-bottom: 10px; }
        .sub-header { text-align: center; font-size: 24px; color: #2c3e50; margin-bottom: 30px; }
        .section-header { font-size: 28px; color: #34495e; border-bottom: 2px solid #ff6b35; padding-bottom: 5px; }
        .input-group { background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0; }
        .result-card { background-color: #e8f4fd; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #ff6b35; }
        .stButton > button { background: linear-gradient(45deg, #ff6b35, #f7931e); color: white; border-radius: 15px; padding: 10px 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<h1 class="main-header">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plan your dream trip with AI! 🌟 Get personalized itineraries, flights, and more.</p>', unsafe_allow_html=True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }

    .main-header {
        text-align: center;
        font-size: 48px;
        font-weight: 700;
        color: #ff6b35;
        margin-bottom: 10px;
    }

    .sub-header {
        text-align: center;
        font-size: 22px;
        color: #2c3e50;
        margin-bottom: 20px;
    }

    .section-header {
        font-size: 28px;
        color: #34495e;
        border-bottom: 2px solid #ff6b35;
        padding-bottom: 5px;
        margin-top: 20px;
    }

    .stButton>button {
        background: linear-gradient(45deg, #ff6b35, #f7931e);
        color: white;
        border-radius: 15px;
        padding: 10px 25px;
        font-weight: 600;
        font-size: 16px;
        transition: transform 0.2s;
    }

    .stButton>button:hover {
        transform: scale(1.05);
    }

    .result-card {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #ff6b35;
        font-size: 16px;
    }

    .input-group {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- API KEYS ----------------
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

if not SERPAPI_KEY:
    st.error("❌ SERPAPI_KEY not found in .env. Add it for flight/hotel searches.")
if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env. Add it for AI features.")

# ---------------- TABS ----------------
tab1, tab2 = st.tabs(["📝 Plan Your Trip", "📊 View Results"])

# ---------------- PLAN YOUR TRIP ----------------
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        source = st.text_input("🛫 Departure City (IATA Code)", "BOM")
        destination = st.text_input("🛬 Destination (IATA Code)", "DEL")
        num_days = st.slider("🕒 Trip Duration (days)", 1, 14, 5)
    with col2:
        travel_theme = st.selectbox("🎭 Travel Theme", ["💑 Couple Getaway", "👨‍👩‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"])
        activity_preferences = st.text_area("🌍 Activities you enjoy", "Relaxing on the beach, exploring historical sites", height=80)

    # Dates
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        departure_date = st.date_input("📅 Departure Date", value=date.today() + timedelta(days=7))
    with date_col2:
        return_date = st.date_input("📅 Return Date", value=date.today() + timedelta(days=12))
    
    if return_date <= departure_date:
        st.error("❌ Return date must be after departure date.")
        st.stop()

    # Sidebar Preferences
    st.sidebar.title("⚙️ Preferences")
    budget = st.sidebar.radio("💰 Budget", ["Economy", "Standard", "Luxury"], horizontal=True)
    flight_class = st.sidebar.radio("✈️ Flight Class", ["Economy", "Business", "First Class"], horizontal=True)
    hotel_rating = st.sidebar.selectbox("🏨 Hotel Rating", ["Any", "3⭐", "4⭐", "5⭐"])
    visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
    travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")

    # ---------------- AGENTS ----------------
    @st.cache_data
    def init_agents():
        researcher = Agent(
            name="Researcher",
            instructions=["Find attractions, culture, and safety tips in Markdown."],
            model=Gemini(id="gemini-2.0-flash-exp"),
            tools=[SerpApiTools(api_key=SERPAPI_KEY)]
        )
        planner = Agent(
            name="Planner",
            instructions=["Create a {num_days}-day itinerary in Markdown: Use headings for days, bullet points for activities, flights, hotels."],
            model=Gemini(id="gemini-2.0-flash-exp")
        )
        hotel_finder = Agent(
            name="Hotel Finder",
            instructions=["Find top hotels and restaurants in Markdown with names, prices, ratings."],
            model=Gemini(id="gemini-2.0-flash-exp"),
            tools=[SerpApiTools(api_key=SERPAPI_KEY)]
        )
        return researcher, planner, hotel_finder

    researcher, planner, hotel_finder = init_agents()

    # ---------------- GENERATE PLAN BUTTON ----------------
    if st.button("🚀 Generate Travel Plan"):
        st.session_state.loading = True
        st.session_state.source = source
        st.session_state.destination = destination
        st.session_state.num_days = num_days
        st.session_state.travel_theme = travel_theme
        st.session_state.activity_preferences = activity_preferences
        st.session_state.departure_date = departure_date
        st.session_state.return_date = return_date
        st.session_state.budget = budget
        st.session_state.flight_class = flight_class
        st.session_state.hotel_rating = hotel_rating
        st.session_state.visa_required = visa_required
        st.session_state.travel_insurance = travel_insurance

        # -------- Flights --------
        st.info("Fetching flights...")  # Placeholder: Replace with API call
        flights = [{"airline": "Air India", "price": 5000, "total_duration": 120}]
        
        # -------- Research --------
        st.info("Researching attractions...")
        research_results = researcher.run(
            f"Top attractions in {destination} for {num_days} days {travel_theme}. Activities: {activity_preferences}. Budget: {budget}."
        ).content
        
        # -------- Hotels --------
        st.info("Finding hotels...")
        hotel_results = hotel_finder.run(
            f"Best hotels near {destination} for {budget} budget, {hotel_rating} rating."
        ).content

        # -------- Itinerary --------
        st.info("Building itinerary...")
        itinerary = planner.run(
            f"Create a {num_days}-day itinerary in {destination} with theme {travel_theme}. "
            f"Include flights: {flights}. Attractions: {research_results}. Hotels: {hotel_results}. Budget: {budget}."
        ).content

        # Save results
        st.session_state.results = {
            'flights': flights,
            'research': research_results,
            'hotels': hotel_results,
            'itinerary': itinerary
        }
        st.success("✅ Travel Plan Generated! Switch to 'View Results' tab to see your plan.")

# ---------------- VIEW RESULTS ----------------
with tab2:
    if 'results' in st.session_state:
        results = st.session_state.results

        st.markdown('<h2 class="section-header">✈️ Recommended Flights</h2>', unsafe_allow_html=True)
        for i, f in enumerate(results['flights'], 1):
            st.markdown(f"**Flight {i}** | 💰 {f.get('price', 'N/A')} INR | 🛫 {f.get('airline', 'Unknown')} | ⏱️ {f.get('total_duration', 'N/A')} min")

        st.markdown('<h2 class="section-header">🏨 Hotels & Restaurants</h2>', unsafe_allow_html=True)
        st.markdown(results['hotels'])

        st.markdown('<h2 class="section-header">🗺️ Detailed Itinerary</h2>', unsafe_allow_html=True)
        st.markdown(results['itinerary'])

        st.markdown('<h2 class="section-header">🛃 Visa Requirement</h2>', unsafe_allow_html=True)
        if st.session_state.visa_required:
            st.info(f"Visa required for traveling from {st.session_state.source} to {st.session_state.destination}. Check embassy/official guidelines.")
        else:
            st.success("No visa required for this trip.")
    else:
        st.info("👆 Enter details in the 'Plan Your Trip' tab and click 'Generate Travel Plan' to see results here.")
