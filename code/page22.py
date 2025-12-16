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

# Title and description
st.title("🗺️ Togolese Resident Population by sexe")
st.markdown("Interactive map showing population distribution across Togo's prefectures")

# Load GeoJSON data using GeoPandas
@st.cache_data
def load_geojson_data():
    """Load GeoJSON file and return both GeoDataFrame and raw GeoJSON"""
    try:
        # Read the GeoJSON file
        gdf = gpd.read_file('population_par_prefecture.geojson')
        
        # Convert to regular GeoJSON format for Folium
        geojson_data = json.loads(gdf.to_json())
        
        return gdf, geojson_data
    except FileNotFoundError:
        st.error("❌ Could not find 'population_par_prefecture.geojson' file in the current directory!")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading GeoJSON file: {str(e)}")
        st.stop()

# Process data for analysis
@st.cache_data
def process_data():
    """Process the geodata for analysis and visualization"""
    gdf, geojson_data = load_geojson_data()
    
    # Filter out entries with null population data
    valid_gdf = gdf[
        (gdf['Ensemble'].notna()) & 
        (~gdf['prefecture'].isin(["LOME COMMUNE", "PLAINE DU MO"]))
    ].copy()
    
    # Clean up the data
    valid_gdf['Region'] = valid_gdf['Region'].fillna('Unknown')
    
    return valid_gdf, geojson_data

# Load and process data
try:
    gdf, geojson_data = process_data()
except Exception as e:
    st.error(f"Error processing data: {str(e)}")
    st.stop()

# Sidebar controls
st.sidebar.header("🎛️ Map Controls")

# Population type selection
population_type = st.sidebar.selectbox(
    "Select Population Type",
    ["Ensemble", "Masculin", "Feminin"],
    format_func=lambda x: {
        "Ensemble": "Total Population",
        "Masculin": "Male Population", 
        "Feminin": "Female Population"
    }[x]
)

# Color scheme selection
color_scheme = st.sidebar.selectbox(
    "Select Color Scheme",
    ["YlOrRd", "Blues", "Greens", "Reds", "Purples", "Oranges", "viridis"]
)

# Prefecture filter
st.sidebar.header("🏘️ Prefecture Filter")

# Option to filter by specific prefectures
filter_option = st.sidebar.radio(
    "Filter Option:",
    ["Show All Prefectures", "Select Specific Prefectures", "Filter by Region"]
)

filtered_gdf = gdf.copy()

if filter_option == "Select Specific Prefectures":
    # Multi-select for prefectures
    selected_prefectures = st.sidebar.multiselect(
        "Select Prefectures:",
        options=sorted(gdf['prefecture'].tolist()),
        default=[]
    )
    
    if selected_prefectures:
        filtered_gdf = gdf[gdf['prefecture'].isin(selected_prefectures)].copy()
    else:
        st.sidebar.warning("⚠️ No prefectures selected. Showing all.")

elif filter_option == "Filter by Region":
    # Region filter as secondary option
    regions = ["All Regions"] + sorted(gdf['Region'].unique().tolist())
    selected_region = st.sidebar.selectbox("Select Region:", regions)
    
    if selected_region != "All Regions":
        filtered_gdf = gdf[gdf['Region'] == selected_region].copy()
        
        # Show prefectures in selected region
        st.sidebar.write(f"**Prefectures in {selected_region}:**")
        region_prefectures = sorted(filtered_gdf['prefecture'].tolist())
        for i, pref in enumerate(region_prefectures, 1):
            st.sidebar.write(f"{i}. {pref}")

# Quick preset filters
st.sidebar.header("⚡ Quick Filters")
col_a, col_b = st.sidebar.columns(2)

with col_a:
    if st.button("🏆 Top 5", help="Show top 5 prefectures by population"):
        top_5_prefectures = gdf.nlargest(5, 'Ensemble')['prefecture'].tolist()
        filtered_gdf = gdf[gdf['prefecture'].isin(top_5_prefectures)].copy()

with col_b:
    if st.button("🎯 Random 5", help="Show 5 random prefectures"):
        random_5 = gdf.sample(5)['prefecture'].tolist()
        filtered_gdf = gdf[gdf['prefecture'].isin(random_5)].copy()

