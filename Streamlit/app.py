import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium import plugins
from get_similar_groups import get_groups_for_user

# Custom CSS for styling
st.markdown("""
<style>
    /* Global Styles */
    body {
        font-family: 'Arial', sans-serif;
        color: #2C3E50;
        background-color: #F4F7F9;
    }

    /* Main Title Container */
    .main-title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #2C3E50, #3498DB);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        animation: fadeIn 0.5s ease-in-out;
    }
    
    .main-header {
        font-size: 3rem;
        color: white;
        text-align: center;
        margin: 0;
        font-family: 'Roboto', sans-serif;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.2);
    }
    
    .logo-img {
        width: 60px;
        height: 60px;
        margin-right: 20px;
        animation: float 2s infinite ease-in-out;
    }
    
    /* Section Header Container */
    .section-header-container {
        display: flex;
        align-items: center;
        background: #FFFFFF;
        padding: 1.5rem 2rem;
        border-left: 6px solid #3498DB;
        margin: 2rem 0;
        border-radius: 0 10px 10px 0;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .section-header-container:hover {
        background: #EAF6FF;
        transform: translateX(5px);
    }

    .section-header {
        font-size: 2rem;
        color: #2C3E50;
        margin: 0;
        font-weight: bold;
    }
    
    .section-icon {
        font-size: 2rem;
        color: #3498DB;
        margin-right: 15px;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
</style>
""", unsafe_allow_html=True)



# Sample Query Results with Additional Amenities
query_results = [
    {
        "apt_address": "123 Main St",
        "apt_bedroom_count": 2,
        "apt_bathroom_count": 1,
        "apt_rent": 3400,
        "apt_living_area": 850,
        "apt_transit_score": 85,
        "apt_latitude": 42.345,
        "apt_longitude": -71.089,
        "apt_url": "https://www.zillow.com//apartments/123-main-st/",
        "apt_image_url": "https://via.placeholder.com/150",
        "apt_zip_code": "02115",
        "apt_building_name": "The Plaza",
        "apt_unit": "5B",
        "restaurants": [
            {"name": "Pizza Palace", "yelp_link": "https://yelp.com/pizza-palace", "cuisine": "Italian", "walking_time": "5 mins"},
            {"name": "Burger Bistro", "yelp_link": "https://yelp.com/burger-bistro", "cuisine": "American", "walking_time": "7 mins"},
            {"name": "Sushi Spot", "yelp_link": "https://yelp.com/sushi-spot", "cuisine": "Japanese", "walking_time": "9 mins"}
        ],
        "parks": [
            {"name": "Central Park", "walking_distance": "3 mins"},
            {"name": "Riverside Park", "walking_distance": "8 mins"},
            {"name": "Elm Grove", "walking_distance": "10 mins"}
        ],
        "subway_stations": [
            {"name": "Downtown Station", "walking_time": "6 mins"},
            {"name": "City Center Station", "walking_time": "9 mins"}
        ]
    },
    {
        "apt_address": "456 Elm St",
        "apt_bedroom_count": 3,
        "apt_bathroom_count": 2,
        "apt_rent": 4500,
        "apt_living_area": 1200,
        "apt_transit_score": 90,
        "apt_latitude": 42.350,
        "apt_longitude": -71.080,
        "apt_url": "https://www.zillow.com//apartments/456-elm-st/",
        "apt_image_url": "https://via.placeholder.com/150",
        "apt_zip_code": "02116",
        "apt_building_name": "CityView Apartments",
        "apt_unit": "7A",
        "restaurants": [
            {"name": "Taco Town", "yelp_link": "https://yelp.com/taco-town", "cuisine": "Mexican", "walking_time": "4 mins"},
            {"name": "Pasta Place", "yelp_link": "https://yelp.com/pasta-place", "cuisine": "Italian", "walking_time": "6 mins"},
            {"name": "Curry Corner", "yelp_link": "https://yelp.com/curry-corner", "cuisine": "Indian", "walking_time": "8 mins"}
        ],
        "parks": [
            {"name": "Lakeside Park", "walking_distance": "5 mins"},
            {"name": "Green Meadows", "walking_distance": "7 mins"},
            {"name": "Hilltop View", "walking_distance": "9 mins"}
        ],
        "subway_stations": [
            {"name": "Uptown Station", "walking_time": "5 mins"},
            {"name": "East Side Station", "walking_time": "8 mins"}
        ]
    }
]

user_text = 'Meditation is very good. Nowadays people are becoming aware of the importance of meditation. Many hi'

meetup_results = get_groups_for_user(user_text)


# Convert query results to DataFrame
df = pd.DataFrame(query_results)

# Streamlit App Title
st.markdown("""
<div class="main-title-container">
    <span class="section-icon">🏢</span>
    <h1 class="main-header">Recommended Apartments</h1>
</div>
""", unsafe_allow_html=True)

# Interactive Map
st.markdown("""
<div class="section-header-container">
    <span class="section-icon">🗺️</span>
    <h2 class="section-header">Apartment Locations</h2>
</div>
""", unsafe_allow_html=True)

# Create enhanced map
m = folium.Map(
    location=[df["apt_latitude"].mean(), df["apt_longitude"].mean()],
    zoom_start=14,
    tiles='cartodbpositron',
    control_scale=True
)

