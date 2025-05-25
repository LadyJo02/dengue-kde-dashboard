import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from utils.kde_processing import generate_kde
from streamlit.components.v1 import html

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/dengue_climate_data.csv")
    gdf = gpd.read_file("data/gadm41_PHL_2.shp")
    return df, gdf

# Prepare KDE points for selected year
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

    return points

# Sidebar for user controls
st.set_page_config(layout="wide")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/616/616408.png", width=50)
st.sidebar.title("Dengue KDE Dashboard")
st.sidebar.markdown("Visualize dengue hotspots using Kernel Density Estimation (KDE)")

# Select Year and Bandwidth
years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
band_methods = {'Scott': 'scott', 'Silverman': 'silverman', 'LOOCV (0.15)': 0.15}
year = st.sidebar.selectbox("Select Year", years)
bw_label = st.sidebar.selectbox("Select Bandwidth Method", list(band_methods.keys()))
bw_value = band_methods[bw_label]

# Load data
df, gdf = load_data()
points = prepare_points(df, year)

st.title("\U0001F99F Dengue KDE Hotspot Dashboard")
st.markdown(f"Visualizing dengue hotspots in **Northern Mindanao (2018–2024)** using Kernel Density Estimation (KDE)")

col1, col2 = st.columns([1, 2])

# KDE Summary
with col1:
    st.subheader("\U0001F4CD KDE Summary")
    top_places = df.sort_values(by=str(year), ascending=False).head(5)
    for _, row in top_places.iterrows():
        st.markdown(f"**{row['place']}**")
        st.write(f"Total Cases: {int(row['Total_Cases'])}")
        st.write(f"Avg Temperature: {row['Temperature_C']}\u00b0C")
        st.write(f"Avg Humidity: {row['Humidity_%']}%")
        st.write(f"Avg Precipitation: {row['Precipitation_mm']} mm")
        yearly_data = " | ".join([f"{y}: {int(row[str(y)])}" for y in years])
        st.markdown(f"*Dengue Cases by Year:*\n{yearly_data}")
        st.markdown("---")

# KDE Heatmap
with col2:
    if points:
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
        ax.set_title(f"Dengue KDE Hotspot Map - {year} ({bw_label})")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        st.pyplot(fig)
    else:
        st.warning(f"No KDE points available for year {year}.")

# Interactive Map with Details
st.subheader("\U0001F30D Interactive KDE Detail Map")
html_path = "data/kde_hotspots_with_details.html"
with open(html_path, "r", encoding="utf-8") as f:
    source_code = f.read()
html(source_code, height=700)
