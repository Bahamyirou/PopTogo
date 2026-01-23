import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(
    page_title="Togo Prefecture Population Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🇹🇬 Togo Prefecture Population with Regional Analysis")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    gdf = gpd.read_file('population_par_prefecture.geojson')
    prefecture_data = gdf[gdf['prefecture'].notna()].dropna(subset=['Ensemble', 'Masculin', 'Feminin'])
    regional_totals = gdf[gdf['prefecture'].isna()].dropna(subset=['Region'])
    return prefecture_data, regional_totals

prefecture_data, regional_totals = load_data()

# Sidebar: Region filter
st.sidebar.header("🎛️ Regional Controls")
regions = ['All Regions'] + sorted(prefecture_data['Region'].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Select Region:", regions)

# Filter data
if selected_region == 'All Regions':
    filtered_data = prefecture_data
else:
    filtered_data = prefecture_data[prefecture_data['Region'] == selected_region]

# Regional summary in sidebar
st.sidebar.markdown("### 📊 Regional Information")

if selected_region != 'All Regions':
    # Show specific region details
    region_prefs = prefecture_data[prefecture_data['Region'] == selected_region]
    
    st.sidebar.write(f"**{selected_region}**")
    st.sidebar.write(f"🏛️ Prefectures: {len(region_prefs)}")
    st.sidebar.write(f"📊 Total: {region_prefs['Ensemble'].sum():,}")
    st.sidebar.write(f"👨 Male: {region_prefs['Masculin'].sum():,}")
    st.sidebar.write(f"👩 Female: {region_prefs['Feminin'].sum():,}")
    
    # Show official regional total if available
    official_region = regional_totals[regional_totals['Region'] == selected_region]
    if len(official_region) > 0:
        official = official_region.iloc[0]
        st.sidebar.markdown("**Official Regional Total:**")
        st.sidebar.write(f"📊 {official['Ensemble']:,.0f}")
        st.sidebar.write(f"👨 {official['Masculin']:,.0f}")
        st.sidebar.write(f"👩 {official['Feminin']:,.0f}")

# Enhanced hover tooltip with regional context
def create_enhanced_tooltip(gdf_data):
    """Create enhanced tooltip with regional context"""
    
    # Calculate regional totals for context
    regional_context = {}
    for region in gdf_data['Region'].dropna().unique():
        region_data = gdf_data[gdf_data['Region'] == region]
        regional_context[region] = {
            'total': region_data['Ensemble'].sum(),
            'count': len(region_data)
        }
    
    # Create tooltips with regional percentage
    tooltip_data = []
    for _, row in gdf_data.iterrows():
        if pd.notna(row['Region']) and row['Region'] in regional_context:
            regional_total = regional_context[row['Region']]['total']
            regional_percent = (row['Ensemble'] / regional_total * 100) if regional_total > 0 else 0
            
            tooltip_data.append({
                'prefecture': row['prefecture'],
                'region': row['Region'],
                'total': f"{row['Ensemble']:,}",
                'male': f"{row['Masculin']:,}",
                'female': f"{row['Feminin']:,}",
                'regional_percent': f"{regional_percent:.1f}%",
                'gender_ratio': f"{(row['Masculin']/row['Feminin']*100):.1f}"
            })
    
    return pd.DataFrame(tooltip_data)

# Create and display map
if len(filtered_data) > 0:
    # Calculate bounds
    bounds = filtered_data.total_bounds
    min_lon, min_lat, max_lon, max_lat = bounds
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8 if selected_region != 'All Regions' else 7,
        tiles='OpenStreetMap'
    )
    
    # Fit bounds
    padding = 0.01 if selected_region != 'All Regions' else 0.02
    m.fit_bounds([
        [min_lat - padding, min_lon - padding],
        [max_lat + padding, max_lon + padding]
    ])
    
    # Add choropleth
    folium.Choropleth(
        geo_data=filtered_data,
        data=filtered_data,
        columns=['prefecture', 'Ensemble'],
        key_on='feature.properties.prefecture',
        fill_color='YlOrRd',
        fill_opacity=0.8,
        line_opacity=1.0,
        line_color='navy',
        line_weight=2,
        legend_name='Population'
    ).add_to(m)
    
    # Enhanced tooltips with regional context
    for _, row in filtered_data.iterrows():
        if pd.notna(row['Region']):
            # Calculate prefecture's share of regional population
            region_data = prefecture_data[prefecture_data['Region'] == row['Region']]
            regional_total = region_data['Ensemble'].sum()
            regional_share = (row['Ensemble'] / regional_total * 100) if regional_total > 0 else 0
            
            gender_ratio = (row['Masculin'] / row['Feminin'] * 100) if row['Feminin'] > 0 else 0
            
            # Create custom tooltip
            tooltip_html = f"""
            <div style="font-family: Arial; padding: 10px; background: white; border: 2px solid navy; border-radius: 5px;">
                <h4 style="margin: 0; color: navy;">{row['prefecture']}</h4>
                <hr style="margin: 5px 0;">
                <p style="margin: 2px;"><b>Region:</b> {row['Region']}</p>
                <p style="margin: 2px;"><b>Total Population:</b> {row['Ensemble']:,}</p>
                <p style="margin: 2px;"><b>Male:</b> {row['Masculin']:,} ({(row['Masculin']/row['Ensemble']*100):.1f}%)</p>
                <p style="margin: 2px;"><b>Female:</b> {row['Feminin']:,} ({(row['Feminin']/row['Ensemble']*100):.1f}%)</p>
                <p style="margin: 2px;"><b>Gender Ratio:</b> {gender_ratio:.1f} M/100F</p>
                <p style="margin: 2px;"><b>% of {row['Region']}:</b> {regional_share:.1f}%</p>
            </div>
            """
            
            folium.Marker(
                location=[row.geometry.centroid.y, row.geometry.centroid.x],
                popup=folium.Popup(tooltip_html, max_width=300),
                icon=folium.Icon(color='blue', icon='info-sign', prefix='fa')
            ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=600, use_container_width=True)
    
    # Statistics
    st.markdown("### 📊 Current Selection Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Prefectures", len(filtered_data))
    with col2:
        st.metric("Total Population", f"{filtered_data['Ensemble'].sum():,}")
    with col3:
        st.metric("Male Population", f"{filtered_data['Masculin'].sum():,}")
    with col4:
        st.metric("Female Population", f"{filtered_data['Feminin'].sum():,}")

else:
    st.error("No data available to display.")