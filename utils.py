import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
from datetime import datetime, timedelta
import os
from PIL import Image
import random
import base64


# Custom CSS for the application
def load_css():
    """Return custom CSS styles for the application"""
    return """
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #2E7D32;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #388E3C;
            margin-bottom: 1.5rem;
        }
        .card {
            border-radius: 5px;
            background-color: #f9f9f9;
            padding: 20px;
            margin-bottom: 10px;
        }
        .metric-card {
            background-color: #E8F5E9;
            border-radius: 5px;
            padding: 15px;
            text-align: center;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #2E7D32;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #388E3C;
        }
        .tool-card {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .tool-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
        }
        .stButton>button:hover {
            background-color: #388E3C;
        }
        .stTextInput>div>div>input {
            border-radius: 5px;
        }
    </style>
    """


# Function to create a map with tool markers
def create_tool_map(tools_df, center_lat=None, center_lon=None, zoom_start=13):
    """Create a Folium map with markers for tool locations"""
    if center_lat is None or center_lon is None:
        # Use average coordinates if not specified
        center_lat = tools_df['latitude'].mean()
        center_lon = tools_df['longitude'].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)

    # Add markers for each tool
    for _, tool in tools_df.iterrows():
        popup_html = f"""
        <strong>{tool['title']}</strong><br>
        ${tool['daily_rate']}/day<br>
        {tool['neighborhood']}<br>
        Rating: {tool['rating']}/5 ({tool['review_count']} reviews)<br>
        <a href="#" onclick="parent.postMessage({{type: 'tool_selected', id: {tool['id']}}}, '*');">View Details</a>
        """

        folium.Marker(
            [tool['latitude'], tool['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tool['title'],
            icon=folium.Icon(color="green", icon="wrench", prefix="fa")
        ).add_to(m)

    return m


# Function to create impact visualizations
def create_impact_chart(chart_type="money_saved"):
    """Create a Plotly chart for community impact visualization"""
    # Sample data for the hackathon demo
    months = ["Jan", "Feb", "Mar", "Apr", "May"]
    impact_data = pd.DataFrame({
        "Month": months,
        "Tools Shared": [24, 36, 52, 68, 85],
        "CO2 Saved (kg)": [120, 180, 260, 340, 425],
        "Money Saved ($)": [1450, 2200, 3150, 4300, 5800]
    })

    if chart_type == "money_saved":
        fig = px.bar(
            impact_data,
            x="Month",
            y="Money Saved ($)",
            color_discrete_sequence=["#2E7D32"],
            title="Community Savings Over Time"
        )
    elif chart_type == "environmental":
        fig = px.line(
            impact_data,
            x="Month",
            y="CO2 Saved (kg)",
            markers=True,
            color_discrete_sequence=["#388E3C"],
            title="CO2 Emissions Avoided Through Tool Sharing"
        )
    elif chart_type == "tools_shared":
        fig = px.area(
            impact_data,
            x="Month",
            y="Tools Shared",
            color_discrete_sequence=["#81C784"],
            title="Growth in Tool Sharing Activity"
        )

    fig.update_layout(height=400)
    return fig


# Function to format currency
def format_currency(amount):
    """Format a number as currency"""
    return f"${amount:.2f}"


# Function to generate a placeholder image URL
def get_placeholder_image_url(text, width=300, height=200):
    """Generate a placeholder image URL with specified text"""
    return f"https://via.placeholder.com/{width}x{height}.png?text={text.replace(' ', '+')}"


# Function to calculate metrics for the dashboard
def calculate_dashboard_metrics(tools_df, bookings_df):
    """Calculate metrics for the dashboard"""
    available_tools = len(tools_df[tools_df['available'] == True])

    # For demo purposes, we'll use fixed values for some metrics
    # In a real app, these would be calculated from actual data
    avg_savings_percentage = 82

    # Calculate community savings based on bookings
    community_savings = 0
    if not bookings_df.empty and 'total_cost' in bookings_df.columns:
        completed_bookings = bookings_df[
            bookings_df['status'].isin(['Completed', 'Approved', 'Returned'])
        ]
        if not completed_bookings.empty:
            # Assume savings is 3x the rental cost (cost of buying vs. renting)
            community_savings = completed_bookings['total_cost'].sum() * 3

    # For demo, if no savings calculated, use a default
    if community_savings == 0:
        community_savings = 12450

    # User satisfaction (fixed for demo)
    user_satisfaction = 4.8

    return {
        "available_tools": available_tools,
        "avg_savings_percentage": avg_savings_percentage,
        "community_savings": community_savings,
        "user_satisfaction": user_satisfaction
    }


# Function to check if dates are valid for booking
def validate_booking_dates(start_date, end_date):
    """Validate booking date range"""
    if start_date > end_date:
        return False, "End date must be after start date."

    today = datetime.now().date()
    if start_date < today:
        return False, "Start date cannot be in the past."

    # Limit bookings to 30 days
    max_duration = timedelta(days=30)
    if end_date - start_date > max_duration:
        return False, "Maximum booking duration is 30 days."

    return True, ""


# Function to generate random mock reviews
def generate_mock_reviews(count=3):
    """Generate random mock reviews for the demo"""
    review_comments = [
        "Great tool, worked perfectly for my project!",
        "Owner was very helpful with instructions.",
        "Clean and well-maintained. Would rent again.",
        "Saved me so much money by not having to buy this.",
        "Excellent condition, just as described.",
        "Easy pickup and return process.",
        "Tool was exactly what I needed for my weekend project.",
        "Very satisfied with this rental.",
        "The owner was friendly and flexible with pickup time.",
        "Will definitely use this service again!"
    ]

    review_dates = [
        "2 days ago",
        "1 week ago",
        "2 weeks ago",
        "1 month ago",
        "2 months ago"
    ]

    reviews = []
    for i in range(count):
        reviews.append({
            "rating": random.randint(4, 5),
            "comment": random.choice(review_comments),
            "date": random.choice(review_dates)
        })

    return reviews


# Initialize session state variables
def initialize_session_state():
    """Initialize session state variables"""
    if 'user_logged_in' not in st.session_state:
        st.session_state.user_logged_in = False

    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

    if 'page' not in st.session_state:
        st.session_state.page = 'home'