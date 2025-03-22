import pandas as pd
import os
import random
from datetime import datetime, timedelta


# Function to initialize data directories
def initialize_data_directories():
    """Create necessary directories for data storage"""
    os.makedirs('data', exist_ok=True)
    os.makedirs('images', exist_ok=True)


# Functions to generate mock data for the demo
def generate_mock_users():
    """Generate mock user data for the demo"""
    users = [
        {"username": "john_diy", "name": "John Smith", "email": "john@example.com"},
        {"username": "sarah_maker", "name": "Sarah Johnson", "email": "sarah@example.com"},
        {"username": "mike_build", "name": "Mike Chen", "email": "mike@example.com"},
        {"username": "lisa_craft", "name": "Lisa Rodriguez", "email": "lisa@example.com"},
        {"username": "david_tools", "name": "David Wilson", "email": "david@example.com"},
        {"username": "emma_fix", "name": "Emma Brown", "email": "emma@example.com"},
        {"username": "demo_user", "name": "Demo User", "email": "demo@toolshare.com"}
    ]

    df = pd.DataFrame(users)
    df.to_csv('data/users.csv', index=False)
    return df


def generate_mock_tools(users_df):
    """Generate mock tool listings for the demo"""
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

    # Generate 50 mock tools
    mock_data = []

    for i in range(50):
        neighborhood = random.choice(list(neighborhoods.keys()))
        lat, lon = neighborhoods[neighborhood]
        # Add small random variation to lat/lon to spread tools out
        lat += random.uniform(-0.01, 0.01)
        lon += random.uniform(-0.01, 0.01)

        owner = users_df.iloc[random.randint(0, len(users_df) - 1)]

        tool_type = random.choice(tool_types)
        brand = random.choice(brands)

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
            "image_path": f"images/tool_{i + 1}.jpg",  # Placeholder image paths
            "available": random.random() > 0.2  # 80% of tools are available
        })

    df = pd.DataFrame(mock_data)
    df.to_csv('data/tools.csv', index=False)
    return df


def initialize_bookings():
    """Initialize an empty bookings dataframe"""
    bookings_df = pd.DataFrame(columns=[
        "id", "tool_id", "renter_username", "start_date", "end_date",
        "total_cost", "status", "created_at"
    ])
    bookings_df.to_csv('data/bookings.csv', index=False)
    return bookings_df


# Data loading functions
def load_user_data():
    """Load user data from CSV file or generate if it doesn't exist"""
    if os.path.exists('data/users.csv'):
        return pd.read_csv('data/users.csv')
    else:
        return generate_mock_users()


def load_tool_data():
    """Load tool data from CSV file or generate if it doesn't exist"""
    if os.path.exists('data/tools.csv'):
        return pd.read_csv('data/tools.csv')
    else:
        users_df = load_user_data()
        return generate_mock_tools(users_df)


def load_bookings_data():
    """Load bookings data from CSV file or initialize if it doesn't exist"""
    if os.path.exists('data/bookings.csv'):
        return pd.read_csv('data/bookings.csv')
    else:
        return initialize_bookings()


# Data manipulation functions
def add_tool_listing(tool_data):
    """Add a new tool listing to the database"""
    tools_df = load_tool_data()

    # Assign new ID
    tool_id = tools_df['id'].max() + 1 if not tools_df.empty else 1
    tool_data["id"] = tool_id

    # Create new row
    new_tool = pd.DataFrame([tool_data])

    # Append to tools dataframe
    updated_df = pd.concat([tools_df, new_tool], ignore_index=True)
    updated_df.to_csv('data/tools.csv', index=False)

    return tool_id


def update_tool_availability(tool_id, available):
    """Update the availability of a tool"""
    tools_df = load_tool_data()
    tools_df.loc[tools_df['id'] == tool_id, 'available'] = available
    tools_df.to_csv('data/tools.csv', index=False)


def create_booking(booking_data):
    """Create a new booking in the database"""
    bookings_df = load_bookings_data()

    # Assign new ID
    booking_id = bookings_df['id'].max() + 1 if not bookings_df.empty else 1
    booking_data["id"] = booking_id
    booking_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create new row
    new_booking = pd.DataFrame([booking_data])

    # Append to bookings dataframe
    updated_df = pd.concat([bookings_df, new_booking], ignore_index=True)
    updated_df.to_csv('data/bookings.csv', index=False)

    return booking_id


def update_booking_status(booking_id, status):
    """Update the status of a booking"""
    bookings_df = load_bookings_data()
    bookings_df.loc[bookings_df['id'] == booking_id, 'status'] = status
    bookings_df.to_csv('data/bookings.csv', index=False)


# Helper functions for the application
def calculate_booking_cost(tool_id, start_date, end_date):
    """Calculate the total cost of a booking"""
    tools_df = load_tool_data()
    tool = tools_df[tools_df['id'] == tool_id].iloc[0]

    # Convert string dates to datetime if necessary
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Calculate duration in days
    duration_days = (end_date - start_date).days
    if duration_days == 0:
        duration_days = 1  # Minimum 1 day

    total_cost = duration_days * tool['daily_rate']

    return {
        "duration_days": duration_days,
        "daily_rate": tool['daily_rate'],
        "total_cost": total_cost,
        "deposit": tool['deposit']
    }


def get_tool_details(tool_id):
    """Get detailed information about a specific tool"""
    tools_df = load_tool_data()
    tool = tools_df[tools_df['id'] == tool_id]

    if tool.empty:
        return None

    return tool.iloc[0].to_dict()


def get_user_tools(username):
    """Get all tools owned by a specific user"""
    tools_df = load_tool_data()
    user_tools = tools_df[tools_df['owner_username'] == username]
    return user_tools


def get_user_bookings(username):
    """Get all bookings made by a specific user"""
    bookings_df = load_bookings_data()
    user_bookings = bookings_df[bookings_df['renter_username'] == username]
    return user_bookings


def get_tool_bookings(tool_id):
    """Get all bookings for a specific tool"""
    bookings_df = load_bookings_data()
    tool_bookings = bookings_df[bookings_df['tool_id'] == tool_id]
    return tool_bookings


def get_rental_requests_for_user(username):
    """Get all rental requests for tools owned by a specific user"""
    tools_df = load_tool_data()
    bookings_df = load_bookings_data()

    # Get all tools owned by the user
    user_tools = tools_df[tools_df['owner_username'] == username]

    if user_tools.empty:
        return pd.DataFrame()

    # Get all bookings for those tools
    tool_ids = user_tools['id'].tolist()
    rental_requests = bookings_df[bookings_df['tool_id'].isin(tool_ids)]

    return rental_requests


def initialize_data():
    """Initialize all data for the application"""
    initialize_data_directories()
    users_df = load_user_data()
    tools_df = load_tool_data()
    bookings_df = load_bookings_data()

    return {
        "users": users_df,
        "tools": tools_df,
        "bookings": bookings_df
    }


# Call this function to set up the data when the module is imported
if __name__ == "__main__":
    initialize_data()