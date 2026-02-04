# Togolese Pop Statistics App 

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://posit-connect-dv.phac-aspc.gc.ca/wastewater-KeyMetrics/) [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A Streamlit-based dashboard for monitoring, analyzing, Togolese population statistics. 


## 🚀 Features

- ⚠️ About Page
- 🗺️ Population Distribution

## 🏗️ Architecture

```
Togo Stat Pop - streamlit/
├── app.py                    # Main application entry
├── views/                    # Page components
│   ├── AboutPage.py          # About the page
│   ├── PopDistribution.py    # Prefecture and Regional Distribution page
├── utils.py                  # Shared util functions
├── .env                      # Environment configuration
└── requirements.txt          # Dependencies
```


## 🛠️ Installation

```bash
git clone https://github.com/Bahamyirou/PopTogo.git
cd  C:\PopTogo
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

1. Cold Cluster Startup:
   The first data load may take up to 5 minutes if the data cluster is cold. Please allow extra time on startup.

2. Contact abahamyirou@gmail.com for other issues.