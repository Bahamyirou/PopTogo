import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import json

# Page configuration
st.set_page_config(
    page_title="Togo Population Map",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Population Map of Togo Prefectures")
st.markdown("Interactive map showing population distribution across Togo's prefectures")

# Load data
@st.cache_data
def load_data():
    try:
        gdf = gpd.read_file('population_par_prefecture.geojson')
        # Filter out entries with null population data
        return gdf[(gdf['Ensemble'].notna()) & (~gdf['prefecture'].isin(["LOME COMMUNE", "PLAINE DU MO"]))].copy()
    except FileNotFoundError:
        st.error("❌ Could not find 'population_par_prefecture.geojson' file!")
        st.stop()

gdf = load_data()

# Sidebar controls
st.sidebar.header("🎛️ Controls")

# Population type selection
population_type = st.sidebar.selectbox(
    "Population Type:",
    ["Ensemble", "Masculin", "Feminin"],
    format_func=lambda x: {"Ensemble": "Total", "Masculin": "Male", "Feminin": "Female"}[x]
)

# Color scheme
color_scheme = st.sidebar.selectbox(
    "Color Scheme:",
    ["YlOrRd", "Blues", "Greens", "Reds", "Purples", "Oranges"]
)

# Prefecture filtering
st.sidebar.header("🏘️ Prefecture Selection")

filter_option = st.sidebar.radio(
    "Filter Type:",
    ["All Prefectures", "Select Specific", "By Population Size"]
)

# Initialize filtered data
filtered_gdf = gdf.copy()

if filter_option == "Select Specific":
    selected_prefectures = st.sidebar.multiselect(
        "Choose Prefectures:",
        options=sorted(gdf['prefecture'].tolist()),
        default=[]
    )
    
    if selected_prefectures:
        filtered_gdf = gdf[gdf['prefecture'].isin(selected_prefectures)].copy()

elif filter_option == "By Population Size":
    # Population range filter
    min_pop = st.sidebar.slider(
        "Minimum Population:",
        min_value=int(gdf['Ensemble'].min()),
        max_value=int(gdf['Ensemble'].max()),
        value=int(gdf['Ensemble'].min()),
        step=10000,
        format="%d"
    )
    
    max_pop = st.sidebar.slider(
        "Maximum Population:",
        min_value=int(gdf['Ensemble'].min()),
        max_value=int(gdf['Ensemble'].max()),
        value=int(gdf['Ensemble'].max()),
        step=10000,
        format="%d"
    )
    
    filtered_gdf = gdf[
        (gdf['Ensemble'] >= min_pop) & 
        (gdf['Ensemble'] <= max_pop)
    ].copy()

# Quick preset filters
st.sidebar.subheader("⚡ Quick Presets")
col_preset1, col_preset2 = st.sidebar.columns(2)

with col_preset1:
    if st.button("🏆 Top 5"):
        filtered_gdf = gdf.nlargest(5, 'Ensemble').copy()

with col_preset2:
    if st.button("🏅 Top 10"):
        filtered_gdf = gdf.nlargest(10, 'Ensemble').copy()


# Statistics
st.sidebar.header("📊 Statistics")
st.sidebar.metric("Showing", f"{len(filtered_gdf)} of {len(gdf)} prefectures")
if not filtered_gdf.empty:
    st.sidebar.metric("Total Population", f"{filtered_gdf['Ensemble'].sum():,}")
    if len(filtered_gdf) > 1:
        st.sidebar.metric("Average Population", f"{filtered_gdf['Ensemble'].mean():,.0f}")

# Create map function
def create_map():
    m = folium.Map(location=[8.0, 1.0], zoom_start=7, tiles="OpenStreetMap")
    
    # Background layer (all prefectures)
    folium.GeoJson(
        json.loads(gdf.to_json()),
        style_function=lambda x: {
            'fillColor': '#f0f0f0', 
            'color': '#cccccc', 
            'weight': 1, 
            'fillOpacity': 0.3
        }
    ).add_to(m)
    
    # Highlighted layer (selected prefectures)
    if not filtered_gdf.empty and len(filtered_gdf) < len(gdf):
        folium.Choropleth(
            geo_data=json.loads(filtered_gdf.to_json()),
            data=filtered_gdf,
            columns=['prefecture', population_type],
            key_on='feature.properties.prefecture',
            fill_color=color_scheme,
            fill_opacity=0.8,
            line_weight=2,
            legend_name=f'{population_type} Population'
        ).add_to(m)
    
    elif len(filtered_gdf) == len(gdf):
        # Show choropleth for all when all are selected
        folium.Choropleth(
            geo_data=json.loads(filtered_gdf.to_json()),
            data=filtered_gdf,
            columns=['prefecture', population_type],
            key_on='feature.properties.prefecture',
            fill_color=color_scheme,
            fill_opacity=0.7,
            line_weight=1,
            legend_name=f'{population_type} Population'
        ).add_to(m)
    
    # Tooltips
    folium.GeoJson(
        json.loads(filtered_gdf.to_json()),
        tooltip=folium.GeoJsonTooltip(
            fields=['prefecture', 'Region', 'Ensemble', 'Masculin', 'Feminin'],
            aliases=['Prefecture:', 'Region:', 'Total:', 'Male:', 'Female:'],
        ),
        style_function=lambda x: {'fillColor': 'transparent', 'weight': 0}
    ).add_to(m)
    
    return m

# Dynamic layout based on selection size
num_selected = len(filtered_gdf)

col1, col2 = st.columns([3, 1])
    
with col1:
        st.subheader(f"📍 Map: {population_type} - All Prefectures ({num_selected})")
        map_obj = create_map()
        st_folium(map_obj, width=800, height=600)
    
with col2:
        st.subheader("📊 Overview")
        
        # Key metrics
        st.metric("Total Prefectures", f"{num_selected}")
        st.metric("Combined Population", f"{filtered_gdf['Ensemble'].sum():,}")
        st.metric("Average Population", f"{filtered_gdf['Ensemble'].mean():,.0f}")
        
        # Top performers
        st.write("**🏆 Largest Prefectures:**")
        top_3 = filtered_gdf.nlargest(3, 'Ensemble')
        for i, (_, row) in enumerate(top_3.iterrows(), 1):
            st.write(f"{i}. **{row['prefecture']}**")
            st.write(f"   {row['Ensemble']:,} people")
        
        
  
  # Full width section below
st.markdown("---")
st.markdown("### 🏘️ Detailed By Region")

# Regional summary
#st.write("**🏘️ :**")
region_summary = filtered_gdf.groupby('Region').agg({
            'prefecture': 'count',
            'Ensemble': 'sum'
        })
        
for region, stats in region_summary.iterrows():
            pref_count = stats['prefecture']
            pop_total = stats['Ensemble']
            st.write(f"• **{region}**: {pref_count} pref. ({pop_total:,})")
# Rest of your app continues...