# Display statistics for filtered data
st.sidebar.header("📊 Statistics")
if not filtered_gdf.empty:
    total_pop = filtered_gdf['Ensemble'].sum()
    male_pop = filtered_gdf['Masculin'].sum()
    female_pop = filtered_gdf['Feminin'].sum()
    
    st.sidebar.metric("Filtered Total Population", f"{total_pop:,}")
    st.sidebar.metric("Filtered Male Population", f"{male_pop:,}")
    st.sidebar.metric("Filtered Female Population", f"{female_pop:,}")
    st.sidebar.metric("Male/Female Ratio", f"{male_pop/female_pop:.2f}" if female_pop > 0 else "N/A")
    st.sidebar.metric("Showing Prefectures", f"{len(filtered_gdf)} of {len(gdf)}")

# Create the map
def create_map():
    """Create the folium map with choropleth visualization"""
    # Center the map on Togo
    togo_center = [8.0, 1.0]
    
    # Create base map
    m = folium.Map(
        location=togo_center,
        zoom_start=7,
        tiles="OpenStreetMap"
    )
    
    # Alternative tile layers
    folium.TileLayer("CartoDB Positron", name="Light Mode").add_to(m)
    folium.TileLayer("CartoDB Dark_Matter", name="Dark Mode").add_to(m)
    
    # Convert all GDF to GeoJSON for background
    all_geojson = json.loads(gdf.to_json())
    
    # Add background layer (all prefectures in light gray)
    folium.GeoJson(
        all_geojson,
        style_function=lambda feature: {
            'fillColor': '#f0f0f0',
            'color': '#cccccc',
            'weight': 1,
            'fillOpacity': 0.3,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['prefecture', 'Region'],
            aliases=['Prefecture:', 'Region:'],
            localize=True
        )
    ).add_to(m)
    
    # Convert filtered GDF to GeoJSON for highlighted layer
    if not filtered_gdf.empty:
        filtered_geojson = json.loads(filtered_gdf.to_json())
        
        # Create choropleth layer for selected prefectures
        folium.Choropleth(
            geo_data=filtered_geojson,
            name=f"Selected Prefectures - {population_type}",
            data=filtered_gdf,
            columns=['prefecture', population_type],
            key_on='feature.properties.prefecture',
            fill_color=color_scheme,
            fill_opacity=0.8,
            line_opacity=0.8,
            line_weight=2,
            legend_name=f'{population_type} Population (Selected)',
            highlight=True
        ).add_to(m)
        
        # Add detailed tooltips for selected prefectures
        folium.GeoJson(
            filtered_geojson,
            style_function=lambda feature: {
                'fillColor': 'transparent',
                'color': '#000000',
                'weight': 3,
                'fillOpacity': 0,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['prefecture', 'Region', 'Masculin', 'Feminin', 'Ensemble'],
                aliases=['Prefecture:', 'Region:', 'Male:', 'Female:', 'Total:'],
                localize=True,
                sticky=False,
                labels=True,
                style="""
                    background-color: white;
                    border: 2px solid black;
                    border-radius: 5px;
                    box-shadow: 3px;
                    font-size: 14px;
                    padding: 10px;
                """,
                max_width=500,
            ),
            popup=folium.GeoJsonPopup(
                fields=['prefecture', 'Region', 'Masculin', 'Feminin', 'Ensemble'],
                aliases=['Prefecture:', 'Region:', 'Male:', 'Female:', 'Total:'],
                localize=True,
                labels=True,
                max_width=400,
            ),
            highlight_function=lambda x: {
                'weight': 4,
                'fillOpacity': 0.9
            }
        ).add_to(m)
        
        # Auto-fit map bounds to selected prefectures
        if len(filtered_gdf) < len(gdf):
            bounds = filtered_gdf.total_bounds
            m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

# Main layout
col1, col2 = st.columns([3, 1])

with col1:
    if len(filtered_gdf) < len(gdf):
        st.subheader(f"📍 Map: {population_type} - {len(filtered_gdf)} Selected Prefecture(s)")
        st.info(f"Showing {len(filtered_gdf)} of {len(gdf)} prefectures")
    else:
        st.subheader(f"📍 Map: {population_type} - All Prefectures")
    
    # Create and display the map
    if not gdf.empty:
        map_obj = create_map()
        
        # Display the map
        map_data = st_folium(
            map_obj, 
            width=800, 
            height=600,
            key="togo_map"
        )
    else:
        st.warning("No data available.")

