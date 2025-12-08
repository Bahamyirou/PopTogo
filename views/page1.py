import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import json

# Configure the Streamlit page
st.set_page_config(
    page_title="Togo Prefecture Population Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# App title and description
st.title("🇹🇬 Togo Prefecture Population Distribution")
st.markdown("---")
st.markdown("### Interactive map showing population counts by prefecture")
st.markdown("*Hover over any prefecture to see its name and population count*")

# Create a container for the map
with st.container():
    try:
        # Load the geojson with population data
        gdf = gpd.read_file('prefectures_with_population.geojson')
        
        # Calculate map center
        center_lat = gdf.geometry.centroid.y.mean()
        center_lon = gdf.geometry.centroid.x.mean()
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon], 
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Add choropleth layer
        folium.Choropleth(
            geo_data=gdf,
            data=gdf,
            columns=['prefecture', 'PopCount'],  # Adjust 'NAME' to your prefecture column
            key_on='feature.properties.prefecture',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Population Count'
        ).add_to(m)
        
        # Add interactive features with detailed hover
        folium.GeoJson(
            gdf,
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': 'blue',
                'weight': 1,
                'fillOpacity': 0
            },
            popup=folium.GeoJsonPopup(
                fields=['prefecture', 'PopCount'],
                aliases=['Prefecture:', 'Population:'],
                localize=True,
                labels=True
            ),
            tooltip=folium.GeoJsonTooltip(
                fields=['prefecture', 'PopCount'],
                aliases=['Prefecture:', 'Population:'],
                localize=True,
                sticky=False,
                labels=True,
                style="""
                    background-color: white;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """,
                max_width=800
            )
        ).add_to(m)
        
        # Display the map in Streamlit
        st_data = st_folium(m, width=1200, height=600)
        
        # Display some statistics in the sidebar or below map
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Prefectures", len(gdf))
        
        with col2:
            st.metric("Total Population", f"{gdf['PopCount'].sum():,}")
        
        with col3:
            st.metric("Average Population", f"{gdf['PopCount'].mean():,.0f}")
        
        with col4:
            st.metric("Highest Population", f"{gdf['PopCount'].max():,}")
        
        # Show top 5 prefectures by population
        st.markdown("### 🏆 Top 5 Prefectures by Population")
        top_5 = gdf.nlargest(5, 'PopCount')[['prefecture', 'PopCount']]
        top_5.index = range(1, len(top_5) + 1)
        st.dataframe(top_5, use_container_width=True)
        
    except FileNotFoundError:
        st.error("❌ Error: 'prefectures_with_population.geojson' file not found!")
        st.markdown("Please make sure the GeoJSON file is in the same directory as this app.")
        
    except Exception as e:
        st.error(f"❌ Error loading the map: {str(e)}")
        st.markdown("Please check your data file and try again.")

# Footer
st.markdown("---")
st.markdown("*Data visualization built with Streamlit and Folium*")