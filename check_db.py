# 1. Import sqlite3, pandas (as pd), and Path
from pathlib import Path
import sqlite3
import pandas as pd
import requests

# 2. Point to the database: BASE_DIR from this script's folder, then DB_PATH to wa_pfas.db
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "wa_pfas.db"
# 3. Connect to the database
conn = sqlite3.connect(DB_PATH)

# 4. Count the rows in the sites table, and print the result
sites_count = pd.read_sql("SELECT COUNT(*) FROM sites", conn).iloc[0, 0]
print(f"Number of sites: {sites_count}")

# 5. Count the rows in the results table, and print the result
results_count = pd.read_sql("SELECT COUNT(*) FROM results", conn).iloc[0, 0]
print(f"Number of results: {results_count}")


# 6. Close the connection
conn.close()    