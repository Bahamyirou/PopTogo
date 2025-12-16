import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Configure the Streamlit page
st.set_page_config(
    page_title="Togo Prefecture Population Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("Togo Prefecture Population Distribution")
st.markdown("---")
st.markdown("### Interactive map showing population by prefecture and gender")
st.markdown("*Hover over any prefecture to see total population and breakdown by sex*")

# Create a container for the map
with st.container():
    try:
        # Load the geojson with population data
        gdf = gpd.read_file('population_par_prefecture.geojson')
        
        # Display column names to help identify the correct fields
        st.sidebar.markdown("### Available Data Fields")
        st.sidebar.write(gdf.columns.tolist())
        
        # ⚠️ ADJUST THESE COLUMN NAMES based on your actual GeoJSON structure
        # Common possibilities: 'prefecture', 'Prefecture', 'nom_prefecture', etc.
        prefecture_col = 'prefecture'  # Adjust this
        region_col = 'Region'  # Adjust this if available
        total_col = 'Ensemble'  # Total population - adjust this
        male_col = 'Masculin'  # Male population - adjust this (could be 'male', 'masculin', 'homme')
        female_col = 'Feminin'  # Female population - adjust this (could be 'female', 'feminin', 'femme')
        
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
            columns=[prefecture_col, total_col],
            key_on=f'feature.properties.{prefecture_col}',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Total Population'
        ).add_to(m)
        
        # Add interactive features with detailed hover showing all 3 values
        folium.GeoJson(
            gdf,
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': 'blue',
                'weight': 1,
                'fillOpacity': 0
            },
            popup=folium.GeoJsonPopup(
                fields=[prefecture_col, total_col, male_col, female_col],
                aliases=['Prefecture:', 'Total Population:', 'Male:', 'Female:'],
                localize=True,
                labels=True
            ),
            tooltip=folium.GeoJsonTooltip(
                fields=[prefecture_col, total_col, male_col, female_col],
                aliases=['Prefecture:', 'Population:', 'Male:', 'Female:'],
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
        
        # Display the map in Streamlit
        st_data = st_folium(m, width=1200, height=600)
        
        # Display statistics
        st.markdown("---")
        st.markdown("## 📊 Overall Statistics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Prefectures", len(gdf))
        
        with col2:
            st.metric("Total Population", f"{gdf[total_col].sum():,}")
        
        with col3:
            st.metric("Total Male", f"{gdf[male_col].sum():,}")
        
        with col4:
            st.metric("Total Female", f"{gdf[female_col].sum():,}")
        
        with col5:
            # Calculate gender ratio
            ratio = (gdf[male_col].sum() / gdf[female_col].sum() * 100) if gdf[female_col].sum() > 0 else 0
            st.metric("Male/Female Ratio", f"{ratio:.1f}%")
        
        st.markdown("---")
        
        # Create two columns for visualizations
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.markdown("### 🏆 Top 10 Prefectures by Total Population")
            top_10 = gdf.nlargest(10, total_col)[[prefecture_col, total_col, male_col, female_col]].copy()
            top_10.columns = ['Prefecture', 'Ensemble', 'Male', 'Female']
            top_10.index = range(1, len(top_10) + 1)
            st.dataframe(top_10, use_container_width=True)
        
        with viz_col2:
            st.markdown("### 👥 Gender Distribution Chart")
            # Pie chart for overall gender distribution
            gender_data = pd.DataFrame({
                'Gender': ['Male', 'Female'],
                'Count': [gdf[male_col].sum(), gdf[female_col].sum()]
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
        
        # Bar chart for top prefectures by gender
        st.markdown("### 📊 Top 10 Prefectures - Population by Gender")
        top_10_chart = gdf.nlargest(10, total_col)[[prefecture_col, male_col, female_col]].copy()
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
            height=500,
            xaxis_title="Prefecture",
            yaxis_title="Population"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Additional statistics table
        st.markdown("### 📋 Complete Prefecture Statistics")
        
        # Create a comprehensive table
        stats_df = gdf[[prefecture_col, total_col, male_col, female_col]].copy()
        if region_col in gdf.columns:
            stats_df = gdf[[region_col, prefecture_col, total_col, male_col, female_col]].copy()
            stats_df.columns = ['Region', 'Prefecture', 'Total Population', 'Male', 'Female']
        else:
            stats_df.columns = ['Prefecture', 'Total Population', 'Male', 'Female']
        
        # Add percentage columns
        stats_df['% Male'] = (stats_df['Male'] / stats_df['Total Population'] * 100).round(2)
        stats_df['% Female'] = (stats_df['Female'] / stats_df['Total Population'] * 100).round(2)
        
        # Sort by total population
        stats_df = stats_df.sort_values('Total Population', ascending=False).reset_index(drop=True)
        stats_df.index = range(1, len(stats_df) + 1)
        
        st.dataframe(stats_df, use_container_width=True, height=400)
        
        # Download button for the data
        csv = stats_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Statistics as CSV",
            data=csv,
            file_name="togo_prefecture_population_stats.csv",
            mime="text/csv",
        )
        
    except FileNotFoundError:
        st.error("❌ Error: 'population_par_prefecture.geojson' file not found!")
        st.markdown("Please make sure the GeoJSON file is in the same directory as this app.")
        
    except KeyError as e:
        st.error(f"❌ Error: Column not found - {str(e)}")
        st.markdown("**Please update the column names in the code to match your GeoJSON file.**")
        st.markdown("Available columns are shown in the sidebar.")
        
    except Exception as e:
        st.error(f"❌ Error loading the map: {str(e)}")
        st.markdown("Please check your data file and try again.")

# Footer
st.markdown("---")
st.markdown("*Data visualization built with Streamlit, Folium, and Plotly*")