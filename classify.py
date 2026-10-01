# 1. Import sqlite3, pandas (as pd), and Path
from pathlib import Path
import sqlite3
import pandas as pd

# 2. Point to the database: BASE_DIR from this script's folder, then DB_PATH to wa_pfas.db
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "wa_pfas.db"
# 3. Connect to the database
conn = sqlite3.connect(DB_PATH)
# 4. Write a query that keeps only the results we want. It needs there conditions in the where and joined with AND: ActivityMediaName is 'water', ActivityTypeCode is 'Sample-Routine', and CharacteristicName is NOT one of the two non-PFAS checmicals
query = """
WITH labeled AS (
SELECT MonitoringLocationIdentifier, CharacteristicName,ResultMeasureValue,ResultDetectionConditionText,
       CASE
         WHEN ResultDetectionConditionText = 'Not Detected' THEN 0
         WHEN ResultDetectionConditionText = 'Present Below Quantification Limit' THEN 1
          WHEN ResultMeasureValue IS NOT NULL THEN 1
         ELSE NULL
       END AS detected
FROM results
WHERE ActivityMediaName = 'Water'
  AND ActivityTypeCode = 'Sample-Routine'
  AND CharacteristicName NOT IN ('CFC-114', 'Propane, 1,1,2,2-tetrafluoro-')
),
site_summary AS (
SELECT
MonitoringLocationIdentifier,
MAX(detected) AS any_detect,
Count(*) AS total_results,
sum(detected) AS detected_results
FROM labeled
GROUP BY MonitoringLocationIdentifier
)
SELECT 
    ss.MonitoringLocationIdentifier,
    s.MonitoringLocationName,
    s.MonitoringLocationTypeName,
    s.LatitudeMeasure,
    s.LongitudeMeasure,
    s.HorizontalCoordinateReferenceSystemDatumName,
    ss.total_results,
    ss.detected_results,
    CASE WHEN ss.any_detect = 1 THEN 'PFAS detected' ELSE 'Not detected' END AS status
FROM site_summary AS ss
LEFT JOIN sites AS s
    ON ss.MonitoringLocationIdentifier = s.MonitoringLocationIdentifier
"""
# 5. Execute the query and store the results in a DataFrame
df = pd.read_sql(query, conn)
# 6. Print the first 5 rows of the DataFrame
print(df.head())
print(f"Number of rows: {df.shape[0]}")
print(df["status"].value_counts())
print(df[["MonitoringLocationName", "LatitudeMeasure", "LongitudeMeasure", "status"]])
df.to_sql("site_status", conn, if_exists="replace", index=False)
print("Saved site_status table")
# 7. Close the connection
conn.close()