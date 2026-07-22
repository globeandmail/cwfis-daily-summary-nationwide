
from datetime import date, datetime
from zoneinfo import ZoneInfo
import csv
import requests
import os

# GET TODAY'S DATE FOR URL
url_date = date.today().strftime("%Y-%m-%d")

# DO TIMESTAMP FOR CHART
dt = datetime.now(ZoneInfo("America/Toronto"))
timestamp = (
    dt.strftime("%B %d, %Y, %I:%M %p")
      .replace("AM", "a.m.")
      .replace("PM", "p.m.")
      .replace(" 0", " ")
)

timestamp += " ET"

# DATA URL
url = (
    "https://api.cwfif.nrcan.gc.ca/reported-fire-stats/ytd/by-response-type"
    "?group_by_stage_of_control=true"
    "&group_by_status=true"
    f"&date={url_date}"
)

def do_string(text):
    return text.replace("_", " ").capitalize()

#FETCH DATA 

response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()[0]
area_data = data["area_burned"]["response_type"]
count_data = data["fire_count"]["response_type"]

# BUILD CSV
rows = []

rows.append([
    "Status",
    "Hectares burned",
    "Number of fires",
    "Timestamp (ET)"
])

# FULL RESPONSE
for status in ["out_of_control", "being_held", "under_control"]:
    rows.append([
        f"{do_string(status)}",
        count_data["full_response"]["stage_of_control"][status],
        area_data["full_response"]["stage_of_control"][status],
        timestamp
    ])

# MODIFIED AND MONITORED RESPONSE
for response in ["modified_response", "monitored_response"]:
    rows.append([
        f"{do_string(response)}",
        count_data[response]["status"]["active"],
        area_data[response]["status"]["active"],
        timestamp
    ])

# monitored_response
# rows.append([
#     "Monitored response",
#     count_data["monitored_response"]["status"]["active"],
#     area_data["monitored_response"]["status"]["active"],
#     timestamp
# ])

with open("data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # writer.writerow([
    #     "Status",
    #     "Hectares burned",
    #     "Number of fires",
    #     "Timestamp (ET)"
    # ])

    writer.writerows(rows)

print("data.csv updated")

API_TOKEN = os.environ["TOKEN"]
URL_BASE = os.environ["URL_BASE"]
CHART_ID = "AUj6h"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# CSV data to upload
csv_data = """date,value
2026-07-20,100
2026-07-21,125
2026-07-22,150
"""

# UPDATE DATA
response = requests.put(
    f"{URL_BASE}charts/{CHART_ID}/data",
    headers=HEADERS,
    data=csv_data.encode("utf-8")
)

response.raise_for_status()

# PATCH CHART
payload = {
    "title": "COOL CHORT BRO"
}

response = requests.patch(
    f"{URL_BASE}charts/{CHART_ID}",
    json=payload,
    headers=HEADERS
)

response.raise_for_status()

# PUBLISH CHART
response = requests.post(
    f"{URL_BASE}charts/{CHART_ID}/publish",
    headers=HEADERS
)

response.raise_for_status()

print("Chart updated and published.")