# Add additional tile layers
#folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(m)

# Add markers with enhanced styling
for _, apartment in df.iterrows():
    popup_content = f"""
    <div style="width: 200px; font-family: Arial;">
        <h4 style="color: #2C3E50; margin: 0;">{apartment['apt_building_name']}</h4>
        <p style="margin: 5px 0;"><strong>Unit:</strong> {apartment['apt_unit']}</p>
        <p style="margin: 5px 0;"><strong>Rent:</strong> ${apartment['apt_rent']}</p>
        <p style="margin: 5px 0;"><strong>Specs:</strong> {apartment['apt_bedroom_count']}BR/{apartment['apt_bathroom_count']}BA</p>
    </div>
    """
    
    icon = folium.Icon(
        color='blue',
        icon='home',
        prefix='fa',
        icon_color='white'
    )
    
    folium.Marker(
        location=[apartment["apt_latitude"], apartment["apt_longitude"]],
        popup=folium.Popup(popup_content, max_width=300),
        tooltip=apartment["apt_building_name"],
        icon=icon
    ).add_to(m)

# Add additional map controls
plugins.Fullscreen().add_to(m)
plugins.MeasureControl(position='bottomleft').add_to(m)
folium.LayerControl().add_to(m)

# Render Map in Streamlit
st_folium(m, width=700, height=500)

# Detailed Apartment Listings with Amenities
st.markdown("""
<div class="section-header-container">
    <span class="section-icon">🏢</span>
    <h2 class="section-header">Apartment Details</h2>
</div>
""", unsafe_allow_html=True)

for apartment in query_results:
    st.markdown(f"""
    <div style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); padding: 20px; margin-bottom: 30px;">
        <div style="display: flex; align-items: flex-start;">
            <div style="flex: 1;">
                <h2 style="color: #3498DB; margin-top: 0;">{apartment["apt_building_name"]} - Unit {apartment['apt_unit']}</h2>
                <p style="color: #7f8c8d; font-size: 14px;"><i class="fas fa-map-marker-alt"></i> {apartment['apt_address']}</p>
                <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                    <div>
                        <p style="font-weight: bold; color: #2C3E50;">💰 ${apartment['apt_rent']}/month</p>
                        <p style="color: #7f8c8d;">🛏 {apartment['apt_bedroom_count']} BR | 🚿 {apartment['apt_bathroom_count']} BA</p>
                        <p style="color: #7f8c8d;">📐 {apartment['apt_living_area']} sq ft</p>
                    </div>
                    <div>
                        <p style="font-weight: bold; color: #2C3E50;">🚇 Transit Score: {apartment['apt_transit_score']}</p>
                        <a href="{apartment['apt_url']}" target="_blank" style="display: inline-block; background-color: #3498DB; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; margin-top: 10px;">View Listing</a>
                    </div>
                </div>
            </div>
            <img src="{apartment["apt_image_url"]}" style="width: 200px; height: 150px; object-fit: cover; border-radius: 5px; margin-left: 20px;" alt="Apartment Image">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.expander("🍴 Nearby Restaurants"):
            for restaurant in apartment["restaurants"]:
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #2C3E50;">{restaurant['name']}</h4>
                    <p style="margin: 5px 0; color: #7f8c8d;">🍽 {restaurant['cuisine']}</p>
                    <p style="margin: 5px 0; color: #7f8c8d;">🚶‍♂️ {restaurant['walking_time']} walk</p>
                    <a href="{restaurant['yelp_link']}" target="_blank" style="color: #3498DB; text-decoration: none;">View on Yelp</a>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        with st.expander("🌳 Nearby Parks"):
            for park in apartment["parks"]:
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #2C3E50;">{park['name']}</h4>
                    <p style="margin: 5px 0; color: #7f8c8d;">🚶‍♂️ {park['walking_distance']} walk</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col3:
        with st.expander("🚇 Nearby Subway Stations"):
            for station in apartment["subway_stations"]:
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #2C3E50;">{station['name']}</h4>
                    <p style="margin: 5px 0; color: #7f8c8d;">🚶‍♂️ {station['walking_time']} walk</p>
                </div>
                """, unsafe_allow_html=True)


# Section Header for Meetup Groups
st.markdown("""
<div class="section-header-container">
    <span class="section-icon">🤝</span>
    <h2 class="section-header">Meet Your Groups</h2>
</div>
""", unsafe_allow_html=True)

# Display Meetup Groups
for group in meetup_results:
    st.markdown(f"""
    <div style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); padding: 20px; margin-bottom: 30px;">
        <h3 style="color: #2C3E50; margin-top: 0;">{group["meetup_group_name"]}</h3>
        <p style="color: #7f8c8d;"><strong>Members:</strong> {group["meetup_group_member_count"]}</p>
        <p style="color: #34495e; margin-top: 15px;">{group["meetup_group_description"]}</p>
        <a href="{group['meetup_group_link']}" target="_blank" style="display: inline-block; background-color: #3498DB; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; margin-top: 10px;">Visit Meetup Page</a>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📅 Past Events"):
        for event in group["meetup_group_past_events"]:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <p style="margin: 0; color: #2C3E50;">{event}</p>
            </div>
            """, unsafe_allow_html=True)