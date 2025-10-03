# 🌍 AI-Powered Travel Planner

AI-Powered Travel Planner is a Streamlit-based web application that helps users plan their dream trips effortlessly. It integrates AI models for personalized itinerary creation, hotel and flight recommendations, and travel insights. The application provides a clean, user-friendly interface with modern UI elements and interactive results.  

---

## Features

- **Personalized Trip Planning**: Generate itineraries based on travel theme, activities, and budget.  
- **Flight Recommendations**: Fetches best flights using SerpApi with price, airline, and duration.  
- **Hotel Recommendations**: Finds top hotels and restaurants matching your preferences.  
- **Visa Requirement Check**: Shows whether a visa is required for the destination.  
- **User-Friendly Interface**: Clean layout with tabs, input columns, cards, and styled buttons.  
- **Collapsible Results**: Flights, hotels, and itinerary are shown in expandable sections for easy navigation.  
- **Modern Fonts & Styles**: Uses Google Fonts and gradient buttons for an engaging UI.  

---

## Technologies Used

- **Python 3.x**  
- **Streamlit** for web interface  
- **Agno AI Agents** (Gemini model) for itinerary and travel suggestions  
- **SerpApi** for flight and hotel data  
- **Datetime** for date manipulations  
- **Dotenv** for environment variable management  
- **ReportLab / FPDF** for PDF generation (optional)  

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ai-travel-planner.git
cd ai-travel-planner
```
2. Install required packages:
```
pip install -r requirements.txt
```

3. Add your API keys:
```
SERPAPI_KEY=your_serpapi_key_here
GOOGLE_API_KEY=your_google_api_key_here
```
4. Run the Streamlit app:
```
streamlit run app.py
```
