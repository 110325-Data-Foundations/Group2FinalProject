import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# --- Load env + connect ---
load_dotenv()
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

# # --- 1. Total row count ---
# df_count = pd.read_sql(
#     "SELECT COUNT(*) AS total_rows FROM storm_events_details",
#     engine
# )
# print("\n Total Rows:")
# print(df_count)



# # --- 2. Preview key columns (first 5 rows) ---
# df_preview = pd.read_sql(
#     """
#     SELECT 
#         "EVENT_ID",
#         "STATE",
#         "YEAR",
#         "MONTH_NAME",
#         "EVENT_TYPE",
#         "BEGIN_DATE_TIME",
#         "END_DATE_TIME",
#         "INJURIES_DIRECT",
#         "DEATHS_DIRECT"
#     FROM storm_events_details
#     LIMIT 5
#     """,
#     engine
# )
# print("\n First 5 Event Samples:")
# print(df_preview)

# # --- 3. Top 10 states by number of storms ---
# df_states = pd.read_sql(
#     """
#     SELECT "STATE", COUNT(*) AS total_events
#     FROM storm_events_details
#     GROUP BY "STATE"
#     ORDER BY total_events DESC
#     LIMIT 10
#     """,
#     engine
# )
# print("\n Top 10 States by Storm Count:")
# print(df_states)

# # --- 4. Total injuries & deaths ---
# df_casualties = pd.read_sql(
#     """
#     SELECT
#         SUM("INJURIES_DIRECT" + "INJURIES_INDIRECT") AS total_injuries,
#         SUM("DEATHS_DIRECT" + "DEATHS_INDIRECT")     AS total_deaths
#     FROM storm_events_details
#     """,
#     engine
# )
# print("\n Total Injuries & Deaths:")
# print(df_casualties)

# # --- 5. Check geographic coordinates (for Cartopy) ---
# df_coords = pd.read_sql(
#     """
#     SELECT
#         "BEGIN_LAT", "BEGIN_LON",
#         "END_LAT", "END_LON",
#         "EVENT_TYPE", "STATE"
#     FROM storm_events_details
#     WHERE "BEGIN_LAT" IS NOT NULL
#       AND "BEGIN_LON" IS NOT NULL
#     LIMIT 5
#     """,
#     engine
# )
# print("\n Coordinate Sample:")
# print(df_coords)

# # --- 6. Top 10 event types ---
# df_event_types = pd.read_sql(
#     """
#     SELECT "EVENT_TYPE", COUNT(*) AS total_events
#     FROM storm_events_details
#     GROUP BY "EVENT_TYPE"
#     ORDER BY total_events DESC
#     LIMIT 10
#     """,
#     engine
# )
# print("\n Top 10 Event Types:")
# print(df_event_types)

df_full = pd.read_sql("SELECT * FROM storm_events_details", engine)
# print("\nAny NULLs in dataset?:", df_full.isna().any().any())
# print("Total NULL values:", df_full.isna().sum().sum())

null_percent = (df_full.isna().mean() * 100).sort_values(ascending=False)
print("\nNULL Percentage Per Column:")
print(null_percent[null_percent > 0])


# df_full.notna().all(axis=1).sum()
# print("Rows with NO NULL values:", df_full.notna().all(axis=1).sum())
# print("Rows WITH at least one NULL:", df_full.isna().any(axis=1).sum())

print("Rows with these coordinates present:",
      df_full[
          df_full["BEGIN_LAT"].notna() &
          df_full["BEGIN_LON"].notna() &
          df_full["END_LAT"].notna() &
          df_full["END_LON"].notna()
      ].shape[0]
)

