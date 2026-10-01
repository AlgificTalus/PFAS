from io import StringIO
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl
import sqlite3

import pandas as pd
import requests

# --- Settings ---
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "wa_pfas.db"
SITES_URL = "https://www.waterqualitydata.us/data/Station/search"
RESULTS_URL = "https://www.waterqualitydata.us/data/Result/search"

# Paste the Query URL from the Water Quality Portal's search form here.
# Python pulls the filters out of it and decodes them.
FORM_URL = "https://waterqualitydata.us/#countrycode=US&statecode=US%3A53&characteristicType=PFAS%2CPerfluorinated%20Alkyl%20Substance&mimeType=csv&providers=NWIS&providers=STORET"
PARAMS = parse_qsl(urlsplit(FORM_URL).fragment)
print(PARAMS)


# --- Download helper ---
# Sites and results are downloaded the same way, so one function handles both.
def download(url):
    # 1. Send the request to url, with PARAMS (save it as response)
    response = requests.get(url, params=PARAMS)
    response.raise_for_status()    # 2. stop with an error if the download failed
    # 3. Read the CSV text into a table, and return it
    return pd.read_csv(StringIO(response.text), low_memory=False)


# --- Fetch ---
sites = download(SITES_URL)
results = download(RESULTS_URL)
print(f"{len(sites)} sites, {len(results)} results downloaded")

# --- Save to SQLite ---
# Two related tables, linked by MonitoringLocationIdentifier.
# "replace" overwrites each run, since every download contains the full history.
conn = sqlite3.connect(DB_PATH)
sites.to_sql("sites", conn, if_exists="replace", index=False)
results.to_sql("results", conn, if_exists="replace", index=False)
conn.close()
print(f"Saved to {DB_PATH.name}")