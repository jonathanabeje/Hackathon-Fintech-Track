import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
from datetime import datetime, timedelta
import os
from PIL import Image
import random
import json
import base64

# Configure the Streamlit page
st.set_page_config(
    page_title="ToolShare - Neighborhood Tool Rental Marketplace",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for user authentication and data persistence
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'page' not in st.session_state:
    st.session_state.page = 'home'


# Tool type to image mapping
def get_tool_image_url(tool_type):
    """Get an image URL based on tool type"""
    tool_image_map = {
        "Power Drill": "https://cdn.pixabay.com/photo/2016/10/05/08/57/drill-1710332_960_720.jpg",
        "Circular Saw": "https://cdn.pixabay.com/photo/2016/03/27/21/32/circular-saw-1281730_960_720.jpg",
        "Lawn Mower": "https://cdn.pixabay.com/photo/2017/04/02/21/06/gardening-2199526_960_720.jpg",
        "Pressure Washer": "https://cdn.pixabay.com/photo/2018/10/06/08/09/pressure-washer-3728199_960_720.jpg",
        "Leaf Blower": "https://cdn.pixabay.com/photo/2016/10/05/14/26/leaf-blower-1720536_960_720.jpg",
        "Hedge Trimmer": "https://cdn.pixabay.com/photo/2015/03/21/22/33/hedge-trimmer-684941_960_720.jpg",
        "Ladder": "https://cdn.pixabay.com/photo/2018/06/04/02/15/ladder-3453397_960_720.jpg",
        "Chain Saw": "https://cdn.pixabay.com/photo/2021/09/18/14/37/chainsaw-6635616_960_720.jpg",
        "Sander": "https://cdn.pixabay.com/photo/2019/02/18/12/37/sander-4004617_960_720.jpg",
        "Nail Gun": "https://cdn.pixabay.com/photo/2014/12/08/16/18/hammer-560831_960_720.jpg",
        "Air Compressor": "https://cdn.pixabay.com/photo/2020/05/02/17/18/compressor-5122186_960_720.jpg",
        "Generator": "https://cdn.pixabay.com/photo/2020/12/18/06/24/generator-5841302_960_720.jpg",
        "Router": "https://cdn.pixabay.com/photo/2017/02/14/15/26/router-2066385_960_720.jpg",
        "Planer": "https://cdn.pixabay.com/photo/2016/04/27/03/02/wood-planer-1355818_960_720.jpg",
        "Jigsaw": "https://cdn.pixabay.com/photo/2015/03/19/02/51/jigsaw-680741_960_720.jpg",
        "Rotary Hammer": "https://cdn.pixabay.com/photo/2017/06/06/21/37/drill-2378341_960_720.jpg",
        "Tile Cutter": "https://cdn.pixabay.com/photo/2017/02/08/09/56/angle-grinder-2048422_960_720.jpg",
        "Paint Sprayer": "https://cdn.pixabay.com/photo/2013/04/01/09/07/paint-gun-98435_960_720.jpg"
    }
    # Fallback image for any tool type not in the map
    fallback_image_url = "https://cdn.pixabay.com/photo/2016/12/19/14/59/tool-1916386_960_720.jpg"
    return tool_image_map.get(tool_type, fallback_image_url)


# Function to load data (mock data for the hackathon)
@st.cache_data
def load_tool_data():
    # Check if data file exists, otherwise create mock data
    if os.path.exists('data/tools.csv'):
        df = pd.read_csv('data/tools.csv')

        # Add image_url column if it doesn't exist
        if 'image_url' not in df.columns:
            df['image_url'] = df.apply(lambda row: get_tool_image_url(row['tool_type']), axis=1)
            df.to_csv('data/tools.csv', index=False)

        return df
    else:
        # Create directory if it doesn't exist
        os.makedirs('data', exist_ok=True)

        # Create mock data
        tool_types = [
            "Power Drill", "Circular Saw", "Lawn Mower", "Pressure Washer",
            "Hedge Trimmer", "Ladder", "Chain Saw", "Sander", "Nail Gun",
            "Air Compressor", "Generator", "Router", "Planer", "Jigsaw",
            "Rotary Hammer", "Tile Cutter", "Paint Sprayer", "Leaf Blower"
        ]

        brands = [
            "DeWalt", "Makita", "Milwaukee", "Bosch", "Ryobi", "Black & Decker",
            "Craftsman", "Ridgid", "Festool", "Hitachi", "Porter-Cable", "Kobalt"
        ]

        conditions = ["Like New", "Good", "Fair", "Well Used but Functional"]

        # Generate 50 mock tools
        mock_data = []

        # Define a fixed set of neighborhoods with coordinates for the demo
        neighborhoods = {
            "Downtown": (40.7128, -74.0060),
            "Midtown": (40.7549, -73.9840),
            "Uptown": (40.8075, -73.9626),
            "Brooklyn Heights": (40.6950, -73.9950),
            "Williamsburg": (40.7081, -73.9571),
            "Astoria": (40.7636, -73.9232),
            "Park Slope": (40.6710, -73.9814),
            "Long Island City": (40.7447, -73.9485)
        }

        # Mock user data
        users = [
            {"username": "john_diy", "name": "John Smith", "email": "john@example.com"},
            {"username": "sarah_maker", "name": "Sarah Johnson", "email": "sarah@example.com"},
            {"username": "mike_build", "name": "Mike Chen", "email": "mike@example.com"},
            {"username": "lisa_craft", "name": "Lisa Rodriguez", "email": "lisa@example.com"},
            {"username": "david_tools", "name": "David Wilson", "email": "david@example.com"},
            {"username": "emma_fix", "name": "Emma Brown", "email": "emma@example.com"},
            {"username": "demo_user", "name": "Demo User", "email": "demo@toolshare.com"}
        ]

        for i in range(50):
            neighborhood = random.choice(list(neighborhoods.keys()))
            lat, lon = neighborhoods[neighborhood]
            # Add small random variation to lat/lon to spread tools out
            lat += random.uniform(-0.01, 0.01)
            lon += random.uniform(-0.01, 0.01)

            owner = random.choice(users)

            tool_type = random.choice(tool_types)
            brand = random.choice(brands)

            # Get image URL for the tool type
            image_url = get_tool_image_url(tool_type)

            # Create a title that combines brand and tool type
            title = f"{brand} {tool_type}"

            # Create a more detailed description
            descriptions = [
                f"Great {tool_type} for home projects. Well maintained and ready to use.",
                f"Professional grade {tool_type}. Perfect for serious DIYers.",
                f"Reliable {tool_type} that gets the job done. Easy to use.",
                f"High-quality {brand} {tool_type}. Powerful and efficient.",
                f"Versatile {tool_type} suitable for various applications."
            ]

            hourly_rate = round(random.uniform(5, 25), 2)
            daily_rate = round(hourly_rate * 5, 2)  # Daily rate is approximately 5x hourly

            # Some tools will have a security deposit
            deposit = round(random.uniform(20, 100), 2) if random.random() > 0.3 else 0

            # Generate random ratings with a bias toward positive reviews
            rating = round(random.uniform(3, 5), 1)
            review_count = random.randint(0, 25)

            mock_data.append({
                "id": i + 1,
                "title": title,
                "description": random.choice(descriptions),
                "tool_type": tool_type,
                "brand": brand,
                "condition": random.choice(conditions),
                "hourly_rate": hourly_rate,
                "daily_rate": daily_rate,
                "deposit": deposit,
                "owner_username": owner["username"],
                "owner_name": owner["name"],
                "neighborhood": neighborhood,
                "latitude": lat,
                "longitude": lon,
                "rating": rating,
                "review_count": review_count,
                "available": random.random() > 0.2,  # 80% of tools are available
                "image_url": image_url  # Add image URL to the data
            })

        # Convert to DataFrame and save
        df = pd.DataFrame(mock_data)
        # Create the directory for storing images
        os.makedirs('images', exist_ok=True)

        # Save to CSV
        df.to_csv('data/tools.csv', index=False)

        # Also save users data
        users_df = pd.DataFrame(users)
        users_df.to_csv('data/users.csv', index=False)

        return df


@st.cache_data
def load_user_data():
    if os.path.exists('data/users.csv'):
        return pd.read_csv('data/users.csv')
    else:
        # If tools data is loaded first, this file should exist
        # But just in case, we'll return an empty DataFrame
        return pd.DataFrame(columns=["username", "name", "email"])


@st.cache_data
def load_bookings_data():
    if os.path.exists('data/bookings.csv'):
        return pd.read_csv('data/bookings.csv')
    else:
        # Create an empty bookings dataframe
        bookings_df = pd.DataFrame(columns=[
            "id", "tool_id", "renter_username", "start_date", "end_date",
            "total_cost", "status", "created_at"
        ])
        bookings_df.to_csv('data/bookings.csv', index=False)
        return bookings_df


# Load data
tools_df = load_tool_data()
users_df = load_user_data()
bookings_df = load_bookings_data()


# Helper function for login - MUST BE DEFINED BEFORE USE
def login(username):
    if username in users_df['username'].values:
        st.session_state.user_logged_in = True
        st.session_state.current_user = username
        return True
    else:
        st.error("Invalid username. Please try again.")
        return False


# Custom CSS
st.markdown("""
<style>
    .metric-container {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        height: 100%;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2E7D32;
    }
    .metric-label {
        font-size: 1rem;
        color: #555;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #eee;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .tool-card-image {
        object-fit: cover;
        height: 200px;
        width: 100%;
        border-radius: 8px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    # Logo and Title
    st.image("https://via.placeholder.com/150x80.png?text=ToolShare", width=150)
    st.title("ToolShare")

    # User Authentication
    if st.session_state.user_logged_in:
        user_data = users_df[users_df['username'] == st.session_state.current_user].iloc[0]
        st.write(f"Logged in as: {user_data['name']}")
        if st.button("Log Out"):
            st.session_state.user_logged_in = False
            st.session_state.current_user = None
            st.rerun()
    else:
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username")
            if st.form_submit_button("Login"):
                login(username)
                st.rerun()

        # Demo quick login
        if st.button("Use Demo Account"):
            login("demo_user")
            st.rerun()

    st.divider()

    # Navigation
    st.header("Navigation")
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()

    if st.button("🔍 Find Tools", use_container_width=True):
        st.session_state.page = 'find_tools'
        st.rerun()

    if st.session_state.user_logged_in:
        if st.button("➕ Add Tool Listing", use_container_width=True):
            st.session_state.page = 'add_listing'
            st.rerun()

        if st.button("👤 My Profile", use_container_width=True):
            st.session_state.page = 'profile'
            st.rerun()

        if st.button("📚 My Bookings", use_container_width=True):
            st.session_state.page = 'bookings'
            st.rerun()

    st.divider()
    st.header("About")
    st.write("""
        ToolShare connects neighbors to share 
        tools and equipment, saving money 
        and reducing waste.
    """)


def render_tool_card(tool, col):
    """Render a tool card using Streamlit components"""
    with col:
        # Display the actual image
        st.image(
            tool["image_url"],
            caption=f"{tool['brand']} {tool['tool_type']}",
            use_column_width=True
        )

        # Tool details
        st.subheader(tool['title'])
        st.write(f"**${tool['daily_rate']:.2f}/day** · {tool['neighborhood']}")
        st.write(f"{tool['description'][:100]}...")

        # View button
        if st.button(f"View Details", key=f"view_{tool['id']}"):
            st.session_state.selected_tool = tool['id']
            st.session_state.page = 'tool_details'
            st.rerun()


# Home page
def show_home_page():
    # App title
    st.title("🛠️ ToolShare")
    st.subheader("Neighborhood Tool Rental Marketplace")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-value">128</div>
            <div class="metric-label">Available Tools</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-value">82%</div>
            <div class="metric-label">Average Savings</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-value">$12,450</div>
            <div class="metric-label">Community Savings</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-value">4.8/5</div>
            <div class="metric-label">User Satisfaction</div>
        </div>
        """, unsafe_allow_html=True)

    # Featured tools section
    st.markdown("<h2 class='section-title'>Featured Tools</h2>", unsafe_allow_html=True)

    # Filter for only available tools
    available_tools = tools_df[tools_df['available'] == True]

    # Get 3 random tools to feature
    if len(available_tools) >= 3:
        featured_tools = available_tools.sample(3)

        # Create three columns
        cols = st.columns(3)

        for i, (_, tool) in enumerate(featured_tools.iterrows()):
            render_tool_card(tool, cols[i])

    # How it works section
    st.markdown("<h2 class='section-title'>How It Works</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container():
            st.markdown("#### 1. Find Nearby Tools")
            st.write("Browse our interactive map to discover tools available in your neighborhood.")

    with col2:
        with st.container():
            st.markdown("#### 2. Book & Pay")
            st.write("Reserve tools for when you need them and complete the secure payment process.")

    with col3:
        with st.container():
            st.markdown("#### 3. Pick Up & Use")
            st.write("Meet your neighbor, pick up the tool, and get your project done!")

    # Community impact section
    st.markdown("<h2 class='section-title'>Community Impact</h2>", unsafe_allow_html=True)

    # Create a sample dataframe for community impact visualization
    months = ["Jan", "Feb", "Mar", "Apr", "May"]
    impact_data = pd.DataFrame({
        "Month": months,
        "Tools Shared": [24, 36, 52, 68, 85],
        "CO2 Saved (kg)": [120, 180, 260, 340, 425],
        "Money Saved ($)": [1450, 2200, 3150, 4300, 5800]
    })

    tab1, tab2 = st.tabs(["Money Saved", "Environmental Impact"])

    with tab1:
        fig = px.bar(
            impact_data,
            x="Month",
            y="Money Saved ($)",
            color_discrete_sequence=["#2E7D32"],
            title="Community Savings Over Time"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.line(
            impact_data,
            x="Month",
            y="CO2 Saved (kg)",
            markers=True,
            color_discrete_sequence=["#388E3C"],
            title="CO2 Emissions Avoided Through Tool Sharing"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Testimonials
    st.markdown("<h2 class='section-title'>What Our Users Say</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            st.info(
                """ "I saved over $400 by borrowing a pressure washer and lawn aerator instead of buying them for a one-time project!" - Sarah J.""")

    with col2:
        with st.container():
            st.info(
                """ "My garage was full of tools I only use once a year. Now they're helping neighbors and generating some extra income!" - Mike T.""")


def show_find_tools_page():
    st.title("🔍 Find Tools")

    # Filter options
    st.subheader("Filter Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        tool_types = ["All Types"] + sorted(tools_df['tool_type'].unique().tolist())
        selected_type = st.selectbox("Tool Type", tool_types)

    with col2:
        neighborhoods = ["All Neighborhoods"] + sorted(tools_df['neighborhood'].unique().tolist())
        selected_neighborhood = st.selectbox("Neighborhood", neighborhoods)

    with col3:
        price_range = st.slider("Max Daily Rate ($)",
                                min_value=float(tools_df['daily_rate'].min()),
                                max_value=float(tools_df['daily_rate'].max()),
                                value=float(tools_df['daily_rate'].max()))

    # Filter the dataframe
    filtered_df = tools_df.copy()

    if selected_type != "All Types":
        filtered_df = filtered_df[filtered_df['tool_type'] == selected_type]

    if selected_neighborhood != "All Neighborhoods":
        filtered_df = filtered_df[filtered_df['neighborhood'] == selected_neighborhood]

    filtered_df = filtered_df[filtered_df['daily_rate'] <= price_range]

    # Only show available tools
    filtered_df = filtered_df[filtered_df['available'] == True]

    # Map view tab and List view tab
    tab1, tab2 = st.tabs(["Map View", "List View"])

    with tab1:
        # Create a map centered on the average coordinates
        if not filtered_df.empty:
            center_lat = filtered_df['latitude'].mean()
            center_lon = filtered_df['longitude'].mean()

            m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

            # Add markers for each tool
            for _, tool in filtered_df.iterrows():
                popup_html = f"""
                <div style="width: 200px;">
                    <img src="{tool['image_url']}" style="width: 100%; height: auto; border-radius: 4px; margin-bottom: 8px;">
                    <h4>{tool['title']}</h4>
                    <p><strong>${tool['daily_rate']:.2f}/day</strong></p>
                    <p>{tool['neighborhood']}</p>
                    <p>Rating: {tool['rating']}/5 ({tool['review_count']} reviews)</p>
                    <p><a href="#" onclick="parent.postMessage({{type: 'tool_selected', id: {tool['id']}}}, '*');">View Details</a></p>
                </div>
                """

                folium.Marker(
                    [tool['latitude'], tool['longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=tool['title'],
                    icon=folium.Icon(color="green", icon="wrench", prefix="fa")
                ).add_to(m)

            # Display the map
            folium_static(m, width=800, height=500)

            # Handle the JavaScript message for tool selection
            selected_tool_id = st.text_input("Enter tool ID to view details:", "", key="map_tool_id")
            if selected_tool_id and selected_tool_id.isdigit():
                st.session_state.selected_tool = int(selected_tool_id)
                st.session_state.page = 'tool_details'
                st.rerun()
        else:
            st.warning("No tools match your search criteria.")

    with tab2:
        if not filtered_df.empty:
            # Display results count
            st.write(f"{len(filtered_df)} tools found")

            # Display as cards in grid layout
            cols = st.columns(3)

            for i, (_, tool) in enumerate(filtered_df.iterrows()):
                render_tool_card(tool, cols[i % 3])
        else:
            st.warning("No tools match your search criteria.")


def show_tool_details():
    if 'selected_tool' not in st.session_state:
        st.error("No tool selected.")
        return

    tool_id = st.session_state.selected_tool
    tool_data = tools_df[tools_df['id'] == tool_id]

    if tool_data.empty:
        st.error("Tool not found.")
        return

    tool = tool_data.iloc[0]

    # Back button
    if st.button("← Back to Search"):
        st.session_state.page = 'find_tools'
        st.rerun()

    # Tool title and details
    st.title(tool['title'])

    col1, col2 = st.columns([2, 1])

    with col1:
        # Display the image
        st.image(
            tool["image_url"],
            caption=f"{tool['brand']} {tool['tool_type']}",
            use_column_width=True
        )

        # Description
        st.subheader("Description")
        st.write(tool['description'])

        # Specifications
        st.subheader("Specifications")
        specs_col1, specs_col2 = st.columns(2)

        with specs_col1:
            st.write(f"**Type:** {tool['tool_type']}")
            st.write(f"**Brand:** {tool['brand']}")
            st.write(f"**Condition:** {tool['condition']}")

        with specs_col2:
            st.write(f"**Location:** {tool['neighborhood']}")
            st.write(f"**Rating:** {tool['rating']}/5 ({tool['review_count']} reviews)")
            st.write(f"**Owner:** {tool['owner_name']}")

        # Reviews
        st.subheader("Reviews")

        # Mock reviews
        review_texts = [
            "Great tool, worked perfectly for my project!",
            "Owner was very helpful with instructions.",
            "Clean and well-maintained. Would rent again.",
            "Saved me so much money by not having to buy this.",
            "Excellent condition, just as described."
        ]

        review_names = ["John D.", "Sarah M.", "David W.", "Lisa R.", "Michael C."]
        review_times = ["2 days ago", "1 week ago", "2 weeks ago", "1 month ago", "2 months ago"]

        # Display 3 random reviews or fewer if there aren't enough
        review_count = min(3, tool['review_count'])

        for i in range(review_count):
            with st.container():
                review_rating = random.randint(4, 5)
                review_text = random.choice(review_texts)
                reviewer_name = random.choice(review_names)
                review_time = random.choice(review_times)

                st.markdown(f"**{'⭐' * review_rating}** - {reviewer_name} ({review_time})")
                st.write(f"_{review_text}_")
                st.divider()

        if tool['review_count'] > 3:
            st.button(f"View all {tool['review_count']} reviews")

    with col2:
        # Booking information
        st.subheader("Booking Information")

        with st.container():
            st.write("### Pricing")
            st.write(f"**Hourly Rate:** ${tool['hourly_rate']:.2f}")
            st.write(f"**Daily Rate:** ${tool['daily_rate']:.2f}")
            st.write(f"**Security Deposit:** ${tool['deposit']:.2f}")

        # Booking form
        st.subheader("Book This Tool")

        if not st.session_state.user_logged_in:
            st.warning("Please log in to book this tool.")
        else:
            with st.form("booking_form"):
                # Date selection
                today = datetime.now().date()
                start_date = st.date_input("Start Date", today)
                end_date = st.date_input("End Date", today + timedelta(days=1))

                # Calculate duration and cost
                if start_date and end_date:
                    if end_date < start_date:
                        st.error("End date must be after start date.")

                    duration_days = (end_date - start_date).days
                    if duration_days == 0:
                        duration_days = 1  # Minimum 1 day

                    total_cost = duration_days * tool['daily_rate']
                    st.write(f"**Duration:** {duration_days} days")
                    st.write(f"**Total Cost:** ${total_cost:.2f}")

                    if tool['deposit'] > 0:
                        st.write(f"**Security Deposit:** ${tool['deposit']:.2f} (refundable)")

                # Submit button
                if st.form_submit_button("Book Now"):
                    if end_date < start_date:
                        st.error("Please correct the date selection.")
                    else:
                        # Create a new booking record
                        booking_id = len(bookings_df) + 1
                        new_booking = pd.DataFrame([{
                            "id": booking_id,
                            "tool_id": tool_id,
                            "renter_username": st.session_state.current_user,
                            "start_date": start_date.strftime("%Y-%m-%d"),
                            "end_date": end_date.strftime("%Y-%m-%d"),
                            "total_cost": total_cost,
                            "status": "Pending",
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }])

                        # Append to bookings dataframe
                        updated_bookings_df = pd.concat([bookings_df, new_booking], ignore_index=True)
                        updated_bookings_df.to_csv('data/bookings.csv', index=False)

                        # Bust cache to refresh data
                        load_bookings_data.clear()

                        # Success message and redirect
                        st.success("Booking successful! The owner has been notified.")
                        st.session_state.page = 'bookings'
                        st.rerun()

        # Map showing the tool location
        st.subheader("Location")

        m = folium.Map(location=[tool['latitude'], tool['longitude']], zoom_start=15)

        # Add a circle to show approximate location (for privacy)
        folium.Circle(
            radius=300,
            location=[tool['latitude'], tool['longitude']],
            color="green",
            fill=True,
            fill_opacity=0.2
        ).add_to(m)

        folium.Marker(
            [tool['latitude'], tool['longitude']],
            tooltip=tool['neighborhood'],
            icon=folium.Icon(color="green", icon="wrench", prefix="fa")
        ).add_to(m)

        folium_static(m, width=400, height=300)

        st.info("Exact location will be provided after booking is confirmed.")


def show_add_listing():
    if not st.session_state.user_logged_in:
        st.warning("Please log in to add a tool listing.")
        return

    st.title("Add Tool Listing")

    # Image upload (simulated for the hackathon)
    st.subheader("Upload Photos")
    st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    st.info("For the hackathon demo, uploaded images won't be processed, and placeholder images will be used instead.")

    # Listing details form
    with st.form("add_tool_form"):
        st.subheader("Listing Details")

        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Tool Title")

            tool_types = sorted(tools_df['tool_type'].unique().tolist())
            tool_type = st.selectbox("Tool Type", tool_types)

            brand = st.text_input("Brand")

            conditions = ["Like New", "Good", "Fair", "Well Used but Functional"]
            condition = st.selectbox("Condition", conditions)

        with col2:
            hourly_rate = st.number_input("Hourly Rate ($)", min_value=1.0, max_value=100.0, step=0.5)
            daily_rate = st.number_input("Daily Rate ($)", min_value=5.0, max_value=500.0, step=1.0)
            deposit = st.number_input("Security Deposit ($)", min_value=0.0, max_value=1000.0, step=10.0)

            neighborhoods = sorted(tools_df['neighborhood'].unique().tolist())
            neighborhood = st.selectbox("Neighborhood", neighborhoods)

        st.subheader("Description")
        description = st.text_area("Provide details about your tool, its features, and any usage instructions",
                                   height=100)

        # Submit button
        submit = st.form_submit_button("Create Listing")

        if submit:
            if not title or not description:
                st.error("Please fill in all required fields.")
            else:
                # Create a new tool record
                neighborhood_data = {
                    "Downtown": (40.7128, -74.0060),
                    "Midtown": (40.7549, -73.9840),
                    "Uptown": (40.8075, -73.9626),
                    "Brooklyn Heights": (40.6950, -73.9950),
                    "Williamsburg": (40.7081, -73.9571),
                    "Astoria": (40.7636, -73.9232),
                    "Park Slope": (40.6710, -73.9814),
                    "Long Island City": (40.7447, -73.9485)
                }

                base_lat, base_lon = neighborhood_data.get(neighborhood, (40.7128, -74.0060))
                lat = base_lat + random.uniform(-0.01, 0.01)
                lon = base_lon + random.uniform(-0.01, 0.01)

                tool_id = tools_df['id'].max() + 1 if not tools_df.empty else 1

                user_data = users_df[users_df['username'] == st.session_state.current_user].iloc[0]

                # Get image URL based on tool type
                image_url = get_tool_image_url(tool_type)

                new_tool = pd.DataFrame([{
                    "id": tool_id,
                    "title": title,
                    "description": description,
                    "tool_type": tool_type,
                    "brand": brand,
                    "condition": condition,
                    "hourly_rate": hourly_rate,
                    "daily_rate": daily_rate,
                    "deposit": deposit,
                    "owner_username": st.session_state.current_user,
                    "owner_name": user_data['name'],
                    "neighborhood": neighborhood,
                    "latitude": lat,
                    "longitude": lon,
                    "rating": 0,
                    "review_count": 0,
                    "available": True,
                    "image_url": image_url
                }])

                # Append to tools dataframe
                updated_tools_df = pd.concat([tools_df, new_tool], ignore_index=True)
                updated_tools_df.to_csv('data/tools.csv', index=False)

                # Bust cache to refresh data
                load_tool_data.clear()

                # Success message
                st.success("Tool listing created successfully!")

                # Redirect to the tools page
                st.session_state.page = 'find_tools'
                st.rerun()


def show_profile():
    if not st.session_state.user_logged_in:
        st.warning("Please log in to view your profile.")
        return

    user_data = users_df[users_df['username'] == st.session_state.current_user].iloc[0]
    user_tools = tools_df[tools_df['owner_username'] == st.session_state.current_user]

    st.title(f"{user_data['name']}'s Profile")

    col1, col2 = st.columns([1, 2])

    with col1:
        # Profile avatar
        st.markdown(
            f"""
            <div style="
                width: 150px;
                height: 150px;
                background-color: #E8F5E9;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px auto;
                color: #2E7D32;
                font-size: 4rem;
                font-weight: bold;
            ">
                {user_data['name'][0]}
            </div>
            """,
            unsafe_allow_html=True
        )

        # User info
        st.write(f"**Username:** {user_data['username']}")
        st.write(f"**Email:** {user_data['email']}")
        st.write("**Member Since:** January 2023")

        # Stats
        st.subheader("Stats")
        st.write(f"**Tools Listed:** {len(user_tools)}")
        st.write("**Rental Income:** $345")
        st.write("**Money Saved:** $280")
        st.write("**Rating:** ⭐⭐⭐⭐⭐ (5.0)")

    with col2:
        st.subheader("My Tools")

        if user_tools.empty:
            st.info("You haven't listed any tools yet.")
            if st.button("Add Your First Tool"):
                st.session_state.page = 'add_listing'
                st.rerun()
        else:
            # Display each tool
            for _, tool in user_tools.iterrows():
                with st.container():
                    # Tool card with image
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        st.image(tool['image_url'], width=150)

                    with col2:
                        st.subheader(tool['title'])
                        st.write(f"**${tool['daily_rate']}/day** · {tool['neighborhood']}")
                        st.write(f"**Status:** {'Available' if tool['available'] else 'Not Available'}")

                        # Buttons
                        but_col1, but_col2 = st.columns(2)
                        with but_col1:
                            if tool['available']:
                                if st.button("Mark Unavailable", key=f"unavail_{tool['id']}"):
                                    # Update availability
                                    updated_tools_df = tools_df.copy()
                                    updated_tools_df.loc[updated_tools_df['id'] == tool['id'], 'available'] = False
                                    updated_tools_df.to_csv('data/tools.csv', index=False)
                                    load_tool_data.clear()
                                    st.rerun()
                            else:
                                if st.button("Mark Available", key=f"avail_{tool['id']}"):
                                    # Update availability
                                    updated_tools_df = tools_df.copy()
                                    updated_tools_df.loc[updated_tools_df['id'] == tool['id'], 'available'] = True
                                    updated_tools_df.to_csv('data/tools.csv', index=False)
                                    load_tool_data.clear()
                                    st.rerun()

                    st.divider()


def show_bookings():
    if not st.session_state.user_logged_in:
        st.warning("Please log in to view your bookings.")
        return

    st.title("My Bookings")

    # Get fresh data
    fresh_bookings_df = load_bookings_data()

    # Get bookings for the current user
    user_bookings = fresh_bookings_df[fresh_bookings_df['renter_username'] == st.session_state.current_user]

    # Get tools owned by the current user
    owned_tools = tools_df[tools_df['owner_username'] == st.session_state.current_user]

    # Get bookings for tools owned by the current user
    rental_requests = pd.DataFrame()
    if not owned_tools.empty:
        owned_tool_ids = owned_tools['id'].tolist()
        rental_requests = fresh_bookings_df[fresh_bookings_df['tool_id'].isin(owned_tool_ids)]

    # Create tabs for rentals and tool rental requests
    tab1, tab2 = st.tabs(["Tools I'm Renting", "Rental Requests for My Tools"])

    with tab1:
        if user_bookings.empty:
            st.info("You haven't rented any tools yet.")
            if st.button("Find Tools to Rent"):
                st.session_state.page = 'find_tools'
                st.rerun()
        else:
            # Display bookings
            for _, booking in user_bookings.iterrows():
                # Get tool details
                tool_data = tools_df[tools_df['id'] == booking['tool_id']]
                if tool_data.empty:
                    continue  # Skip if tool no longer exists

                tool = tool_data.iloc[0]

                with st.container():
                    # Booking info with image
                    col1, col2, col3 = st.columns([1, 2, 1])

                    with col1:
                        st.image(tool['image_url'], width=150)

                    with col2:
                        st.subheader(tool['title'])
                        st.write(f"**Booking ID:** {booking['id']}")
                        st.write(f"**Dates:** {booking['start_date']} to {booking['end_date']}")
                        st.write(f"**Total Cost:** ${booking['total_cost']}")
                        st.write(f"**Owner:** {tool['owner_name']}")

                        # Status badge
                        status = booking['status']
                        st.write(f"**Status:** {status}")

                    with col3:
                        if booking['status'] == 'Pending':
                            if st.button("Cancel", key=f"cancel_{booking['id']}"):
                                # Update booking status
                                updated_bookings_df = fresh_bookings_df.copy()
                                updated_bookings_df.loc[
                                    updated_bookings_df['id'] == booking['id'], 'status'] = 'Cancelled'
                                updated_bookings_df.to_csv('data/bookings.csv', index=False)
                                load_bookings_data.clear()
                                st.rerun()

                        if booking['status'] == 'Approved':
                            if st.button("Return", key=f"return_{booking['id']}"):
                                # Update booking status
                                updated_bookings_df = fresh_bookings_df.copy()
                                updated_bookings_df.loc[
                                    updated_bookings_df['id'] == booking['id'], 'status'] = 'Returned'
                                updated_bookings_df.to_csv('data/bookings.csv', index=False)
                                load_bookings_data.clear()
                                st.rerun()

                    st.divider()

    with tab2:
        if rental_requests.empty:
            st.info("You don't have any rental requests for your tools.")
        else:
            # Display rental requests
            for _, request in rental_requests.iterrows():
                # Get tool details
                tool_data = tools_df[tools_df['id'] == request['tool_id']]
                if tool_data.empty:
                    continue  # Skip if tool no longer exists

                tool = tool_data.iloc[0]

                # Get renter details
                renter_data = users_df[users_df['username'] == request['renter_username']]
                if renter_data.empty:
                    renter_name = "Unknown User"
                else:
                    renter_name = renter_data.iloc[0]['name']

                with st.container():
                    # Request info with image
                    col1, col2, col3 = st.columns([1, 2, 1])

                    with col1:
                        st.image(tool['image_url'], width=150)

                    with col2:
                        st.subheader(tool['title'])
                        st.write(f"**Booking ID:** {request['id']}")
                        st.write(f"**Dates:** {request['start_date']} to {request['end_date']}")
                        st.write(f"**Total Cost:** ${request['total_cost']}")
                        st.write(f"**Renter:** {renter_name}")

                        # Status badge
                        status = request['status']
                        st.write(f"**Status:** {status}")

                    with col3:
                        if request['status'] == 'Pending':
                            if st.button("Approve", key=f"approve_{request['id']}"):
                                # Update booking status
                                updated_bookings_df = fresh_bookings_df.copy()
                                updated_bookings_df.loc[
                                    updated_bookings_df['id'] == request['id'], 'status'] = 'Approved'
                                updated_bookings_df.to_csv('data/bookings.csv', index=False)
                                load_bookings_data.clear()
                                st.rerun()

                            if st.button("Decline", key=f"decline_{request['id']}"):
                                # Update booking status
                                updated_bookings_df = fresh_bookings_df.copy()
                                updated_bookings_df.loc[
                                    updated_bookings_df['id'] == request['id'], 'status'] = 'Declined'
                                updated_bookings_df.to_csv('data/bookings.csv', index=False)
                                load_bookings_data.clear()
                                st.rerun()

                        if request['status'] == 'Returned':
                            if st.button("Confirm Return", key=f"confirm_{request['id']}"):
                                # Update booking status
                                updated_bookings_df = fresh_bookings_df.copy()
                                updated_bookings_df.loc[
                                    updated_bookings_df['id'] == request['id'], 'status'] = 'Completed'
                                updated_bookings_df.to_csv('data/bookings.csv', index=False)
                                load_bookings_data.clear()
                                st.rerun()

                    st.divider()


# Render the appropriate page based on the current state
if st.session_state.page == 'home':
    show_home_page()
elif st.session_state.page == 'find_tools':
    show_find_tools_page()
elif st.session_state.page == 'tool_details':
    show_tool_details()
elif st.session_state.page == 'add_listing':
    show_add_listing()
elif st.session_state.page == 'profile':
    show_profile()
elif st.session_state.page == 'bookings':
    show_bookings()