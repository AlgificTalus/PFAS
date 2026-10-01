from io import StringIO

import pandas as pd
import requests

# --- Settings ---
SITES_URL = "https://www.waterqualitydata.us/data/Station/search"
RESULTS_URL = "https://www.waterqualitydata.us/data/Result/search"
PARAMS = {
    "countrycode": "US",
    "statecode": "US:53",
    "characteristicType": "PFAS,Perfluorinated Alkyl Substance",
    "mimeType": "csv",
}
# --- Sites ---
response = requests.get(SITES_URL, params=PARAMS)
print(f"Sites status code: {response.status_code}")
sites = pd.read_csv(StringIO(response.text))
print(sites.shape)
print(sites.columns.tolist())
print(sites["MonitoringLocationTypeName"].value_counts())
print(sites["HorizontalCoordinateReferenceSystemDatumName"].value_counts())
# --- Results ---
response = requests.get(RESULTS_URL, params=PARAMS)
print(f"Results status code: {response.status_code}")
results = pd.read_csv(StringIO(response.text))
print(results.shape)
print(results.columns.tolist())
print(results["CharacteristicName"].value_counts().head(15))
print(results["ResultMeasure/MeasureUnitCode"].value_counts())
print(results["ActivityMediaName"].value_counts())
print(results["ActivityTypeCode"].value_counts())
print(results["ResultDetectionConditionText"].value_counts())

water = results[
    (results["ActivityMediaName"] == "Water")
    & (results["ActivityTypeCode"] == "Sample-Routine")
]
print(water.shape)
print(water["CharacteristicName"].value_counts())
print(water["ResultMeasure/MeasureUnitCode"].value_counts(dropna=False))

pfoa_pfos_names = [
    "Perfluorooctanesulfonate",
    "Perfluorooctane sulfonic acid",
    "Perfluorooctanoic acid",
]
target = water[water["CharacteristicName"].isin(pfoa_pfos_names)]
print("Water sites, any compound:", water["MonitoringLocationIdentifier"].nunique())
print("Water sites with PFOA or PFOS:", target["MonitoringLocationIdentifier"].nunique())