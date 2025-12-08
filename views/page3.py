import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import pandas as pd

# Configure the Streamlit page
st.set_page_config(
    page_title="Togo Prefecture Explorer",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title
st.title("🏛️ Togo Prefecture Explorer")
st.markdown("### Filter and explore individual prefectures")

# Load data
@st.cache_data
def load_data():
    try:
        gdf = gpd.read_file('prefectures_with_population.geojson')
        return gdf
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

gdf = load_data()

if gdf is not None:
    # Sidebar filters
    st.sidebar.header("🎯 Prefecture Filters")
    
    # Get list of prefectures
    prefecture_list = sorted(gdf['prefecture'].unique())
    
    # Filter options
    filter_option = st.sidebar.radio(
        "Select filter mode:",
        ["Single Prefecture", "Multiple Prefectures", "Population Range", "All Prefectures"]
    )
    
    # Apply filters based on selection
    if filter_option == "Single Prefecture":
        selected_prefecture = st.sidebar.selectbox(
            "Choose a prefecture:",
            prefecture_list,
            help="Select one prefecture to view in detail"
        )
        filtered_gdf = gdf[gdf['prefecture'] == selected_prefecture]
        map_title = f"Prefecture: {selected_prefecture}"
        
    elif filter_option == "Multiple Prefectures":
        selected_prefectures = st.sidebar.multiselect(
            "Choose prefectures:",
            prefecture_list,
            default=prefecture_list[:3],
            help="Select multiple prefectures to compare"
        )
        filtered_gdf = gdf[gdf['prefecture'].isin(selected_prefectures)]
        map_title = f"Selected Prefectures ({len(selected_prefectures)})"
        
    elif filter_option == "Population Range":
        min_pop = int(gdf['PopCount'].min())
        max_pop = int(gdf['PopCount'].max())
        
        pop_range = st.sidebar.slider(
            "Population range:",
            min_value=min_pop,
            max_value=max_pop,
            value=(min_pop, max_pop),
            step=100,
            help="Filter prefectures by population count"
        )
        
        filtered_gdf = gdf[
            (gdf['PopCount'] >= pop_range[0]) & 
            (gdf['PopCount'] <= pop_range[1])
        ]
        map_title = f"Prefectures with {pop_range[0]:,} - {pop_range[1]:,} population"
        
    else:  # All Prefectures
        filtered_gdf = gdf
        map_title = "All Togo Prefectures"
    
    # Additional sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Filter Results")
    st.sidebar.write(f"**Prefectures shown:** {len(filtered_gdf)}")
    if len(filtered_gdf) > 0:
        st.sidebar.write(f"**Total population:** {filtered_gdf['PopCount'].sum():,}")
        st.sidebar.write(f"**Average population:** {filtered_gdf['PopCount'].mean():,.0f}")
    
    # Main content
    if len(filtered_gdf) > 0:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### 🗺️ {map_title}")
            
            # Calculate bounds for filtered data
            bounds = filtered_gdf.total_bounds
            min_lon, min_lat, max_lon, max_lat = bounds
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2
            
            # Calculate zoom based on area
            lat_diff = max_lat - min_lat
            lon_diff = max_lon - min_lon
            max_diff = max(lat_diff, lon_diff)
            
            if max_diff > 2:
                zoom_level = 7
            elif max_diff > 1:
                zoom_level = 8
            elif max_diff > 0.5:
                zoom_level = 9
            elif max_diff > 0.2:
                zoom_level = 10
            else:
                zoom_level = 11
            
            # Create map
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=zoom_level,
                tiles='OpenStreetMap'
            )
            
            # Fit to filtered bounds
            padding = 0.01
            southwest = [min_lat - padding, min_lon - padding]
            northeast = [max_lat + padding, max_lon + padding]
            m.fit_bounds([southwest, northeast])
            
            # Add choropleth for filtered data
            folium.Choropleth(
                geo_data=filtered_gdf,
                data=filtered_gdf,
                columns=['prefecture', 'PopCount'],
                key_on='feature.properties.prefecture',
                fill_color='YlOrRd',
                fill_opacity=0.8,
                line_opacity=1.0,
                line_color='darkblue',
                line_weight=3,
                legend_name='Population Count'
            ).add_to(m)
            
            # Add interactive tooltips and popups
            folium.GeoJson(
                filtered_gdf,
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': 'darkblue',
                    'weight': 3,
                    'fillOpacity': 0
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['prefecture', 'PopCount'],
                    aliases=['Prefecture:', 'Population:'],
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: #f0f0f0;
                        border: 3px solid darkblue;
                        border-radius: 8px;
                        font-family: Arial, sans-serif;
                        font-size: 16px;
                        font-weight: bold;
                        color: #333;
                        padding: 12px;
                    """,
                    max_width=350
                ),
                popup=folium.GeoJsonPopup(
                    fields=['prefecture', 'PopCount'],
                    aliases=['Prefecture:', 'Population:'],
                    localize=True,
                    labels=True,
                    style="background-color: yellow; color: black; font-weight: bold; font-size: 14px;"
                )
            ).add_to(m)
            
            # Display map
            map_data = st_folium(m, width=800, height=600)
            
        with col2:
            st.markdown("### 📈 Prefecture Details")
            
            # Display details for filtered prefectures
            if len(filtered_gdf) == 1:
                # Single prefecture detailed view
                pref_row = filtered_gdf.iloc[0]
                
                st.metric("**Name**", pref_row['prefecture'])
                st.metric("**Population**", f"{pref_row['PopCount']:,}")
                
                # Calculate rank
                rank = (gdf['PopCount'] > pref_row['PopCount']).sum() + 1
                st.metric("**Population Rank**", f"{rank} of {len(gdf)}")
                
                # Calculate percentile
                percentile = ((gdf['PopCount'] <= pref_row['PopCount']).sum() / len(gdf)) * 100
                st.metric("**Population Percentile**", f"{percentile:.1f}%")
                
                # Comparison with average
                avg_pop = gdf['PopCount'].mean()
                diff_from_avg = pref_row['PopCount'] - avg_pop
                st.metric(
                    "**Difference from Average**", 
                    f"{diff_from_avg:+,.0f}",
                    help=f"Average population: {avg_pop:,.0f}"
                )
                
                # Calculate bounds info
                bounds = pref_row.geometry.bounds
                area = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
                st.metric("**Geographic Area**", f"{area:.4f} degrees²")
                
            else:
                # Multiple prefectures summary
                st.write("**Summary Statistics:**")
                st.write(f"• Total prefectures: {len(filtered_gdf)}")
                st.write(f"• Total population: {filtered_gdf['PopCount'].sum():,}")
                st.write(f"• Average population: {filtered_gdf['PopCount'].mean():,.0f}")
                st.write(f"• Highest: {filtered_gdf['PopCount'].max():,}")
                st.write(f"• Lowest: {filtered_gdf['PopCount'].min():,}")
                
                # Show list of selected prefectures
                st.markdown("**Selected Prefectures:**")
                prefecture_summary = filtered_gdf[['prefecture', 'PopCount']].sort_values('PopCount', ascending=False)
                prefecture_summary.index = range(1, len(prefecture_summary) + 1)
                prefecture_summary['PopCount'] = prefecture_summary['PopCount'].apply(lambda x: f"{x:,}")
                st.dataframe(prefecture_summary, use_container_width=True)
        
        # Full width section below
        st.markdown("---")
        st.markdown("### 📊 Detailed Data Table")
        
        # Create detailed table
        display_df = filtered_gdf[['prefecture', 'PopCount']].copy()
        display_df['Population Rank'] = display_df['PopCount'].rank(method='dense', ascending=False).astype(int)
        display_df['% of Total Population'] = (display_df['PopCount'] / gdf['PopCount'].sum() * 100).round(2)
        display_df = display_df.sort_values('PopCount', ascending=False)
        display_df.index = range(1, len(display_df) + 1)
        
        # Format population with commas
        display_df['PopCount'] = display_df['PopCount'].apply(lambda x: f"{x:,}")
        
        # Rename columns for display
        display_df.columns = ['Prefecture Name', 'Population', 'Rank', '% of Total']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name=f"togo_prefectures_filtered.csv",
            mime="text/csv"
        )
        
    else:
        st.warning("⚠️ No prefectures match your filter criteria. Please adjust your selection.")
        
    # Comparison section
    if len(filtered_gdf) > 1:
        st.markdown("---")
        st.markdown("### 🔍 Prefecture Comparison")
        
        # Quick comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Population Distribution**")
            chart_data = filtered_gdf[['prefecture', 'PopCount']].sort_values('PopCount', ascending=True)
            st.bar_chart(chart_data.set_index('prefecture')['PopCount'])
            
        with col2:
            st.markdown("**Population Statistics**")
            stats_data = {
                'Metric': ['Count', 'Total', 'Average', 'Median', 'Std Dev'],
                'Value': [
                    len(filtered_gdf),
                    f"{filtered_gdf['PopCount'].sum():,}",
                    f"{filtered_gdf['PopCount'].mean():,.0f}",
                    f"{filtered_gdf['PopCount'].median():,.0f}",
                    f"{filtered_gdf['PopCount'].std():,.0f}"
                ]
            }
            st.table(pd.DataFrame(stats_data))

else:
    st.error("Failed to load prefecture data. Please check the file path.")

# Footer
st.markdown("---")
st.markdown("*🇹🇬 Prefecture Explorer - Detailed view of Togo's administrative divisions*")