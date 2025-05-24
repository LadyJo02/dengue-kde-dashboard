# Dengue KDE Dashboard

This Streamlit dashboard visualizes dengue hotspots in Northern Mindanao (2018–2024) using Kernel Density Estimation (KDE). It allows users to interactively explore hotspot evolution and compare bandwidth methods (Scott, Silverman, LOOCV).

## Features
- Yearly KDE maps from 2018–2024
- Bandwidth method comparison
- Real-time dengue hotspot viewer
- Raster export (.png, .tif)

## Dataset
- `dengue_climate_data.csv` – Case counts + environmental features
- `gadm41_PHL_2.*` – Shapefile for boundary mapping

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment
You can deploy this using:
- [Streamlit Cloud](https://streamlit.io/cloud)
- GitHub + Heroku (for advanced hosting)

## Authors
Pabololot, Honey Angel H., 
Sanchez Airyll H., Santos, 
Joanna Reyda D. 
University of Science and Technology of Southern Philippines – CDO

## Acknowledgements
Thanks to our instructor and project collaborators for guiding this geospatial research effort.
