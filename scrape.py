from datetime import date, datetime, timezone
import csv
import requests

today = date.today().strftime("%Y-%m-%d")

generated_utc = datetime.now(timezone.utc).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)

url = (
    "https://api.cwfif.nrcan.gc.ca/reported-fire-stats/ytd/by-response-type"
    "?group_by_stage_of_control=true"
    "&group_by_status=true"
    f"&date={today}"
)

def do_string(text):
    return text.replace("_", " ").capitalize()
    
response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()[0]

area_data = data["area_burned"]["response_type"]
count_data = data["fire_count"]["response_type"]

rows = []
# full_response statuses
for status in ["out_of_control", "being_held", "under_control"]:
    rows.append([
        f"{do_string(status)}",
        area_data["full_response"]["stage_of_control"][status],
        count_data["full_response"]["stage_of_control"][status],
        generated_utc
    ])

# modified_response
rows.append([
    "Modified response",
    area_data["modified_response"]["status"]["active"],
    count_data["modified_response"]["status"]["active"],
    generated_utc
])

# monitored_response
rows.append([
    "Monitored response",
    area_data["monitored_response"]["status"]["active"],
    count_data["monitored_response"]["status"]["active"],
    generated_utc
])

with open("data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "Status",
        "Hectares burned",
        "Number of fires",
        "Timestamp (UTC)"
    ])

    writer.writerows(rows)

print("data.csv updated")
