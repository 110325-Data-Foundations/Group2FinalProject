import csv
import json

# --- Input / Output files ---
csv_file = "StormEvents_details-ftp_v1.0_d2025_c20251118.csv"
json_file = "StormEvents_details-ftp_v1.0_d2025_c20251118.json"

data = []

# --- Read CSV ---
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)   # uses first row as keys
    for row in reader:
        data.append(row)

# --- Write JSON ---
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("Converted:", csv_file, "→", json_file)
