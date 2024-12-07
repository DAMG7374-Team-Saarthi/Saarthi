import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium import plugins
from get_similar_groups import get_groups_for_user
from get_transformed_apartment_data import transform_apartment_data

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
    "Apartment": {
      "apt_address": "19 Peterborough St, Boston, MA",
      "apt_unit": 1,
      "apt_building_name": "NotAvailable",
      "apt_rent": "$3350",
      "apt_bedroom_count": 2,
      "apt_bathroom_count": 1,
      "apt_living_area": "nan sq ft",
      "apt_transit_score Score": 95,
      "apt_latitude": 42.34434,
      "apt_longitude": -71.09599,
      "apt_url": "https://www.zillow.com//apartments/boston-ma/19-peterborough-st-apt-33/5Xj92v/",
      "apt_image_url": "https://photos.zillowstatic.com/fp/f1ef1bfd8fc7ec162529d78a526f38f2-p_e.jpg"
    },
    "Nearby Places": {
      "Parks": [
        {
          "openspace_name": "Agassiz Road",
          "openspace_type": "Parkways, Reservations & Beaches",
          "distance": "0.5 km",
          "walking_time Time": "7 mins"
        },
        {
          "openspace_name": "Ramler Park",
          "openspace_type": "Parks, Playgrounds & Athletic Fields",
          "distance": "0.5 km",
          "walking_time Time": "7 mins"
        },
        {
          "openspace_name": "Park Drive I",
          "openspace_type": "Parkways, Reservations & Beaches",
          "distance": "0.6 km",
          "walking_time Time": "9 mins"
        }
      ],
      "Restaurants": [
        {
          "restaurant_name": "Blaze Pizza",
          "restaurant_cuisine": "Other",
          "restaurant_rating": 4.0,
          "distance": "0.1 km",
          "walking_time Time": "2 mins",
          "restaurant_url": "https://www.yelp.com/biz/blaze-pizza-boston?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        },
        {
          "restaurant_name": "Citizen Public House & Oyster Bar",
          "restaurant_cuisine": "Other",
          "restaurant_rating": 3.7,
          "distance": "0.2 km",
          "walking_time Time": "2 mins",
          "restaurant_url": "https://www.yelp.com/biz/citizen-public-house-and-oyster-bar-boston?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        },
        {
          "restaurant_name": "Wow Tikka",
          "restaurant_cuisine": "Indian",
          "restaurant_rating": 4.7,
          "distance": "0.3 km",
          "walking_time Time": "4 mins",
          "restaurant_url": "https://www.yelp.com/biz/wow-tikka-boston-2?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        }
      ],
      "Subway Stations": [
        {
          "subway_station_name": "Fenway",
          "subway_line": "GREEN",
          "subway_route": "D - Riverside",
          "distance": "0.9 km",
          "walking_time": "13 mins"
        },
        {
          "subway_station_name": "Museum Of Fine Arts",
          "subway_line": "GREEN",
          "subway_route": "E - Health Street",
          "distance": "1.1 km",
          "walking_time": "15 mins"
        }
      ]
    }
  },
  {
    "Apartment": {
      "apt_address": "100 Queensberry St, Boston, MA",
      "apt_unit": 2,
      "apt_building_name": "NotAvailable",
      "apt_rent": "$3400",
      "apt_bedroom_count": 2,
      "apt_bathroom_count": 1,
      "apt_living_area": "nan sq ft",
      "apt_transit_score Score": 80,
      "apt_latitude": 42.341835,
      "apt_longitude": -71.09955,
      "apt_url": "https://www.zillow.com//b/100-queensberry-street-boston-ma-5Xj8JZ/",
      "apt_image_url": "https://photos.zillowstatic.com/fp/884091dc7b30e72320fdc393ce3d1cdc-p_e.jpg"
    },
    "Nearby Places": {
      "Parks": [
        {
          "openspace_name": "Ramler Park",
          "openspace_type": "Parks, Playgrounds & Athletic Fields",
          "distance": "0.3 km",
          "walking_time Time": "4 mins"
        },
        {
          "openspace_name": "Park Drive I",
          "openspace_type": "Parkways, Reservations & Beaches",
          "distance": "0.4 km",
          "walking_time Time": "5 mins"
        },
        {
          "openspace_name": "Park Drive II",
          "openspace_type": "Parkways, Reservations & Beaches",
          "distance": "0.4 km",
          "walking_time Time": "5 mins"
        }
      ],
      "Restaurants": [
        {
          "restaurant_name": "Wow Tikka",
          "restaurant_cuisine": "Indian",
          "restaurant_rating": 4.7,
          "distance": "0.2 km",
          "walking_time Time": "3 mins",
          "restaurant_url": "https://www.yelp.com/biz/wow-tikka-boston-2?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        },
        {
          "restaurant_name": "Rod Thai Family Taste",
          "restaurant_cuisine": "Other",
          "restaurant_rating": 4.0,
          "distance": "0.2 km",
          "walking_time Time": "3 mins",
          "restaurant_url": "https://www.yelp.com/biz/rod-thai-family-taste-boston-2?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        },
        {
          "restaurant_name": "The Greek Gyro",
          "restaurant_cuisine": "Other",
          "restaurant_rating": 4.6,
          "distance": "0.2 km",
          "walking_time Time": "3 mins",
          "restaurant_url": "https://www.yelp.com/biz/the-greek-gyro-boston-2?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        }
      ],
      "Subway Stations": [
        {
          "subway_station_name": "Fenway",
          "subway_line": "GREEN",
          "subway_route": "D - Riverside",
          "distance": "0.7 km",
          "walking_time": "10 mins"
        },
        {
          "subway_station_name": "Museum Of Fine Arts",
          "subway_line": "GREEN",
          "subway_route": "E - Health Street",
          "distance": "1.0 km",
          "walking_time": "15 mins"
        }
      ]
    }
  },
  {
    "Apartment": {
      "apt_address": "12 Aberdeen St #2, Boston, MA 02215",
      "apt_unit": 99,
      "apt_building_name": "NotAvailable",
      "apt_rent": "$3400",
      "apt_bedroom_count": 2,
      "apt_bathroom_count": 1,
      "apt_living_area": "768.0 sq ft",
      "apt_transit_score Score": 85,
      "apt_latitude": 42.346367,
      "apt_longitude": -71.10357,
      "apt_url": "https://www.zillow.com//homedetails/12-Aberdeen-St-2-Boston-MA-02215/59168538_zpid/",
      "apt_image_url": "https://photos.zillowstatic.com/fp/e5ab84c31704cd93bd25d3bc1eb83be2-p_e.jpg"
    },
    "Nearby Places": {
      "Parks": [
        {
          "openspace_name": "Park Drive I",
          "openspace_type": "Parkways, Reservations & Beaches",
          "distance": "0.5 km",
          "walking_time Time": "8 mins"
        },
        {
          "openspace_name": "Park Drive II",
          "openspace_type": "Parkways, Reservations & Beaches",
          "distance": "0.5 km",
          "walking_time Time": "8 mins"
        },
        {
          "openspace_name": "Ramler Park",
          "openspace_type": "Parks, Playgrounds & Athletic Fields",
          "distance": "0.7 km",
          "walking_time Time": "10 mins"
        }
      ],
      "Restaurants": [
        {
          "restaurant_name": "Audubon Boston",
          "restaurant_cuisine": "Other",
          "restaurant_rating": 4.2,
          "distance": "0.2 km",
          "walking_time Time": "3 mins",
          "restaurant_url": "https://www.yelp.com/biz/audubon-boston-boston?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        },
        {
          "restaurant_name": "Inchu",
          "restaurant_cuisine": "Korean",
          "restaurant_rating": 3.8,
          "distance": "0.4 km",
          "walking_time Time": "6 mins",
          "restaurant_url": "https://www.yelp.com/biz/inchu-boston?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        },
        {
          "restaurant_name": "Gogo ya",
          "restaurant_cuisine": "Mexican",
          "restaurant_rating": 3.8,
          "distance": "0.4 km",
          "walking_time Time": "6 mins",
          "restaurant_url": "https://www.yelp.com/biz/gogo-ya-boston?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        }
      ],
      "Subway Stations": [
        {
          "subway_station_name": "Fenway",
          "subway_line": "GREEN",
          "subway_route": "D - Riverside",
          "distance": "0.2 km",
          "walking_time": "4 mins"
        },
        {
          "subway_station_name": "Blandford Street",
          "subway_line": "GREEN",
          "subway_route": "B - Boston College",
          "distance": "0.6 km",
          "walking_time": "9 mins"
        },
        {
          "subway_station_name": "Boston University Central",
          "subway_line": "GREEN",
          "subway_route": "B - Boston College",
          "distance": "0.6 km",
          "walking_time": "9 mins"
        }
      ]
    }
  },
  {
    "Apartment": {
      "apt_address": "111 Queensberry St APT 5, Boston, MA 02215",
      "apt_unit": 99,
      "apt_building_name": "NotAvailable",
      "apt_rent": "$3450",
      "apt_bedroom_count": 2,
      "apt_bathroom_count": 1,
      "apt_living_area": "700.0 sq ft",
      "apt_transit_score Score": 95,
      "apt_latitude": 42.342148,
      "apt_longitude": -71.10047,
      "apt_url": "https://www.zillow.com//homedetails/111-Queensberry-St-APT-5-Boston-MA-02215/2126746418_zpid/",
      "apt_image_url": "https://photos.zillowstatic.com/fp/71e6b1d1a88aad72679808bff3f18184-p_e.jpg"
    },
    "Nearby Places": {
      "Parks": [
        {
          "openspace_name": "Ramler Park",
          "openspace_type": "Parks, Playgrounds & Athletic Fields",
          "distance": "0.1 km",
          "walking_time Time": "2 mins"
        },
        {
          "openspace_name": "Park Drive I",
          "openspace_type": "Parkways, Reservations & Beaches",
          "distance": "0.2 km",
          "walking_time Time": "3 mins"
        },
        {
          "openspace_name": "Park Drive II",
          "openspace_type": "Parkways, Reservations & Beaches",
          "distance": "0.2 km",
          "walking_time Time": "3 mins"
        }
      ],
      "Restaurants": [
        {
          "restaurant_name": "Wow Tikka",
          "restaurant_cuisine": "Indian",
          "restaurant_rating": 4.7,
          "distance": "0.3 km",
          "walking_time Time": "4 mins",
          "restaurant_url": "https://www.yelp.com/biz/wow-tikka-boston-2?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        },
        {
          "restaurant_name": "Gogo ya",
          "restaurant_cuisine": "Mexican",
          "restaurant_rating": 3.8,
          "distance": "0.3 km",
          "walking_time Time": "5 mins",
          "restaurant_url": "https://www.yelp.com/biz/gogo-ya-boston?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        },
        {
          "restaurant_name": "Rod Thai Family Taste",
          "restaurant_cuisine": "Other",
          "restaurant_rating": 4.0,
          "distance": "0.3 km",
          "walking_time Time": "3 mins",
          "restaurant_url": "https://www.yelp.com/biz/rod-thai-family-taste-boston-2?adjust_creative=LZkXjIasaeGxsBSkACtcwQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=LZkXjIasaeGxsBSkACtcwQ"
        }
      ],
      "Subway Stations": [
        {
          "subway_station_name": "Fenway",
          "subway_line": "GREEN",
          "subway_route": "D - Riverside",
          "distance": "0.5 km",
          "walking_time": "8 mins"
        },
        {
          "subway_station_name": "Museum Of Fine Arts",
          "subway_line": "GREEN",
          "subway_route": "E - Health Street",
          "distance": "0.9 km",
          "walking_time": "14 mins"
        }
      ]
    }
  }
]

# Transform Apartment Data
query_results = transform_apartment_data(query_results)

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
    cleaned_address = apartment["apt_address"].split(',', 1)[0]
    st.markdown(f"""
    <div style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); padding: 20px; margin-bottom: 30px;">
        <div style="display: flex; align-items: flex-start;">
            <div style="flex: 1;">
                <h2 style="color: #3498DB; margin-top: 0;">{cleaned_address}</h2>
                <p style="color: #7f8c8d; font-size: 14px;"><i class="fas fa-map-marker-alt"></i> Address - {apartment['apt_address']}</p>
                <p style="color: #7f8c8d; font-size: 14px;"><i class="fas fa-map-marker-alt"></i> Unit - {apartment['apt_unit']}</p>
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