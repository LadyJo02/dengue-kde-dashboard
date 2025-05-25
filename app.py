import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html
from utils.kde_processing import generate_kde

# ------------------- Load Data -------------------
@st.cache_data

def load_data():
    df = pd.read_csv("data/dengue_climate_data.csv")
    gdf = gpd.read_file("data/gadm41_PHL_2.shp")
    return df, gdf

# ------------------- Prepare KDE Points -------------------
def prepare_points(df, year):
    df_year = df.copy()
    df_year[str(year)] = pd.to_numeric(df_year[str(year)], errors="coerce").fillna(0).astype(int)

    points = []
    for _, row in df_year.iterrows():
        count = row[str(year)]
        if count > 0:
            points.extend([[row["centroid_lon"], row["centroid_lat"]]] * count)

    if not points:
        return np.empty((2, 0))

    return np.array(points).T

# ------------------- UI Setup -------------------
st.set_page_config(layout="wide", page_title="Dengue KDE Dashboard")

# ------------------- Header -------------------
st.markdown("""
    <style>
    .main-title { font-size: 2.5em; font-weight: bold; color: #2c3e50; }
    .subheader { font-size: 1.2em; font-weight: 500; margin-top: 10px; }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🦟 Dengue KDE Hotspot Dashboard</h1>", unsafe_allow_html=True)
st.markdown("Visualizing dengue hotspots in **Northern Mindanao (2018–2024)** using Kernel Density Estimation (KDE)")

# ------------------- Sidebar Controls -------------------
st.sidebar.header("🗂️ Dashboard Controls")
years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
band_methods = {'Scott': 'scott', 'Silverman': 'silverman', 'LOOCV (0.15)': 0.15}

year = st.sidebar.selectbox("📅 Select Year", years)
bw_label = st.sidebar.selectbox("🧪 Select Bandwidth Method", list(band_methods.keys()))
bw_value = band_methods[bw_label]

# ------------------- Load Data -------------------
df, gdf = load_data()

# ------------------- Layout -------------------
col1, col2 = st.columns([1, 2])

# ----- LEFT: KDE Summary Cards -----
with col1:
    st.subheader("📍 Top 5 Locations by Total Dengue Cases")
    df_total = df.copy()
    df_total["Total_Cases"] = df[[str(y) for y in years]].sum(axis=1)
    top5 = df_total.sort_values("Total_Cases", ascending=False).head(5)

    for _, row in top5.iterrows():
        st.markdown(f"<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"**{row['City/Municipality']}**")
        st.markdown(f"- Total Cases: {int(row['Total_Cases'])}")
        st.markdown(f"- Avg Temperature: {round(row['Avg_Temperature'], 2)}°C")
        st.markdown(f"- Avg Humidity: {round(row['Avg_Humidity'], 2)}%")
        st.markdown(f"- Avg Precipitation: {round(row['Avg_Precipitation'], 2) if not pd.isna(row['Avg_Precipitation']) else 'N/A'} mm")
        st.markdown("</div>", unsafe_allow_html=True)

# ----- RIGHT: KDE Map -----
with col2:
    points = prepare_points(df, year)
    if points.shape[1] == 0:
        st.warning("No dengue cases recorded for the selected year.")
    else:
        xi, yi, zi = generate_kde(points, bandwidth=bw_value)

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
        ax.set_title(f"Dengue KDE Hotspot Map - {year} ({bw_label})", fontsize=14, fontweight="bold")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        st.pyplot(fig)

# ------------------- KDE HTML MAP -------------------
st.divider()
st.subheader("🧭 Interactive KDE Detail Map")
with open("data/kde_hotspots_with_details.html", "r", encoding="utf-8") as f:
    html(f.read(), height=700, scrolling=True)
