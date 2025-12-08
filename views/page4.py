import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium

st.set_page_config(page_title="Prefecture Viewer", layout="wide")
st.title("🏛️ Prefecture Boundary Viewer")

# Load data
@st.cache_data
def load_data():
    return gpd.read_file('prefectures_with_population.geojson')

gdf = load_data()

# Prefecture selector
prefecture_names = sorted(gdf['prefecture'].unique())
selected_prefecture = st.selectbox(
    "🎯 Select a prefecture to explore:",
    prefecture_names,
    help="Choose any prefecture to see its boundaries and details"
)

# Filter data
filtered_gdf = gdf[gdf['prefecture'] == selected_prefecture]
prefecture_data = filtered_gdf.iloc[0]

# Create two columns
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"### 🗺️ {selected_prefecture} Boundaries")
    
    # Calculate bounds for selected prefecture
    bounds = prefecture_data.geometry.bounds
    min_lon, min_lat, max_lon, max_lat = bounds
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    
    # Create focused map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Add prefecture boundary
    folium.GeoJson(
        filtered_gdf.iloc[0:1],
        style_function=lambda x: {
            'fillColor': 'lightblue',
            'color': 'darkblue',
            'weight': 4,
            'fillOpacity': 0.7
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['prefecture', 'PopCount'],
            aliases=['Prefecture:', 'Population:'],
            style="font-size: 16px; font-weight: bold;"
        )
    ).add_to(m)
    
    # Fit to prefecture bounds
    padding = 0.01
    m.fit_bounds([
        [min_lat - padding, min_lon - padding],
        [max_lat + padding, max_lon + padding]
    ])
    
    st_folium(m, width=800, height=500)

with col2:
    st.markdown(f"### 📊 {selected_prefecture} Details")
    
    # Display metrics
    st.metric("Population", f"{prefecture_data['PopCount']:,}")
    
    # Rank calculation
    rank = (gdf['PopCount'] > prefecture_data['PopCount']).sum() + 1
    st.metric("Population Rank", f"{rank} of {len(gdf)}")
    
    # Area calculation
    area = (max_lat - min_lat) * (max_lon - min_lon)
    st.metric("Area", f"{area:.4f} deg²")
    
    # Coordinates
    st.write("**Boundaries:**")
    st.write(f"• North: {max_lat:.4f}°")
    st.write(f"• South: {min_lat:.4f}°")
    st.write(f"• East: {max_lon:.4f}°")
    st.write(f"• West: {min_lon:.4f}°")
    st.write(f"• Center: ({center_lat:.4f}°, {center_lon:.4f}°)")

# Population comparison
st.markdown("---")
st.markdown("### 📈 Population Comparison")

# Show how this prefecture compares
avg_pop = gdf['PopCount'].mean()
diff = prefecture_data['PopCount'] - avg_pop
percentage_diff = (diff / avg_pop) * 100

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Prefecture Population", f"{prefecture_data['PopCount']:,}")
with col2:
    st.metric("National Average", f"{avg_pop:,.0f}")
with col3:
    st.metric("Difference", f"{diff:+,.0f}", f"{percentage_diff:+.1f}%")

# Show neighboring or similar prefectures
st.markdown("### 🔍 Similar Prefectures")
tolerance = 1000
similar_prefs = gdf[
    abs(gdf['PopCount'] - prefecture_data['PopCount']) <= tolerance
]['prefecture'].tolist()

if len(similar_prefs) > 1:
    st.write(f"Prefectures with similar population (±{tolerance:,}):")
    for pref in similar_prefs:
        pop = gdf[gdf['prefecture'] == pref]['PopCount'].iloc[0]
        st.write(f"• **{pref}**: {pop:,}")
else:
    st.write("No prefectures with similar population found.")