import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

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

# --- Step 4: Load into PostgreSQL ---
df.to_sql(
    "storm_events_details",  # table name
    engine,
    if_exists="replace",     # use "append" if you don’t want overwrite
    index=False
)

print("StormEvents_details.csv successfully loaded into PostgreSQL.")
