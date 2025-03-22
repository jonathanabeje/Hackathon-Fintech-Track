import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
from datetime import datetime, timedelta
import os
import random
from utils import create_tool_map, generate_mock_reviews, format_currency, get_placeholder_image_url


# UI Component for tool cards in grid view
def render_tool_card(tool, key_prefix="tool"):
    """Render a card for a tool in grid view"""
    st.image(get_placeholder_image_url(tool['title']), use_column_width=True)
    st.markdown(f"### {tool['title']}")
    st.write(f"**{format_currency(tool['daily_rate'])}/day** · {tool['neighborhood']}")
    st.write(f"Rating: {tool['rating']}/5 ({tool['review_count']} reviews)")

    if st.button(f"View Details", key=f"{key_prefix}_{tool['id']}"):
        st.session_state.selected_tool = tool['id']
        st.session_state.page = 'tool_details'
        st.rerun()

    st.divider()


# UI Component for the metrics dashboard
def render_dashboard_metrics(metrics):
    """Render the metrics dashboard for the home page"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['available_tools']}</div>
            <div class="metric-label">Available Tools</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['avg_savings_percentage']}%</div>
            <div class="metric-label">Average Savings</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_currency(metrics['community_savings'])}</div>
            <div class="metric-label">Community Savings</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['user_satisfaction']}/5</div>
            <div class="metric-label">User Satisfaction</div>
        </div>
        """, unsafe_allow_html=True)


# UI Component for the sidebar navigation
def render_sidebar(users_df):
    """Render the sidebar navigation"""
    with st.sidebar:
        st.image(get_placeholder_image_url("ToolShare", 150, 80), width=150)
        st.markdown("### Welcome to ToolShare")

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
                login_button = st.form_submit_button("Login")

                if login_button:
                    if username in users_df['username'].values:
                        st.session_state.user_logged_in = True
                        st.session_state.current_user = username
                        st.rerun()
                    else:
                        st.error("Invalid username. Please try again.")

            # Demo quick login
            if st.button("Use Demo Account"):
                st.session_state.user_logged_in = True
                st.session_state.current_user = "demo_user"
                st.rerun()

        st.divider()

        # Navigation
        st.markdown("### Navigation")
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
        st.markdown("### About")
        st.markdown("""
            ToolShare connects neighbors to share 
            tools and equipment, saving money 
            and reducing waste.
        """)


# UI Component for the Filter Tools panel
def render_tool_filters(tools_df):
    """Render the filter options for tools"""
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

    # Return the selected filters
    return {
        "tool_type": selected_type,
        "neighborhood": selected_neighborhood,
        "price_range": price_range
    }


# UI Component for the tool booking form
def render_booking_form(tool):
    """Render the booking form for a tool"""
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
            st.write(f"**Total Cost:** {format_currency(total_cost)}")

            if tool['deposit'] > 0:
                st.write(f"**Security Deposit:** {format_currency(tool['deposit'])} (refundable)")

        # Submit button
        submit_booking = st.form_submit_button("Book Now")

        if submit_booking:
            if not st.session_state.user_logged_in:
                st.error("Please log in to book this tool.")
                return None

            if end_date < start_date:
                st.error("Please correct the date selection.")
                return None

            # Return booking data
            return {
                "tool_id": tool['id'],
                "renter_username": st.session_state.current_user,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "total_cost": total_cost,
                "status": "Pending"
            }

    return None


# UI Component for the add tool form
def render_add_tool_form(tools_df, users_df):
    """Render the form for adding a new tool listing"""
    with st.form("add_tool_form"):
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

        description = st.text_area("Description", height=100)

        # Image upload (simulated for the hackathon)
        st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        st.info(
            "For the hackathon demo, uploaded images won't be processed, and placeholder images will be used instead.")

        submit = st.form_submit_button("Create Listing")

        if submit:
            if not title or not description:
                st.error("Please fill in all required fields.")
                return None

            # Get user data
            user_data = users_df[users_df['username'] == st.session_state.current_user].iloc[0]

            # Prepare neighborhood coordinates (in a real app, would use geocoding)
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

            # Return tool data
            return {
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
                "image_path": "images/placeholder.jpg",
                "available": True
            }

    return None


