import streamlit as st
from datetime import datetime

# Configure the page
st.set_page_config(
    page_title="About - Togo Stat Explorer",
    page_icon="ℹ️",
    layout="wide"
)

# Header
st.title("About Togo Stat Explorer")
st.markdown("---")

# App Description Section
#st.markdown("## About This Application")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
   **Togo Stat Explorer** is an interactive web application designed to enhance **FAIR principles** 
    (Findable, Accessible, Interoperable, Reusable) for demographic and geographic data in Togo. 
    This application represents my commitment to making Togolese data more discoverable, accessible, 
    and usable for researchers, policymakers, and citizens worldwide.
    
    ### 🎯 Purpose
    This application was created to:
    - **Visualize** population distribution across Togo's prefectures
    - **Provide** interactive maps for geographic exploration
    - **Enable** detailed analysis of demographic data
    - **Support** researchers, policymakers, and students interested in Togo's demographics
    - **Demonstrate** modern data visualization techniques using Python
    
    ### 🌍 Geographic Coverage
    The app covers all **37 prefectures** of Togo, providing complete national coverage 
    of administrative divisions and their respective population counts.
    """)

with col2:
    # App statistics
    st.markdown("### 📊 App Statistics")
    
    # You can update these with actual data
    stats_data = {
        "Total Prefectures": "37",
        "Total Population": "~9.8M",
        "Data Sources": "Worldometer",
        "Last Updated": "2025",
        "Map Projections": "WGS84"
    }
    
    for key, value in stats_data.items():
        st.metric(key, value)

# Features Section
st.markdown("---")
st.markdown("## 🚀 Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🗺️ Interactive Mapping
    - **Choropleth maps** with population-based color coding
    - **Hover tooltips** for instant prefecture information
    - **Clickable boundaries** for detailed exploration
    - **Zoom and pan** functionality for detailed viewing
    """)

with col2:
    st.markdown("""
    ### 🔍 Advanced Filtering
    - **Single prefecture** detailed view
    - **Multiple prefecture** comparison mode
    - **Population range** filtering
    - **Real-time** map updates
    """)

with col3:
    st.markdown("""
    ### 📈 Data Analysis
    - **Population statistics** and rankings
    - **Comparative analysis** between prefectures
    - **Data export** capabilities (CSV download)
    - **Interactive charts** and visualizations
    """)

# Technology Stack
st.markdown("---")
st.markdown("## 🛠️ Technology Stack")

tech_col1, tech_col2 = st.columns(2)

with tech_col1:
    st.markdown("""
    ### Frontend & Visualization
    - **Streamlit** - Web application framework
    - **Folium** - Interactive mapping library
    - **Plotly** - Advanced data visualization
    - **HTML/CSS** - Custom styling and layouts
    """)

with tech_col2:
    st.markdown("""
    ### Data Processing
    - **GeoPandas** - Geospatial data manipulation
    - **Pandas** - Data analysis and processing
    - **Python** - Core programming language
    - **GeoJSON** - Geographic data format
    """)

# Data Sources Section
st.markdown("---")
st.markdown("## 📊 Data Sources")

tech_col1, tech_col2 = st.columns(2) 

with tech_col1:
  st.markdown("""
### Geographic Data
- **Prefecture boundaries**: Official administrative boundaries of Togo
- **Coordinate system**: WGS84 (EPSG:4326)
- **Data format**: GeoJSON with embedded population attributes

""")

### Data Quality
#All data has been validated and cross-referenced with official sources to ensure accuracy and reliability.
with tech_col2:
  st.markdown("""
### Population Data
- **Source**:   [National census](https://inseed.tg/) and [Administrative subdivision of Togo](https://github.com/gausoft/Subdivision_administrative_Togo)
- **Coverage**: All 37 prefectures of Togo
- **Metrics**: Population counts by administrative division
- **Currency**: Most recent available census data

""")

# About Developer Section
st.markdown("---")
st.markdown("## 👨‍💻 About the Developer")

# Create columns for developer info
dev_col1, dev_col2 , dev_col3 , dev_col4  = st.columns(4)

with dev_col1:
    # You can add your photo here if you have one
    # st.image("your_photo.jpg", width=200)
    
    st.markdown("""
    ### Asma Bahamyirou, PhD.
    
    **Statistician & Causal Inference Specialist**
    
    I am Data-driven professional. Passionate about solving complex problems through technology, AI, and advanced statistical methods to deliver actionable insights.
    
  
    """)

with dev_col2:
    # You can add your photo here if you have one
    # st.image("your_photo.jpg", width=200)
    
    st.markdown("""
    #### 🎓 Background
    - **Education**: [Your education background]
    - **Specialization**: Geospatial analysis, demographic studies, data visualization
    - **Experience**: [Your relevant experience]
          

    """)

with dev_col3:
    # You can add your photo here if you have one
    # st.image("your_photo.jpg", width=200)
    
    st.markdown("""
    ### 📧 Get in Touch
    - **Email**: abahamyirou@gmail.com
    - **LinkedIn**: [LinkedIn](https://www.linkedin.com/in/asma-bahamyirou-ph-d-22933233/)
    - **GitHub**: [PopTogo](https://github.com/Bahamyirou/PopTogo)
  
    """)
with dev_col4:
    st.markdown("""             
    ### 💡 Collaboration
    - **Research Projects**: Open to collaboration
    - **Consulting**: Available for GIS projects
    - **Speaking**: Conference presentations    
    """)

# Project Information
st.markdown("---")
st.markdown("## 📋 Project Information")

project_col1, project_col2 , project_col3 = st.columns(3)

with project_col1:
    st.markdown("""
    ### 🗓️ Development Timeline
    - **Started**: 2025-12-01
    - **Version 1.0**: 2025-12-20
    - **Last Update**: 2025-12-20
    - **Status**: Active development
    """)

with project_col2:
    st.markdown("""
    ### 🔄 Future Enhancements
    - Integration with real-time demographic data
    - Additional socioeconomic indicators
    - Mobile-responsive design improvements
    - Multi-language support (French/English)
    """)
with project_col3:
    st.markdown("""             
    ### 🔀 Want to contribute to this app?
    - Please create a new branch and submit your changes!
    - If you’d like to request new features, feel free to open an issue on GitHub or email me.  
    """)

# Acknowledgments
st.markdown("---")
st.markdown("## 🙏 Acknowledgments")

st.markdown("""
### Data Contributors
- **Togo National Institute of Statistics** - For providing official demographic data
- **OpenStreetMap Contributors** - For geographic base map data
- **Streamlit Community** - For the excellent documentation and community support

### Special Thanks
Thank you to all the open-source contributors and the data science community 
for making tools like this possible through collaborative development and knowledge sharing.
""")

# Disclaimer
st.markdown("---")
st.markdown("## ⚠️ Disclaimer")

st.info("""
**Data Accuracy**: While every effort has been made to ensure data accuracy, 
this application is intended for educational and research purposes. 
For official statistics, please consult the Togo National Institute of Statistics.

**Software License**: This application is provided as-is for educational purposes. 
Please contact the developer for commercial use inquiries.
""")

# Footer with timestamp
st.markdown("---")
current_year = datetime.now().year
st.markdown(f"*© {current_year} Togo Prefecture Explorer. Built with ❤️ using Streamlit and Python.*")

# Add some custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
    }
    
    .tech-stack {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .contact-info {
        text-align: center;
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)