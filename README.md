# PopTogo

# Togolese Pop Statistics App 

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://posit-connect-dv.phac-aspc.gc.ca/wastewater-KeyMetrics/) [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A Streamlit-based dashboard for monitoring, analyzing, Togolese population statistics. 


## 🚀 Features

- 🚰 View and impute XXXX data
- 🦠 View and XXXXX
- 🆕 View the 2 most recent XXXXX
- ⚠️ View recorded XXXXX

## 🏗️ Architecture

```
wastewater-trends-streamlit/
├── app.py                    # Main application entry
├── views/                    # Page components
│   ├── ww-trends.py          # Handles the "Wastewater Trends" page
│   ├── mpox.py               # Handles the "Mpox Trends" page
│   ├── latest-measures.py    # Handles the "Latest Measures" page
│   ├── large-jumps.py        # Handles the "Large Jumps" page
│   ├── admin-page.py         # Shows a log of user actions to admin users
├── utils.py                  # Shared util functions
├── .env                      # Environment configuration
└── requirements.txt          # Dependencies
```

![App Architecture Diagram](diagram.png)

#### Refer to [architecture.md](architecture.md) for a more detailed overview


## 🛠️ Installation

```bash
git clone https://github.com/PHACDataHub/wastewater-trends-streamlit.git
cd  C:\StreamlitTogo
python -m venv .venv
source .venv/bin/activate # If on Linux
.venv\Scripts\activate # If on Windows
pip install -r requirements.txt
```
## 🔧 Configuration

Create a `.env` file in the project root:


## 📈 Usage

`streamlit run app.py`

## 🔍 Troubleshooting

#### Common issues:

1. **Cold Cluster Startup:**  
   The first data load may take up to 5 minutes if the data cluster is cold. Please allow extra time on startup.

2. **Configuration Errors:**  
   - Ensure your `.env` file is set up correctly with the proper values for `ADB_INSTANCE_NAME`, `ADB_HTTP_PATH`, and `ADB_API_KEY`.  
   - Verify that the table names in the `.env` (e.g. `WW_TRENDS_TABLE`, `MPOX_TABLE`, etc.) are correct.

3. **Permission Issues:**  
   If you cannot modify data or load certain pages, check your permissions. In development mode, The `DEVELOPMENT` flag should be added to your `.env`.
