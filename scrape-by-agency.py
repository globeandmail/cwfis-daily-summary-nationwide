
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
    "https://api.cwfif.nrcan.gc.ca/reported-fire-stats/ytd/by-agency"
    "?group_by_stage_of_control=true"
    "&group_by_status=true"
    f"&date={url_date}"
)

def do_string(text):
    return text.replace("_", " ").capitalize()

agencies = { "AB":"Alta.", "BC":"B.C.", "MB":"Man.", "NB":"N.B.", "NL":"N.L.", "NS":"N.S.", "NT":"Nunavut.", "ON":"Ont.", "PC":"Parks Canada", "PE":"PEI", "QC":"Que.", "SK":"Sask.", "YT":"Yukon.", "total":"Total" }

#FETCH DATA

response = requests.get(url, timeout=30)
response.raise_for_status()
data = response.json()[0]

# BUILD CSV

rows = [[
    "Agency",
    "<b>NUMBER OF FIRES</b>",
    "<b>HECTARES BURNED</b>",
    "Timestamp"
]]

for i, d in enumerate(data):
    agency = agencies[d["agency_code"]]
    if agency == "Total":
        continue
    count_data = d["fire_count"]["status"]["active"]
    area_data = d["area_burned"]["status"]["active"]
    rows.append([
        f"{agency}",
        count_data,
        area_data,
        timestamp
    ])
# TOTALS
total_fires = sum(int(row[1]) for row in rows[1:])
total_hectares = sum(float(row[2]) for row in rows[1:])
rows.append(["Total", total_fires, total_hectares])

# CSV DATA
csv_buffer = StringIO()
csv.writer(csv_buffer).writerows(rows)
csv_data = csv_buffer.getvalue()

# FOR CHART UPDATE
API_TOKEN = os.environ["TOKEN"]
URL_BASE = os.environ["URL_BASE"]
CHART_ID = "i42wT"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# UPDATE DATA
response = requests.put(
    f"{URL_BASE}charts/{CHART_ID}/data",
    headers=HEADERS,
    data=csv_data.encode("utf-8")
)

response.raise_for_status()

# UPDATE TIMESTAMP
payload = {
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
