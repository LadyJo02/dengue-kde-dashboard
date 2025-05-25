import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import streamlit as st
from utils.kde_processing import generate_kde

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/dengue_climate_data.csv')
    gdf = gpd.read_file('data/gadm41_PHL_2.shp')
    return df, gdf

def prepare_points(df, year):
    df_year = df.copy()
    df_year[str(year)] = pd.to_numeric(df_year[str(year)], errors='coerce').fillna(0).astype(int)

    points = []
    for _, row in df_year.iterrows():
        count = row[str(year)]
        if count > 0:
            points.extend([[row["centroid_lon"], row["centroid_lat"]]] * count)

    if not points or len(np.unique(points, axis=0)) < 2:
        return None  # Not enough unique points

    return np.array(points).T

# UI
st.set_page_config(page_title="Dengue KDE Dashboard", layout="wide")
st.title("🦟 Dengue KDE Hotspot Dashboard")
st.markdown("Visualizing dengue hotspots in **Northern Mindanao (2018–2024)** using Kernel Density Estimation (KDE)")

df, gdf = load_data()
years = list(range(2018, 2025))
band_methods = {"Scott": "scott", "Silverman": "silverman", "LOOCV (0.15)": 0.15}

year = st.selectbox("📅 Select Year", years)
bw_label = st.selectbox("📏 Select Bandwidth Method", list(band_methods.keys()))
bw_value = band_methods[bw_label]

points = prepare_points(df, year)

if points is None:
    st.warning(f"⚠️ Not enough unique points for KDE in {year}. Try another year.")
else:
    xi, yi, zi = generate_kde(points, bandwidth=bw_value)
    if zi.size == 0:
        st.error("❌ KDE failed due to numerical issue. Try another bandwidth or year.")
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        gdf.boundary.plot(ax=ax, linewidth=0.5, edgecolor='black')
        img = ax.imshow(
            zi.T,
            extent=[xi.min(), xi.max(), yi.min(), yi.max()],
            origin='lower',
            cmap='Reds',
            alpha=0.8,
            norm=mcolors.Normalize(vmin=zi.min(), vmax=zi.max())
        )
        fig.colorbar(img, ax=ax, label="Density")
        ax.set_title(f"Dengue KDE Hotspot Map - {year} ({bw_label})")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        st.pyplot(fig)
