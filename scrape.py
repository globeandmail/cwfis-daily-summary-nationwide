
from datetime import date, datetime
from zoneinfo import ZoneInfo
from io import StringIO
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
rows = [[
    "Status",
    "<b>NUMBER OF FIRES</b>",
    "<b>HECTARES BURNED</b>",
    "Timestamp"
]]

# FULL RESPONSE
for status in ["out_of_control", "being_held", "under_control"]:
    rows.append([
        f"{do_string(status)}",
        count_data["full_response"]["stage_of_control"][status],
        area_data["full_response"]["stage_of_control"][status],
        timestamp
    ])

# MODIFIED AND MONITORED RESPONSE
for response_type in ["modified_response", "monitored_response"]:
    rows.append([
        f"{do_string(response_type)}",
        count_data[response_type]["status"]["active"],
        area_data[response_type]["status"]["active"],
        timestamp
    ])

# CSV DATA
csv_buffer = StringIO()
csv.writer(csv_buffer).writerows(rows)
csv_data = csv_buffer.getvalue()

# TOTALS
total_fires = sum(int(row[1]) for row in rows[1:])
total_hectares = sum(float(row[2]) for row in rows[1:])

# FOR CHART UPDATE
API_TOKEN = os.environ["TOKEN"]
URL_BASE = os.environ["URL_BASE"]
CHART_ID = "s6yBc"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# UPDATE DATA
response = requests.put(
    f"{URL_BASE}charts/{CHART_ID}/data",
    headers=HEADERS,
    data=csv_data.encode("utf-8")
)

response.raise_for_status()

# UPDATE TITLE AND TIMESTAMP
payload = {
    "title": f"There are currently {total_fires:,} wildfires in Canada that have burned {total_hectares:,.0f} hectares",
    "metadata": {
        "describe": {
            "intro": f"By stage of control; As of {timestamp}",
        }
    }
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