with col2:
    st.subheader("🔍 Selected Prefecture(s)")
    
    if not filtered_gdf.empty:
        # Show details for filtered prefectures
        for idx, row in filtered_gdf.iterrows():
            with st.expander(f"📍 {row['prefecture']}"):
                st.write(f"**Region:** {row['Region']}")
                st.write(f"**Total Population:** {row['Ensemble']:,}")
                st.write(f"**Male:** {row['Masculin']:,}")
                st.write(f"**Female:** {row['Feminin']:,}")
                
                # Calculate percentages
                if row['Ensemble'] > 0:
                    male_pct = (row['Masculin'] / row['Ensemble']) * 100
                    female_pct = (row['Feminin'] / row['Ensemble']) * 100
                    st.write(f"**Male %:** {male_pct:.1f}%")
                    st.write(f"**Female %:** {female_pct:.1f}%")
                    
                    # Population rank
                    rank = gdf.sort_values('Ensemble', ascending=False).reset_index(drop=True)
                    prefecture_rank = rank[rank['prefecture'] == row['prefecture']].index[0] + 1
                    st.write(f"**National Rank:** #{prefecture_rank}")
    else:
        st.info("👆 Select prefectures to see details")

# Prefecture search
st.subheader("🔍 Prefecture Search")
search_term = st.text_input("Search prefecture by name:", placeholder="Type prefecture name...")

if search_term:
    search_results = gdf[gdf['prefecture'].str.contains(search_term, case=False, na=False)]
    if not search_results.empty:
        st.success(f"Found {len(search_results)} prefecture(s):")
        for idx, row in search_results.iterrows():
            col_x, col_y, col_z = st.columns([2, 1, 1])
            with col_x:
                st.write(f"**{row['prefecture']}** ({row['Region']})")
            with col_y:
                st.write(f"Pop: {row['Ensemble']:,}")
            with col_z:
                if st.button(f"Focus", key=f"focus_{idx}"):
                    filtered_gdf = gdf[gdf['prefecture'] == row['prefecture']].copy()
                    st.rerun()
    else:
        st.warning(f"No prefectures found matching '{search_term}'")

# Population ranking table
st.subheader("📈 Prefecture Data")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 Selected Data", "🏪 All Prefectures", "📉 Comparisons"])

with tab1:
    # Show filtered/selected data
    if not filtered_gdf.empty:
        ranking_df = filtered_gdf.copy()
        ranking_df = ranking_df.sort_values(population_type, ascending=False).reset_index(drop=True)
        
        # Add rank column
        ranking_df.index += 1
        
        # Select columns for display
        display_cols = ['prefecture', 'Region', 'Masculin', 'Feminin', 'Ensemble']
        display_df = ranking_df[display_cols].copy()
        
        # Format population numbers
        for col in ['Masculin', 'Feminin', 'Ensemble']:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")
        
        # Rename columns
        display_df.columns = ['Prefecture', 'Region', 'Male', 'Female', 'Total']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Summary of selected data
        if len(filtered_gdf) > 1:
            st.write("**Summary of Selected Prefectures:**")
            col_x, col_y, col_z, col_w = st.columns(4)
            with col_x:
                st.metric("Count", len(filtered_gdf))
            with col_y:
                st.metric("Total Pop", f"{filtered_gdf['Ensemble'].sum():,}")
            with col_z:
                st.metric("Avg Pop", f"{filtered_gdf['Ensemble'].mean():,.0f}")
            with col_w:
                st.metric("Max Pop", f"{filtered_gdf['Ensemble'].max():,}")
    else:
        st.info("No prefectures selected. Use the sidebar controls to select prefectures.")

with tab2:
    # All prefectures ranking
    if not gdf.empty:
        all_ranking = gdf.copy()
        all_ranking = all_ranking.sort_values(population_type, ascending=False).reset_index(drop=True)
        all_ranking.index += 1
        
        # Select columns for display
        display_cols = ['prefecture', 'Region', 'Masculin', 'Feminin', 'Ensemble']
        all_display_df = all_ranking[display_cols].copy()
        
        # Format population numbers
        for col in ['Masculin', 'Feminin', 'Ensemble']:
            all_display_df[col] = all_display_df[col].apply(lambda x: f"{x:,.0f}")
        
        # Rename columns
        all_display_df.columns = ['Prefecture', 'Region', 'Male', 'Female', 'Total']
        
        st.dataframe(
            all_display_df,
            use_container_width=True,
            height=400
        )

