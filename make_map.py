from pathlib import Path
import sqlite3

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib_scalebar.scalebar import ScaleBar

# --- Settings ---
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "wa_pfas.db"
MAP_PATH = BASE_DIR / "wa_pfas_map.png"
STATES_URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_20m.zip"

# Washington State Plane South (NAD83 HARN, US survey feet).
# Centered on Washington, so north points straight up across the state.
MAP_CRS = "EPSG:2927"

# Point color for each site status
STYLES = {
    "PFAS detected": "#c0392b",
    "Not detected": "#95a5a6",
}

SOURCE_NOTE = (
    "Data: Water Quality Portal (USGS, EPA), PFAS characteristic group, routine water samples. "
    "CFC-114 and tetrafluoropropane excluded as non-PFAS.\n"
    "A site is marked detected if any PFAS compound was detected, including below the quantification limit. "
    "Six marine sites lack a recorded datum; all coordinates treated as WGS84.\n"
    "Boundary: U.S. Census Bureau, 2023. Projection: NAD83(HARN) / Washington State Plane South."
)

# --- Load the classified sites ---
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM site_status", conn)
conn.close()

# --- Turn latitude and longitude into map points, then project ---
sites = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["LongitudeMeasure"], df["LatitudeMeasure"]),
    crs="EPSG:4326",
).to_crs(MAP_CRS)

# --- Load the Washington outline and project it ---
states = gpd.read_file(STATES_URL)
wa = states[states["NAME"] == "Washington"].to_crs(MAP_CRS)

# --- Draw the map ---
fig, ax = plt.subplots(figsize=(11, 8.5))
wa.plot(ax=ax, color="whitesmoke", edgecolor="black", linewidth=0.8)

# Plot each status separately so each gets its own color and legend entry
for status, color in STYLES.items():
    subset = sites[sites["status"] == status]
    subset.plot(
        ax=ax,
        color=color,
        markersize=70,
        edgecolor="black",
        linewidth=0.6,
        label=f"{status} ({len(subset)} sites)",
    )

# --- Layout: frame, title, legend ---
ax.margins(0.08)          # white space around the state for the map elements
ax.set_xticks([])         # hide coordinate numbers; a report map doesn't need them
ax.set_yticks([])
ax.set_title("PFAS Detections at Water Sampling Sites in Washington", fontsize=16, pad=12)
ax.legend(title="Site status", loc="lower left", frameon=True)

# --- Scale bar ---
# The map's units are US survey feet; one foot is 0.3048006 meters.
ax.add_artist(ScaleBar(0.3048006, units="m", location="lower right", length_fraction=0.2))

# --- North arrow ---
ax.annotate(
    "N",
    xy=(0.94, 0.93),
    xytext=(0.94, 0.80),
    xycoords="axes fraction",
    textcoords="axes fraction",
    ha="center",
    va="center",
    fontsize=14,
    fontweight="bold",
    arrowprops=dict(facecolor="black", width=5, headwidth=14),
)

# --- Source note below the map ---
fig.subplots_adjust(bottom=0.14)
fig.text(0.5, 0.03, SOURCE_NOTE, ha="center", fontsize=8)

# --- Save ---
fig.savefig(MAP_PATH, dpi=300, bbox_inches="tight")
print(f"Saved {MAP_PATH.name}")