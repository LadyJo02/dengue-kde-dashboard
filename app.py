import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from utils.kde_processing import generate_kde
from streamlit.components.v1 import html

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/dengue_climate_data.csv')
    gdf = gpd.read_file('data/gadm41_PHL_2.shp')
    return df, gdf

# Prepare KDE points for the selected year
def prepare_points(df, year):
    df_year = df.copy()
    df_year[str(year)] = pd.to_numeric(df_year[str(year)], errors='coerce').fillna(0).astype(int)

    points = []
    for _, row in df_year.iterrows():
        count = row[str(year)]
        if count > 0:
            points.extend([[row["centroid_lon"], row["centroid_lat"]]] * count)

    if not points:
        return None

    return pd.DataFrame(points, columns=['lon', 'lat']).T

# Main App Layout
st.set_page_config(layout="wide")
st.title("🦟 Dengue KDE Hotspot Dashboard")
st.markdown("Visualizing dengue hotspots in **Northern Mindanao (2018–2024)** using Kernel Density Estimation (KDE)")

# Load data
df, gdf = load_data()
years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
band_methods = {'Scott': 'scott', 'Silverman': 'silverman', 'LOOCV (0.15)': 0.15}

# UI Layout Columns
left, right = st.columns([1, 2])

# --- LEFT PANEL ---
with left:
    st.subheader("📅 Select Year")
    year = st.selectbox("", years, label_visibility="collapsed")

    st.subheader("📏 Select Bandwidth Method")
    bw_label = st.selectbox("", list(band_methods.keys()), label_visibility="collapsed")
    bw_value = band_methods[bw_label]

    st.markdown("---")
    st.subheader("📍 KDE Summary")
    place_data = df[['NAME_2', 'Total_Cases', 'Avg_Temperature', 'Avg_Humidity', 'Avg_Precipitation'] + list(map(str, years))]
    selected_info = place_data.sort_values(by=str(year), ascending=False).head(5)
    for _, row in selected_info.iterrows():
        st.markdown(f"**{row['NAME_2']}**\n\nTotal Cases: {row['Total_Cases']}\n\nAvg Temperature: {row['Avg_Temperature']}°C\n\nAvg Humidity: {row['Avg_Humidity']}%\n\nAvg Precipitation: {row['Avg_Precipitation']} mm")
        st.markdown(f"_Dengue Cases by Year:_\n\n2018: {row['2018']} | 2019: {row['2019']} | 2020: {row['2020']}\n\n2021: {row['2021']} | 2022: {row['2022']} | 2023: {row['2023']} | 2024: {row['2024']}")
        st.markdown("---")

# --- RIGHT PANEL ---
with right:
    st.subheader(f"🗺️ Dengue KDE Hotspot Map - {year} ({bw_label})")
    points = prepare_points(df, year)
    if points is not None:
        xi, yi, zi = generate_kde(points.values, bandwidth=bw_value)

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
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected year.")

    st.subheader("🧭 Interactive KDE Detail Map")
    try:
        with open("data/kde_hotspots_with_details.html", 'r', encoding='utf-8') as f:
            html(f.read(), height=500)
    except FileNotFoundError:
        st.error("Interactive map HTML not found. Please upload `kde_hotspots_with_details.html` to the data folder.")
