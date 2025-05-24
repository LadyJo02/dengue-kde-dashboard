import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from utils.kde_processing import generate_kde


# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/dengue_climate_data.csv')
    gdf = gpd.read_file('data/gadm41_PHL_2.shp')
    return df, gdf

# Filter KDE points
def prepare_points(df, year):
    df_year = df.copy()
    df_year[str(year)] = pd.to_numeric(df_year[str(year)], errors='coerce').fillna(0).astype(int)

    points = []
    for _, row in df_year.iterrows():
        count = row[str(year)]
        if count > 0:
            points.extend([[row["centroid_lon"], row["centroid_lat"]]] * count)
    
    if not points:
        return np.empty((2, 0))
    
    return np.array(points).T

# Streamlit UI
st.title("🦟 Dengue KDE Hotspot Dashboard")
st.markdown("Visualizing dengue hotspots in Northern Mindanao using Kernel Density Estimation")

df, gdf = load_data()
years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
band_methods = {'Scott': 'scott', 'Silverman': 'silverman', 'LOOCV (0.15)': 0.15}

year = st.selectbox("Select Year", years)
bw_label = st.selectbox("Select Bandwidth Method", list(band_methods.keys()))
bw_value = band_methods[bw_label]

points = prepare_points(df, year)
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

# Export option
if st.button("Download PNG"):
    fig.savefig(f"figures/kde_map_{year}_{bw_label.lower().replace(' ', '_')}.png", dpi=300)
    st.success("PNG saved to figures folder.")
