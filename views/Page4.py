import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configure the Streamlit page
st.set_page_config(
    page_title="Togo Prefecture Population Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("🇹🇬 Togo Prefecture Population Distribution")
st.markdown("---")
st.markdown("### Interactive map with regional filtering and population analysis")
st.markdown("*Filter by region and hover over prefectures for detailed breakdown*")

# Load and process data
@st.cache_data
def load_and_process_data():
    try:
        gdf = gpd.read_file('population_par_prefecture2.geojson')
        
        # Separate prefecture data from regional totals
        prefecture_data = gdf[gdf['prefecture'].notna()].copy()
        regional_totals = gdf[gdf['prefecture'].isna()].copy()
        
        # Filter valid prefecture data
        prefecture_valid = prefecture_data.dropna(subset=['Ensemble', 'Masculin', 'Feminin'])
        
        return gdf, prefecture_data, prefecture_valid, regional_totals
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

# Load data
gdf, prefecture_data, prefecture_valid, regional_totals = load_and_process_data()

if gdf is not None and len(prefecture_valid) > 0:
    
    # Sidebar controls
    st.sidebar.header("🎛️ Map Controls & Filters")
    
    # Region filter
    st.sidebar.markdown("### 🗺️ Regional Filter")
    
    # Get unique regions (excluding null)
    available_regions = prefecture_valid['Region'].dropna().unique()
    available_regions = sorted(available_regions)
    
    # Add "All Regions" option
    region_options = ['All Regions'] + list(available_regions)
    
    selected_region = st.sidebar.selectbox(
        "Select region to display:",
        region_options,
        help="Choose a specific region or view all regions"
    )
    
    # Filter data based on selection
    if selected_region == 'All Regions':
        filtered_gdf = prefecture_valid
        map_title = "All Togo Prefectures"
    else:
        filtered_gdf = prefecture_valid[prefecture_valid['Region'] == selected_region]
        map_title = f"Region: {selected_region}"
    
    # Regional summary in sidebar
    if len(regional_totals) > 0:
        st.sidebar.markdown("### 📊 Regional Totals")
        
        if selected_region != 'All Regions':
            # Show specific region data
            region_total = regional_totals[regional_totals['Region'] == selected_region]
            if len(region_total) > 0:
                rt = region_total.iloc[0]
                st.sidebar.write(f"**{selected_region}**")
                st.sidebar.write(f"📊 Total: {rt['Ensemble']:,.0f}")
                st.sidebar.write(f"👨 Male: {rt['Masculin']:,.0f}")
                st.sidebar.write(f"👩 Female: {rt['Feminin']:,.0f}")
                
                # Calculate from prefectures for comparison
                calc_total = filtered_gdf['Ensemble'].sum()
                calc_male = filtered_gdf['Masculin'].sum()
                calc_female = filtered_gdf['Feminin'].sum()
                
                st.sidebar.write(f"**Calculated from prefectures:**")
                st.sidebar.write(f"📊 Total: {calc_total:,.0f}")
                
                # Show difference if any
                diff = abs(calc_total - rt['Ensemble']) if pd.notna(rt['Ensemble']) else 0
                if diff > 0:
                    st.sidebar.warning(f"⚠️ Difference: {diff:,.0f}")
                else:
                    st.sidebar.success("✅ Data consistent!")
        else:
            # Show all regional totals
            for _, region in regional_totals.dropna(subset=['Region']).iterrows():
                with st.sidebar.expander(f"📍 {region['Region']}"):
                    st.write(f"Total: {region['Ensemble']:,.0f}")
                    st.write(f"Male: {region['Masculin']:,.0f}")
                    st.write(f"Female: {region['Feminin']:,.0f}")
                    ratio = (region['Masculin'] / region['Feminin'] * 100) if pd.notna(region['Feminin']) and region['Feminin'] > 0 else 0
                    st.write(f"Ratio: {ratio:.1f} M/100F")
    
    st.sidebar.write(f"**Showing {len(filtered_gdf)} prefectures**")
    
    # Main content
    if len(filtered_gdf) > 0:
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### 🗺️ {map_title}")
            
            # Calculate map bounds for filtered data
            bounds = filtered_gdf.total_bounds
            min_lon, min_lat, max_lon, max_lat = bounds
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2
            
            # Create map
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=8 if selected_region != 'All Regions' else 7,
                tiles='OpenStreetMap'
            )
            
            # Fit to filtered data bounds
            padding = 0.01 if selected_region != 'All Regions' else 0.02
            southwest = [min_lat - padding, min_lon - padding]
            northeast = [max_lat + padding, max_lon + padding]
            m.fit_bounds([southwest, northeast])
            
            # Add choropleth
            folium.Choropleth(
                geo_data=filtered_gdf,
                data=filtered_gdf,
                columns=['prefecture', 'Ensemble'],
                key_on='feature.properties.prefecture',
                fill_color='YlOrRd',
                fill_opacity=0.8,
                line_opacity=1.0,
                line_color='darkblue',
                line_weight=2,
                legend_name='Total Population'
            ).add_to(m)
            
            # Add interactive tooltips
            folium.GeoJson(
                filtered_gdf,
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': 'darkblue',
                    'weight': 3,
                    'fillOpacity': 0
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['prefecture', 'Region', 'Ensemble', 'Masculin', 'Feminin'],
                    aliases=['Prefecture:', 'Region:', 'Total:', 'Male:', 'Female:'],
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
                    max_width=400
                ),
                popup=folium.GeoJsonPopup(
                    fields=['prefecture', 'Region', 'Ensemble', 'Masculin', 'Feminin'],
                    aliases=['Prefecture:', 'Region:', 'Total:', 'Male:', 'Female:'],
                    localize=True,
                    labels=True,
                    style="background-color: yellow; color: black; font-weight: bold; font-size: 16px; padding: 10px;"
                )
            ).add_to(m)
            
            # Display map
            map_data = st_folium(m, width=900, height=600)
            
        with col2:
            st.markdown("### 📊 Summary Statistics")
            
            # Current selection stats
            if len(filtered_gdf) > 0:
                total_pop = filtered_gdf['Ensemble'].sum()
                male_pop = filtered_gdf['Masculin'].sum()
                female_pop = filtered_gdf['Feminin'].sum()
                
                st.metric("Prefectures Shown", len(filtered_gdf))
                st.metric("Total Population", f"{total_pop:,}")
                st.metric("Male Population", f"{male_pop:,}")
                st.metric("Female Population", f"{female_pop:,}")
                
                gender_ratio = (male_pop / female_pop * 100) if female_pop > 0 else 0
                st.metric("Gender Ratio", f"{gender_ratio:.1f} M/100F")
                
                # Regional comparison if specific region selected
                if selected_region != 'All Regions' and len(regional_totals) > 0:
                    st.markdown("---")
                    st.markdown("#### 📋 Regional Validation")
                    
                    region_official = regional_totals[regional_totals['Region'] == selected_region]
                    if len(region_official) > 0:
                        official = region_official.iloc[0]
                        
                        st.write("**Official Regional Total:**")
                        st.write(f"📊 {official['Ensemble']:,.0f}")
                        
                        st.write("**Sum of Prefectures:**")
                        st.write(f"📊 {total_pop:,.0f}")
                        
                        diff = abs(total_pop - official['Ensemble']) if pd.notna(official['Ensemble']) else 0
                        if diff == 0:
                            st.success("✅ Data consistent!")
                        else:
                            st.warning(f"⚠️ Difference: {diff:,.0f}")
        
        # Calculate regional statistics from prefecture data
        regional_calc = prefecture_valid.groupby('Region').agg({
            'Ensemble': 'sum',
            'Masculin': 'sum',
            'Feminin': 'sum',
            'prefecture': 'count'
        }).reset_index()
        
        regional_calc['Gender_Ratio'] = (regional_calc['Masculin'] / regional_calc['Feminin'] * 100).round(1)
        
        # Regional Analysis Section - Following the provided pattern
        st.markdown("---")
        st.markdown("## 📊 Regional Statistics")
        
        # 5-column metrics layout
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Regions", len(regional_calc))
        
        with col2:
            st.metric("Total Population", f"{regional_calc['Ensemble'].sum():,}")
        
        with col3:
            st.metric("Total Male", f"{regional_calc['Masculin'].sum():,}")
        
        with col4:
            st.metric("Total Female", f"{regional_calc['Feminin'].sum():,}")
        
        with col5:
            # Calculate overall gender ratio
            total_male = regional_calc['Masculin'].sum()
            total_female = regional_calc['Feminin'].sum()
            overall_ratio = (total_male / total_female * 100) if total_female > 0 else 0
            st.metric("Male/Female Ratio", f"{overall_ratio:.1f}%")
        
        st.markdown("---")
        
        # Create two columns for visualizations
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.markdown("### 🏆 Regions by Total Population")
            # Sort regions by population
            top_regions = regional_calc.sort_values('Ensemble', ascending=False)[['Region', 'Ensemble', 'Masculin', 'Feminin']].copy()
            top_regions.columns = ['Region', 'Total Population', 'Male', 'Female']
            top_regions.index = range(1, len(top_regions) + 1)
            
            # Format numbers for display
            display_regions = top_regions.copy()
            display_regions['Total Population'] = display_regions['Total Population'].apply(lambda x: f"{x:,}")
            display_regions['Male'] = display_regions['Male'].apply(lambda x: f"{x:,}")
            display_regions['Female'] = display_regions['Female'].apply(lambda x: f"{x:,}")
            
            st.dataframe(display_regions, use_container_width=True)
        
        with viz_col2:
            st.markdown("### 👥 Overall Gender Distribution")
            # Pie chart for overall gender distribution
            gender_data = pd.DataFrame({
                'Gender': ['Male', 'Female'],
                'Count': [regional_calc['Masculin'].sum(), regional_calc['Feminin'].sum()]
            })
            
            fig_pie = px.pie(
                gender_data, 
                values='Count', 
                names='Gender',
                color='Gender',
                color_discrete_map={'Male': '#4A90E2', 'Female': '#E94B3C'},
                hole=0.4
            )
            fig_pie.update_layout(height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Bar chart for regions by gender
        st.markdown("### 📊 Regional Population by Gender")
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name='Male',
            x=regional_calc['Region'],
            y=regional_calc['Masculin'],
            marker_color='#4A90E2'
        ))
        fig_bar.add_trace(go.Bar(
            name='Female',
            x=regional_calc['Region'],
            y=regional_calc['Feminin'],
            marker_color='#E94B3C'
        ))
        
        fig_bar.update_layout(
            barmode='group',
            xaxis_tickangle=-45,
            height=500,
            xaxis_title="Region",
            yaxis_title="Population"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Complete regional statistics table
        st.markdown("### 📋 Complete Regional Statistics")
        
        # Create a comprehensive regional table
        regional_stats = regional_calc.copy()
        regional_stats['% Male'] = (regional_stats['Masculin'] / regional_stats['Ensemble'] * 100).round(2)
        regional_stats['% Female'] = (regional_stats['Feminin'] / regional_stats['Ensemble'] * 100).round(2)
        
        # Rename columns for display
        regional_stats_display = regional_stats[['Region', 'prefecture', 'Ensemble', 'Masculin', 'Feminin', '% Male', '% Female', 'Gender_Ratio']].copy()
        regional_stats_display.columns = ['Region', 'Prefectures', 'Total Population', 'Male', 'Female', '% Male', '% Female', 'M/F Ratio']
        
        # Sort by total population
        regional_stats_display = regional_stats_display.sort_values('Total Population', ascending=False).reset_index(drop=True)
        regional_stats_display.index = range(1, len(regional_stats_display) + 1)
        
        st.dataframe(regional_stats_display, use_container_width=True, height=400)
        
        # Download button for regional data
        regional_csv = regional_stats_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Regional Statistics as CSV",
            data=regional_csv,
            file_name="togo_regional_population_statistics.csv",
            mime="text/csv",
        )
        
        # Prefecture details for selected region
        st.markdown("---")
        st.markdown(f"### 🏛️ Prefecture Details - {map_title}")
        
        if len(filtered_gdf) > 0:
            # Create detailed prefecture table
            prefecture_details = filtered_gdf.copy()
            prefecture_details['Gender_Ratio'] = (prefecture_details['Masculin'] / prefecture_details['Feminin'] * 100).round(1)
            prefecture_details['Male_Percent'] = (prefecture_details['Masculin'] / prefecture_details['Ensemble'] * 100).round(1)
            prefecture_details['Female_Percent'] = (prefecture_details['Feminin'] / prefecture_details['Ensemble'] * 100).round(1)
            
            # Sort by population
            prefecture_details = prefecture_details.sort_values('Ensemble', ascending=False)
            prefecture_details['Rank'] = range(1, len(prefecture_details) + 1)
            
            # Format for display
            prefecture_display = prefecture_details[['Rank', 'prefecture', 'Region', 'Ensemble', 'Masculin', 'Feminin', 'Gender_Ratio']].copy()
            prefecture_display['Total'] = prefecture_display['Ensemble'].apply(lambda x: f"{x:,}")
            prefecture_display['Male'] = prefecture_display['Masculin'].apply(lambda x: f"{x:,}")
            prefecture_display['Female'] = prefecture_display['Feminin'].apply(lambda x: f"{x:,}")
            
            final_display = prefecture_display[['Rank', 'prefecture', 'Region', 'Total', 'Male', 'Female', 'Gender_Ratio']]
            final_display.columns = ['Rank', 'Prefecture', 'Region', 'Total Pop', 'Male', 'Female', 'M/F Ratio']
            
            st.dataframe(final_display, use_container_width=True, height=300)
            
            # Summary stats for current selection
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Prefectures", len(filtered_gdf))
            with col2:
                st.metric("Total Population", f"{filtered_gdf['Ensemble'].sum():,}")
            with col3:
                avg_pop = filtered_gdf['Ensemble'].mean()
                st.metric("Average Population", f"{avg_pop:,.0f}")
            with col4:
                highest_pop = filtered_gdf['Ensemble'].max()
                highest_name = filtered_gdf.loc[filtered_gdf['Ensemble'].idxmax(), 'prefecture']
                st.metric("Highest", f"{highest_pop:,}", f"{highest_name}")
        
        else:
            st.warning("⚠️ No prefectures found for the selected region.")
        
        # Download section
        st.markdown("---")
        st.markdown("### 📥 Data Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export filtered prefecture data
            filtered_csv = filtered_gdf[['prefecture', 'Region', 'Ensemble', 'Masculin', 'Feminin']].copy()
            filtered_csv['Gender_Ratio'] = (filtered_csv['Masculin'] / filtered_csv['Feminin'] * 100).round(2)
            
            st.download_button(
                label="📄 Download Filtered Data",
                data=filtered_csv.to_csv(index=False),
                file_name=f"togo_prefecture_{selected_region.lower().replace(' ', '_')}_population.csv",
                mime="text/csv"
            )
        
        with col2:
            # Export regional summary
            regional_csv = regional_calc.copy()
            
            st.download_button(
                label="📊 Download Regional Summary",
                data=regional_csv.to_csv(index=False),
                file_name="togo_regional_population_summary.csv",
                mime="text/csv"
            )
        
    
    else:
        st.error("No valid prefecture data found.")

else:
    st.error("Failed to load data. Please check the file path and format.")

# Footer
st.markdown("---")
st.markdown("*🇹🇬 Advanced demographic analysis with regional filtering and data validation*")
st.markdown("*📊 FAIR data principles implementation for Togo's administrative divisions*")
