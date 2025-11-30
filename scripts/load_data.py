import os
import pandas as pd
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# --- Step 1: Load environment variables ---
load_dotenv()
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL not found in .env file")

# --- Step 2: Create database engine ---
engine = create_engine(database_url)

# --- Step 3: Read CSV file ---
csv_path = "data/StormEvents_details.csv"
df = pd.read_csv(csv_path)

# --- (Optional) Save raw table to PostgreSQL ---
df.to_sql(
    "storm_events_details",
    engine,
    if_exists="replace",
    index=False,
)

# --- Config: columns to drop / check / fill ---

cols_to_drop = [
    "TOR_OTHER_WFO",
    "TOR_OTHER_CZ_FIPS",
    "TOR_OTHER_CZ_STATE",
    "TOR_OTHER_CZ_NAME",
    "TOR_WIDTH",
    "TOR_LENGTH",
    "TOR_F_SCALE",
    "EVENT_NARRATIVE",
    "EPISODE_NARRATIVE",
    "CATEGORY",
    "DATA_SOURCE",
]

coord_cols_missing_overlap = [
    "BEGIN_AZIMUTH",
    "BEGIN_LOCATION",
    "BEGIN_RANGE",
    "END_RANGE",
    "END_AZIMUTH",
    "BEGIN_LON",
    "BEGIN_LAT",
    "END_LOCATION",
    "END_LON",
    "END_LAT",
]

text_fill_cols = [
    "FLOOD_CAUSE",
    "MAGNITUDE_TYPE",
]

numeric_fill_cols = [
    "MAGNITUDE",
    "DAMAGE_CROPS",
    "DAMAGE_PROPERTY",
]

# --- Step 4: Drop unwanted columns ---
df_clean = df.drop(columns=cols_to_drop)

# --- Step 5: Identify rows with ALL coord columns NULL ---
invalid_mask = df_clean[coord_cols_missing_overlap].isna().all(axis=1)
same_missing_count = invalid_mask.sum()
print("Rows where ALL these columns are NULL:", same_missing_count)

# Capture invalid rows BEFORE filtering them out
df_invalid = df_clean[invalid_mask].copy()

# Keep only valid rows
df_clean = df_clean[~invalid_mask].copy()

# --- Step 6: Fill missing values ---
df_clean[text_fill_cols] = df_clean[text_fill_cols].fillna("N/A")
df_clean[numeric_fill_cols] = df_clean[numeric_fill_cols].fillna(0)

# --- Step 7: Write cleaned + invalid tables to PostgreSQL ---
df_clean.to_sql(
    "storm_events_details_cleaned",
    engine,
    if_exists="replace",
    index=False,
)

df_invalid.to_sql(
    "storm_events_details_invalid",
    engine,
    if_exists="replace",
    index=False,
)

# --- Step 8: Final NULL check ---
print("\nRemaining NULLs Per Column (cleaned):")
remaining_nulls = df_clean.isna().sum()
print(remaining_nulls[remaining_nulls > 0])

print("\nTotal Remaining NULL Values (cleaned):", df_clean.isna().sum().sum())
print(
    "\nRows Still Containing At Least One NULL (cleaned):",
    df_clean.isna().any(axis=1).sum(),
)

df_clean.info()

print("storm_events_details_cleaned and storm_events_details_invalid successfully loaded into PostgreSQL.")

inspector = inspect(engine)

print("storm_events_details_invalid exists:",
      inspector.has_table("storm_events_details_invalid"))