with tab3:
    # Comparison tools
    st.write("**Compare Prefectures:**")
    
    # Select prefectures for comparison
    compare_prefectures = st.multiselect(
        "Select up to 5 prefectures to compare:",
        options=sorted(gdf['prefecture'].tolist()),
        max_selections=5
    )
    
    if compare_prefectures:
        compare_df = gdf[gdf['prefecture'].isin(compare_prefectures)].copy()
        compare_df = compare_df.sort_values('Ensemble', ascending=False)
        
        # Create comparison chart
        chart_data = compare_df.set_index('prefecture')[['Masculin', 'Feminin', 'Ensemble']]
        st.bar_chart(chart_data, height=300)
        
        # Comparison table
        comp_display = compare_df[['prefecture', 'Region', 'Masculin', 'Feminin', 'Ensemble']].copy()
        for col in ['Masculin', 'Feminin', 'Ensemble']:
            comp_display[col] = comp_display[col].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(comp_display, use_container_width=True)

# Prefecture analysis section
st.subheader("📊 Prefecture Analysis")

col1, col2 = st.columns(2)

with col1:
    # Top 10 prefectures by total population
    if not gdf.empty:
        st.write("**Top 10 Prefectures by Total Population:**")
        top_10 = gdf.nlargest(10, 'Ensemble')[['prefecture', 'Ensemble']]
        
        # Create a simple bar chart
        chart_data = top_10.set_index('prefecture')['Ensemble']
        st.bar_chart(chart_data, height=300)

with col2:
    # Regional distribution
    if not gdf.empty:
        st.write("**Population by Region:**")
        region_totals = gdf.groupby('Region')['Ensemble'].sum().sort_values(ascending=False)
        
        for region, pop in region_totals.items():
            percentage = (pop / region_totals.sum()) * 100
            prefecture_count = len(gdf[gdf['Region'] == region])
            st.write(f"• **{region}**: {pop:,} ({percentage:.1f}%) - {prefecture_count} prefectures")

# Prefecture finder
st.subheader("🔍 Prefecture Finder")

# Create columns for different search methods
search_col1, search_col2, search_col3 = st.columns(3)

with search_col1:
    st.write("**🏆 By Population Size:**")
    pop_threshold = st.number_input(
        "Min Population:", 
        min_value=0, 
        max_value=int(gdf['Ensemble'].max()), 
        value=100000,
        step=10000
    )
    
    large_prefectures = gdf[gdf['Ensemble'] >= pop_threshold]['prefecture'].tolist()
    if st.button(f"Show {len(large_prefectures)} Large Prefectures"):
        filtered_gdf = gdf[gdf['prefecture'].isin(large_prefectures)].copy()
        st.rerun()

with search_col2:
    st.write("**🏘️ By Region:**")
    region_for_filter = st.selectbox(
        "Choose Region:",
        options=[""] + sorted(gdf['Region'].unique().tolist()),
        key="region_finder"
    )
    
    if region_for_filter and st.button("Show Region Prefectures"):
        filtered_gdf = gdf[gdf['Region'] == region_for_filter].copy()
        st.rerun()

with search_col3:
    st.write("**⚖️ By Gender Ratio:**")
    ratio_option = st.selectbox(
        "Gender Majority:",
        ["More Males", "More Females", "Balanced (±2%)"]
    )
    
    if st.button("Filter by Gender Ratio"):
        if ratio_option == "More Males":
            condition = gdf['Masculin'] > gdf['Feminin']
        elif ratio_option == "More Females":
            condition = gdf['Masculin'] < gdf['Feminin']
        else:  # Balanced
            ratio = abs(gdf['Masculin'] - gdf['Feminin']) / gdf['Ensemble']
            condition = ratio <= 0.02
        
        filtered_gdf = gdf[condition].copy()
        st.rerun()

# App information
st.sidebar.header("ℹ️ About")
st.sidebar.info(
    f"""
    **Togo Population Visualization**
    
    🗺️ **Features:**
    - Interactive choropleth map
    - Prefecture-level filtering
    - Population analysis tools
    - Comparison capabilities
    
    📊 **Current Data:**
    - {len(gdf)} prefectures
    - {gdf['Region'].nunique()} regions
    - {gdf['Ensemble'].sum():,} total population
    """
)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <small>
    📊 Togo Population Visualization | 
    Data Source: population_par_prefecture.geojson | 
    Built with Streamlit, Folium & GeoPandas
    </small>
    </div>
    """, 
    unsafe_allow_html=True
)