import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium
<<<<<<< HEAD
import pandas as pd

=======
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Configure the Streamlit page
>>>>>>> 45baab05b73844ad4071b8ab5b464bacf9a1cfe6
st.set_page_config(
    page_title="Togo Prefecture Population Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

<<<<<<< HEAD
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
=======
# App title and description
st.title("🗺️ Togo Prefecture & Region Population Distribution")
st.markdown("---")

# Create a container for the map
with st.container():
    try:
        # Load the geojson with population data
        gdf = gpd.read_file('population_par_prefecture.geojson')
        
        # Column names
        prefecture_col = 'prefecture'
        region_col = 'Region'
        total_col = 'Ensemble'
        male_col = 'Masculin'
        female_col = 'Feminin'
        
        # Filter out rows with null values in key columns
        gdf_clean = gdf[gdf[total_col].notna() & gdf[region_col].notna()].copy()
        
        # SIDEBAR CONTROLS
        st.sidebar.title("🎛️ Map Controls")
        
        # View mode selector
        view_mode = st.sidebar.radio(
            "Select View Mode:",
            ["By Prefecture (Population)", "By Region (Colored)", "By Prefecture (Filtered by Region)"]
        )
        
        # Region filter (only for filtered view)
        selected_region = None
        if view_mode == "By Prefecture (Filtered by Region)":
            regions = sorted(gdf_clean[region_col].unique())
            selected_region = st.sidebar.selectbox(
                "Select Region to Display:",
                ["All Regions"] + regions
            )
        
        # Color scheme for regions
        region_colors = {
            'DISTRICT AUTONOME DU GRAND LOME (DAGL)': '#FF6B6B',
            'MARITIME SANS GRAND LOME': '#4ECDC4',
            'PLATEAUX': '#45B7D1',
            'CENTRALE': '#FFA07A',
            'KARA': '#98D8C8',
            'SAVANES': '#F7DC6F'
        }
        
        # Filter data based on selection
        if selected_region and selected_region != "All Regions":
            gdf_display = gdf_clean[gdf_clean[region_col] == selected_region].copy()
        else:
            gdf_display = gdf_clean.copy()
        
        # Calculate map center
        center_lat = gdf_display.geometry.centroid.y.mean()
        center_lon = gdf_display.geometry.centroid.x.mean()
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon], 
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Add different visualizations based on view mode
        if view_mode == "By Region (Colored)":
            # Add colored regions
            for region in gdf_clean[region_col].unique():
                region_data = gdf_clean[gdf_clean[region_col] == region]
                color = region_colors.get(region, '#CCCCCC')
                
                folium.GeoJson(
                    region_data,
                    style_function=lambda x, color=color: {
                        'fillColor': color,
                        'color': 'black',
                        'weight': 2,
                        'fillOpacity': 0.6
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=[prefecture_col, region_col, total_col, male_col, female_col],
                        aliases=['Prefecture:', 'Region:', 'Total:', 'Male:', 'Female:'],
                        localize=True,
                        sticky=False,
                        labels=True,
                        style="""
                            background-color: white;
                            border: 2px solid black;
                            border-radius: 3px;
                            box-shadow: 3px;
                            padding: 10px;
                        """,
                    ),
                    popup=folium.GeoJsonPopup(
                        fields=[prefecture_col, region_col, total_col, male_col, female_col],
                        aliases=['Prefecture:', 'Region:', 'Total:', 'Male:', 'Female:'],
                    ),
                    name=region
                ).add_to(m)
            
            # Add legend for regions
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; right: 50px; width: 250px; height: auto;
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px; border-radius: 5px;">
                <p style="margin-bottom: 10px;"><strong>Regions</strong></p>
            '''
            for region, color in region_colors.items():
                legend_html += f'<p style="margin: 5px;"><span style="background-color:{color}; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></span>{region}</p>'
            legend_html += '</div>'
            m.get_root().html.add_child(folium.Element(legend_html))
            
        else:
            # Add choropleth layer for population
            folium.Choropleth(
                geo_data=gdf_display,
                data=gdf_display,
                columns=[prefecture_col, total_col],
                key_on=f'feature.properties.{prefecture_col}',
                fill_color='YlOrRd',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name='Total Population'
            ).add_to(m)
            
            # Add interactive layer
            folium.GeoJson(
                gdf_display,
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': 'blue',
                    'weight': 1,
                    'fillOpacity': 0
                },
                popup=folium.GeoJsonPopup(
                    fields=[prefecture_col, region_col, total_col, male_col, female_col],
                    aliases=['Prefecture:', 'Region:', 'Total:', 'Male:', 'Female:'],
                    localize=True,
                    labels=True
                ),
                tooltip=folium.GeoJsonTooltip(
                    fields=[prefecture_col, region_col, total_col, male_col, female_col],
                    aliases=['Prefecture:', 'Region:', 'Total:', 'Male:', 'Female:'],
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: white;
                        border: 2px solid black;
                        border-radius: 3px;
                        box-shadow: 3px;
                        padding: 10px;
                    """,
                    max_width=800
                )
            ).add_to(m)
        
        # Display the map
        st.markdown(f"### {'🌍 ' + selected_region if selected_region and selected_region != 'All Regions' else '🌍 All Regions'}")
        st.markdown("*Hover over any prefecture to see total population and breakdown by sex*")
        st_data = st_folium(m, width=1200, height=600)
        
        # ==================== STATISTICS SECTION ====================
        st.markdown("---")
        
        # Overall Statistics
        st.markdown("## 📊 Overall Statistics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("Regions", gdf_clean[region_col].nunique())
        
        with col2:
            st.metric("Prefectures", len(gdf_clean))
        
        with col3:
            st.metric("Total Population", f"{gdf_clean[total_col].sum():,}")
        
        with col4:
            st.metric("Total Male", f"{gdf_clean[male_col].sum():,}")
        
        with col5:
            st.metric("Total Female", f"{gdf_clean[female_col].sum():,}")
        
        with col6:
            ratio = (gdf_clean[male_col].sum() / gdf_clean[female_col].sum() * 100)
            st.metric("M/F Ratio", f"{ratio:.1f}%")
        
        st.markdown("---")
        
        # ==================== REGIONAL ANALYSIS ====================
        st.markdown("## 🌍 Regional Analysis")
        
        # Aggregate by region
        region_stats = gdf_clean.groupby(region_col).agg({
            prefecture_col: 'count',
            total_col: 'sum',
            male_col: 'sum',
            female_col: 'sum'
        }).reset_index()
        region_stats.columns = ['Region', 'Prefectures', 'Total Population', 'Male', 'Female']
        region_stats = region_stats.sort_values('Total Population', ascending=False)
        
        # Regional visualizations
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.markdown("### 📊 Population by Region")
            fig_region_bar = px.bar(
                region_stats,
                x='Region',
                y='Total Population',
                color='Region',
                color_discrete_map=region_colors,
                text='Total Population'
            )
            fig_region_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_region_bar.update_layout(
                xaxis_tickangle=-45,
                height=500,
                showlegend=False,
                xaxis_title="",
                yaxis_title="Population"
            )
            st.plotly_chart(fig_region_bar, use_container_width=True)
        
        with viz_col2:
            st.markdown("### 🥧 Regional Distribution (%)")
            fig_region_pie = px.pie(
                region_stats,
                values='Total Population',
                names='Region',
                color='Region',
                color_discrete_map=region_colors,
                hole=0.4
            )
            fig_region_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_region_pie.update_layout(height=500)
            st.plotly_chart(fig_region_pie, use_container_width=True)
        
        # Regional statistics table
        st.markdown("### 📋 Regional Statistics Summary")
        region_stats_display = region_stats.copy()
        region_stats_display['% Male'] = (region_stats_display['Male'] / region_stats_display['Total Population'] * 100).round(2)
        region_stats_display['% Female'] = (region_stats_display['Female'] / region_stats_display['Total Population'] * 100).round(2)
        region_stats_display['Avg Pop/Prefecture'] = (region_stats_display['Total Population'] / region_stats_display['Prefectures']).round(0)
        st.dataframe(region_stats_display, use_container_width=True)
        
        # ==================== GENDER ANALYSIS ====================
        st.markdown("---")
        st.markdown("## 👥 Gender Distribution Analysis")
        
        # Regional gender breakdown
        st.markdown("### Gender Distribution by Region")
        
        # Prepare data for stacked bar chart
        gender_by_region = region_stats.copy()
        
        fig_gender_region = go.Figure()
        fig_gender_region.add_trace(go.Bar(
            name='Male',
            x=gender_by_region['Region'],
            y=gender_by_region['Male'],
            marker_color='#4A90E2',
            text=gender_by_region['Male'],
            texttemplate='%{text:,.0f}',
            textposition='inside'
        ))
        fig_gender_region.add_trace(go.Bar(
            name='Female',
            x=gender_by_region['Region'],
            y=gender_by_region['Female'],
            marker_color='#E94B3C',
            text=gender_by_region['Female'],
            texttemplate='%{text:,.0f}',
            textposition='inside'
        ))
        
        fig_gender_region.update_layout(
            barmode='stack',
            xaxis_tickangle=-45,
            height=500,
            xaxis_title="Region",
            yaxis_title="Population"
        )
        st.plotly_chart(fig_gender_region, use_container_width=True)
        
        # ==================== PREFECTURE DETAILS ====================
        st.markdown("---")
        st.markdown("## 🏘️ Prefecture Details")
        
        tab1, tab2, tab3 = st.tabs(["📊 Top Prefectures", "📈 By Region", "📋 Complete Data"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏆 Top 10 Prefectures by Population")
                top_10 = gdf_clean.nlargest(10, total_col)[[prefecture_col, region_col, total_col, male_col, female_col]].copy()
                top_10.columns = ['Prefecture', 'Region', 'Total', 'Male', 'Female']
                top_10['% Male'] = (top_10['Male'] / top_10['Total'] * 100).round(2)
                top_10['% Female'] = (top_10['Female'] / top_10['Total'] * 100).round(2)
                top_10.index = range(1, len(top_10) + 1)
                st.dataframe(top_10, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 Top 10 - Gender Breakdown")
                top_10_chart = gdf_clean.nlargest(10, total_col)[[prefecture_col, male_col, female_col]].copy()
                top_10_chart.columns = ['Prefecture', 'Male', 'Female']
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    name='Male',
                    x=top_10_chart['Prefecture'],
                    y=top_10_chart['Male'],
                    marker_color='#4A90E2'
                ))
                fig_bar.add_trace(go.Bar(
                    name='Female',
                    x=top_10_chart['Prefecture'],
                    y=top_10_chart['Female'],
                    marker_color='#E94B3C'
                ))
                
                fig_bar.update_layout(
                    barmode='group',
                    xaxis_tickangle=-45,
                    height=400,
                    xaxis_title="",
                    yaxis_title="Population"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        
        with tab2:
            st.markdown("### 📍 Prefectures Grouped by Region")
            
            # Select region to display
            display_region = st.selectbox(
                "Select Region:",
                sorted(gdf_clean[region_col].unique()),
                key='region_selector'
            )
            
            region_data = gdf_clean[gdf_clean[region_col] == display_region][[
                prefecture_col, total_col, male_col, female_col
            ]].copy()
            region_data.columns = ['Prefecture', 'Total Population', 'Male', 'Female']
            region_data['% Male'] = (region_data['Male'] / region_data['Total Population'] * 100).round(2)
            region_data['% Female'] = (region_data['Female'] / region_data['Total Population'] * 100).round(2)
            region_data = region_data.sort_values('Total Population', ascending=False).reset_index(drop=True)
            region_data.index = range(1, len(region_data) + 1)
            
            # Display metrics for selected region
            rcol1, rcol2, rcol3, rcol4 = st.columns(4)
            with rcol1:
                st.metric("Prefectures", len(region_data))
            with rcol2:
                st.metric("Total Pop", f"{region_data['Total Population'].sum():,}")
            with rcol3:
                st.metric("Male", f"{region_data['Male'].sum():,}")
            with rcol4:
                st.metric("Female", f"{region_data['Female'].sum():,}")
            
            st.dataframe(region_data, use_container_width=True, height=400)
            
            # Chart for selected region
            st.markdown(f"### 📊 Population Distribution in {display_region}")
            fig_region_detail = px.bar(
                region_data.reset_index(),
                x='Prefecture',
                y=['Male', 'Female'],
                title=f"Gender Distribution - {display_region}",
                barmode='group',
                color_discrete_map={'Male': '#4A90E2', 'Female': '#E94B3C'}
            )
            fig_region_detail.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig_region_detail, use_container_width=True)
        
        with tab3:
            st.markdown("### 📋 Complete Prefecture Statistics")
            
            # Create comprehensive table
            stats_df = gdf_clean[[region_col, prefecture_col, total_col, male_col, female_col]].copy()
            stats_df.columns = ['Region', 'Prefecture', 'Total Population', 'Male', 'Female']
            stats_df['% Male'] = (stats_df['Male'] / stats_df['Total Population'] * 100).round(2)
            stats_df['% Female'] = (stats_df['Female'] / stats_df['Total Population'] * 100).round(2)
            
            # Sort by region then population
            stats_df = stats_df.sort_values(['Region', 'Total Population'], ascending=[True, False]).reset_index(drop=True)
            stats_df.index = range(1, len(stats_df) + 1)
            
            st.dataframe(stats_df, use_container_width=True, height=500)
            
            # Download button
            csv = stats_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Complete Statistics as CSV",
                data=csv,
                file_name="togo_population_complete_stats.csv",
                mime="text/csv",
            )
        
        # ==================== COMPARATIVE ANALYSIS ====================
        st.markdown("---")
        st.markdown("## 📊 Comparative Analysis")
        
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            st.markdown("### 🔍 Regional Gender Ratio Comparison")
            
            region_gender_ratio = region_stats.copy()
            region_gender_ratio['M/F Ratio (%)'] = (region_gender_ratio['Male'] / region_gender_ratio['Female'] * 100).round(2)
            region_gender_ratio['Difference'] = region_gender_ratio['Male'] - region_gender_ratio['Female']
            
            fig_ratio = px.bar(
                region_gender_ratio,
                x='Region',
                y='M/F Ratio (%)',
                color='M/F Ratio (%)',
                color_continuous_scale=['#E94B3C', '#FFFFFF', '#4A90E2'],
                color_continuous_midpoint=100,
                text='M/F Ratio (%)'
            )
            fig_ratio.add_hline(y=100, line_dash="dash", line_color="black", 
                               annotation_text="Equal Ratio (100%)")
            fig_ratio.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_ratio.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig_ratio, use_container_width=True)
            
            st.dataframe(
                region_gender_ratio[['Region', 'Male', 'Female', 'M/F Ratio (%)', 'Difference']],
                use_container_width=True
            )
        
        with comp_col2:
            st.markdown("### 📈 Average Population per Prefecture by Region")
            
            avg_pop = region_stats.copy()
            avg_pop['Avg Population'] = (avg_pop['Total Population'] / avg_pop['Prefectures']).round(0)
            
            fig_avg = px.bar(
                avg_pop,
                x='Region',
                y='Avg Population',
                color='Region',
                color_discrete_map=region_colors,
                text='Avg Population'
            )
            fig_avg.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_avg.update_layout(
                xaxis_tickangle=-45,
                height=400,
                showlegend=False,
                xaxis_title="",
                yaxis_title="Average Population per Prefecture"
            )
            st.plotly_chart(fig_avg, use_container_width=True)
            
            st.dataframe(
                avg_pop[['Region', 'Prefectures', 'Total Population', 'Avg Population']],
                use_container_width=True
            )
        
        # ==================== DENSITY ANALYSIS ====================
        st.markdown("---")
        st.markdown("## 🗺️ Regional Insights")
        
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        
        with insight_col1:
            st.markdown("### 🏆 Most Populous Region")
            most_populous = region_stats.iloc[0]
            st.metric("Region", most_populous['Region'])
            st.metric("Population", f"{most_populous['Total Population']:,}")
            st.metric("Prefectures", int(most_populous['Prefectures']))
        
        with insight_col2:
            st.markdown("### 🏆 Most Populous Prefecture")
            most_pop_prefecture = gdf_clean.nlargest(1, total_col).iloc[0]
            st.metric("Prefecture", most_pop_prefecture[prefecture_col])
            st.metric("Region", most_pop_prefecture[region_col])
            st.metric("Population", f"{most_pop_prefecture[total_col]:,}")
        
        with insight_col3:
            st.markdown("### ⚖️ Most Balanced Region (Gender)")
            region_stats_ratio = region_stats.copy()
            region_stats_ratio['Ratio Diff'] = abs((region_stats_ratio['Male'] / region_stats_ratio['Female'] * 100) - 100)
            balanced_region = region_stats_ratio.nsmallest(1, 'Ratio Diff').iloc[0]
            st.metric("Region", balanced_region['Region'])
            ratio_val = (balanced_region['Male'] / balanced_region['Female'] * 100)
            st.metric("M/F Ratio", f"{ratio_val:.2f}%")
            st.metric("Difference", f"{abs(balanced_region['Male'] - balanced_region['Female']):,.0f}")
        
        # ==================== HEATMAP ====================
        st.markdown("---")
        st.markdown("## 🌡️ Population Heatmap by Region and Gender")
        
        # Prepare data for heatmap
        heatmap_data = gdf_clean.groupby(region_col).agg({
            male_col: 'sum',
            female_col: 'sum',
            total_col: 'sum'
        }).reset_index()
        
        # Normalize for better visualization
        heatmap_data['Male (%)'] = (heatmap_data[male_col] / heatmap_data[total_col] * 100).round(2)
        heatmap_data['Female (%)'] = (heatmap_data[female_col] / heatmap_data[total_col] * 100).round(2)
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=[heatmap_data['Male (%)'].values, heatmap_data['Female (%)'].values],
            x=heatmap_data[region_col].values,
            y=['Male %', 'Female %'],
            colorscale='RdBu_r',
            text=[[f"{v:.1f}%" for v in heatmap_data['Male (%)'].values],
                  [f"{v:.1f}%" for v in heatmap_data['Female (%)'].values]],
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="Percentage")
        ))
        
        fig_heatmap.update_layout(
            title="Gender Distribution Percentage by Region",
            xaxis_title="Region",
            yaxis_title="Gender",
            height=300
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
    except FileNotFoundError:
        st.error("❌ Error: 'population_par_prefecture.geojson' file not found!")
        st.markdown("Please make sure the GeoJSON file is in the same directory as this app.")
        
    except KeyError as e:
        st.error(f"❌ Error: Column not found - {str(e)}")
        st.markdown("**Please check the column names in your GeoJSON file.**")
        
    except Exception as e:
        st.error(f"❌ Error loading the map: {str(e)}")
        st.markdown("Please check your data file and try again.")
        import traceback
        st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown("*Data visualization built with Streamlit, Folium, and Plotly | Population data by Prefecture and Region*")
>>>>>>> 45baab05b73844ad4071b8ab5b464bacf9a1cfe6