# UI Component for displaying user bookings
def render_user_bookings(bookings_df, tools_df, is_owner=False):
    """Render the user's bookings"""
    if bookings_df.empty:
        if is_owner:
            st.info("You don't have any rental requests for your tools.")
        else:
            st.info("You haven't rented any tools yet.")
            if st.button("Find Tools to Rent"):
                st.session_state.page = 'find_tools'
                st.rerun()
        return

    # Display bookings in cards
    for _, booking in bookings_df.iterrows():
        # Get tool details
        tool_id = booking['tool_id']
        tool_data = tools_df[tools_df['id'] == tool_id]

        if tool_data.empty:
            continue

        tool = tool_data.iloc[0]

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.markdown(f"### {tool['title']}")
            st.markdown(f"**Booking ID:** {booking['id']}")

            if is_owner:
                renter_username = booking['renter_username']
                st.markdown(f"**Renter:** {renter_username}")
            else:
                st.markdown(f"**Owner:** {tool['owner_name']}")

        with col2:
            st.markdown(f"**Dates:** {booking['start_date']} to {booking['end_date']}")
            st.markdown(f"**Total Cost:** {format_currency(booking['total_cost'])}")
            st.markdown(f"**Status:** {booking['status']}")

        with col3:
            # Different actions based on booking status and whether the user is the owner
            if is_owner:
                if booking['status'] == 'Pending':
                    if st.button("Approve", key=f"approve_{booking['id']}"):
                        return {'action': 'approve', 'booking_id': booking['id']}

                    if st.button("Decline", key=f"decline_{booking['id']}"):
                        return {'action': 'decline', 'booking_id': booking['id']}

                elif booking['status'] == 'Returned':
                    if st.button("Confirm Return", key=f"confirm_{booking['id']}"):
                        return {'action': 'confirm_return', 'booking_id': booking['id']}
            else:
                if booking['status'] == 'Pending':
                    if st.button("Cancel", key=f"cancel_{booking['id']}"):
                        return {'action': 'cancel', 'booking_id': booking['id']}

                elif booking['status'] == 'Approved':
                    if st.button("Return", key=f"return_{booking['id']}"):
                        return {'action': 'return', 'booking_id': booking['id']}

        st.divider()

    return None


# UI Component for displaying user's tools
def render_user_tools(user_tools):
    """Render the user's tool listings"""
    if user_tools.empty:
        st.info("You haven't listed any tools yet.")
        if st.button("Add Your First Tool"):
            st.session_state.page = 'add_listing'
            st.rerun()
        return None

    for _, tool in user_tools.iterrows():
        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.markdown(f"### {tool['title']}")
            st.markdown(f"{tool['description'][:100]}...")

        with col2:
            st.markdown(f"**Daily Rate:** {format_currency(tool['daily_rate'])}")
            st.markdown(f"**Status:** {'Available' if tool['available'] else 'Not Available'}")

        with col3:
            if st.button("Edit", key=f"edit_{tool['id']}"):
                # In a real app, this would take you to an edit page
                st.info("Edit functionality not implemented in the demo.")
                return None

            if tool['available']:
                if st.button("Mark Unavailable", key=f"unavail_{tool['id']}"):
                    return {'action': 'mark_unavailable', 'tool_id': tool['id']}
            else:
                if st.button("Mark Available", key=f"avail_{tool['id']}"):
                    return {'action': 'mark_available', 'tool_id': tool['id']}

        st.divider()

    return None


# UI Component for displaying tool reviews
def render_tool_reviews(tool):
    """Render reviews for a tool"""
    st.markdown("### Reviews")

    # Generate some mock reviews
    review_count = min(3, tool['review_count'])
    if review_count > 0:
        reviews = generate_mock_reviews(review_count)

        for review in reviews:
            st.markdown(f"""
            <div class="card">
                <p>⭐ {review['rating']}/5</p>
                <p><em>"{review['comment']}"</em></p>
                <p>- Anonymous User, {review['date']}</p>
            </div>
            """, unsafe_allow_html=True)

        if tool['review_count'] > 3:
            st.button(f"View all {tool['review_count']} reviews")
    else:
        st.info("This tool has no reviews yet.")