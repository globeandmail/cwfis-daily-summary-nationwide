import requests
import os

API_TOKEN = os.environ["TOKEN"]
URL_BASE = os.environ["URL_BASE"]
CHART_ID = "AUj6h"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# CSV data to upload
csv_data = """date,value
2026-07-20,100
2026-07-21,125
2026-07-22,150
"""

# UPDATE DATA
response = requests.put(
    f"${URL_BASE}/charts/{CHART_ID}/data",
    headers=headers,
    data=csv_data.encode("utf-8")
)

response.raise_for_status()

# PATCH CHART
payload = {
    "title": "COOL CHORT BRO"
}

response = requests.patch(
    f"${URL_BASE}/charts/{CHART_ID}",
    json=payload,
    headers=headers
)

response.raise_for_status()

# PUBLISH CHART
response = requests.post(
    f"${URL_BASE}/charts/{CHART_ID}/publish",
    headers=headers
)

response.raise_for_status()

print("Chart updated and published.")
