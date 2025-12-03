import os
import pandas as pd
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
from tqdm import tqdm
import math

# ---------- ENV + ENGINE ----------

def get_engine(env_var_name: str = "DATABASE_URL"):
    """Load DATABASE_URL from .env and return a SQLAlchemy engine."""
    load_dotenv()
    database_url = os.getenv(env_var_name)

    if not database_url:
        raise ValueError(f"{env_var_name} not found in .env file")

    engine = create_engine(database_url)
    return engine


# ---------- FILE DISCOVERY & LOADING ----------

def list_data_files(data_dir: str = "data"):
    """Return list of CSV/JSON files in the data directory."""
    files = [
        f for f in os.listdir(data_dir)
        if f.lower().endswith((".csv", ".json"))
    ]
    return files


def load_selected_file(files, index: int, data_dir: str = "data") -> pd.DataFrame:
    """
    Given a list of filenames and a chosen index, load the corresponding CSV/JSON
    into a DataFrame.
    """
    if not files:
        raise FileNotFoundError("No CSV or JSON files found in data folder.")

    if index < 0 or index >= len(files):
        raise IndexError("Selected file index out of range.")

    selected_file = files[index]
    file_path = os.path.join(data_dir, selected_file)

    if selected_file.lower().endswith(".csv"):
        df = pd.read_csv(file_path)
    elif selected_file.lower().endswith(".json"):
        df = pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format.")

    return df, selected_file


# ---------- Convert numerical values to proper form  ----------

def normalize_damage_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert DAMAGE_PROPERTY / DAMAGE_CROPS like '2.50K' / '0.00K' / '1.25M'
    to numeric values (float). Unknown / bad values -> 0.
    """
    for col in ["DAMAGE_PROPERTY", "DAMAGE_CROPS"]:
        if col in df.columns:
            s = df[col].astype(str).str.strip()

            # Treat these as missing
            s = s.replace(
                {"": None, "None": None, "nan": None, "NaN": None}
            )

            # Separate numeric part and suffix (K/M)
            factor = s.str.extract(r'([KkMmBb])$', expand=False)
            base = s.str.replace(r'[KkMmBb]', '', regex=True)

            num = pd.to_numeric(base, errors="coerce")

            # Apply multiplier: K -> 1_000, M -> 1_000_000, default -> 1
            multiplier = factor.map(
                {"K": 1_000, "k": 1_000, "M": 1_000_000, "m": 1_000_000, "b" : 1_000_000_000, "B" : 1_000_000_000}
            ).fillna(1)

            num = num * multiplier

            # Save back, fill NaN with 0 (you can choose to keep NaN if you prefer)
            df[col] = num.fillna(0)

    return df


# ---------- RAW INSERT ----------

def insert_raw_staging(df_raw: pd.DataFrame, engine, chunksize: int = 5000):
    """
    Insert raw DataFrame into storm_events_details (staging) table
    with a visible progress bar.
    """
    total_rows = len(df_raw)
    total_chunks = math.ceil(total_rows / chunksize)

    print(f"\nInserting {total_rows:,} rows into storm_events_details...")
    print(f"Chunks: {total_chunks} (chunksize={chunksize})\n")

    for i in tqdm(range(0, total_rows, chunksize), desc="Staging Insert"):
        chunk = df_raw.iloc[i:i + chunksize]

        chunk.to_sql(
            "storm_events_details",
            engine,
            if_exists="append",
            index=False,
            method="multi",
        )
# ---------- CLEAN / INVALID SPLIT + FILL ----------

COLS_TO_DROP = [
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

COORD_COLS_MISSING_OVERLAP = [
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

TEXT_FILL_COLS = [
    "FLOOD_CAUSE",
    "MAGNITUDE_TYPE",
]

NUMERIC_FILL_COLS = [
    "MAGNITUDE",
    "DAMAGE_CROPS",
    "DAMAGE_PROPERTY",
]


def split_clean_invalid(df_raw: pd.DataFrame):
    """
    From the raw DataFrame:
      - Identify invalid rows where ALL coord columns are NULL
      - Return (df_clean_base, df_invalid, invalid_count)
    df_clean_base still contains all columns; dropping happens later.
    """
    valid_coord_cols = [
        c for c in COORD_COLS_MISSING_OVERLAP
        if c in df_raw.columns
    ]

    if not valid_coord_cols:
        # No coord columns found; treat all as valid
        invalid_mask = pd.Series(False, index=df_raw.index)
    else:
        invalid_mask = df_raw[valid_coord_cols].isna().all(axis=1)

    invalid_count = int(invalid_mask.sum())

    df_invalid = df_raw[invalid_mask].copy()
    df_clean_base = df_raw[~invalid_mask].copy()

    return df_clean_base, df_invalid, invalid_count


def build_clean_df(df_clean_base: pd.DataFrame):
    """
    Drop unwanted columns from df_clean_base and return df_clean.
    """
    existing_cols_to_drop = [c for c in COLS_TO_DROP if c in df_clean_base.columns]
    df_clean = df_clean_base.drop(columns=existing_cols_to_drop)
    return df_clean


def fill_missing_values(df_clean: pd.DataFrame):
    """
    Fill text and numeric missing values in-place and return df_clean.
    """
    for col in TEXT_FILL_COLS:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna("N/A")

    for col in NUMERIC_FILL_COLS:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(0)

    return df_clean


# ---------- DB INSERTS FOR CLEAN/INVALID ----------

def insert_clean_and_invalid(df_clean: pd.DataFrame, df_invalid: pd.DataFrame, engine, chunksize: int = 5000):
    if not df_clean.empty:
        total_rows = len(df_clean)
        print(f"\nInserting {total_rows:,} cleaned rows...")
        for i in tqdm(range(0, total_rows, chunksize), desc="Cleaned Insert"):
            chunk = df_clean.iloc[i:i + chunksize]
            chunk.to_sql(
                "storm_events_details_cleaned",
                engine,
                if_exists="append",
                index=False,
                method="multi",
            )

    if not df_invalid.empty:
        total_rows = len(df_invalid)
        print(f"\nInserting {total_rows:,} invalid rows...")
        for i in tqdm(range(0, total_rows, chunksize), desc="Invalid Insert"):
            chunk = df_invalid.iloc[i:i + chunksize]
            chunk.to_sql(
                "storm_events_details_invalid",
                engine,
                if_exists="append",
                index=False,
                method="multi",
            )


# ---------- ANALYSIS / DIAGNOSTICS ----------

def analyze_nulls(df_clean: pd.DataFrame):
    """
    Return summary stats about NULLs in df_clean:
      - per-column counts (Series)
      - total null count
      - rows with at least one NULL
    """
    remaining_nulls = df_clean.isna().sum()
    remaining_nonzero = remaining_nulls[remaining_nulls > 0]
    total_nulls = int(df_clean.isna().sum().sum())
    rows_with_null = int(df_clean.isna().any(axis=1).sum())
    return remaining_nonzero, total_nulls, rows_with_null


def table_exists(engine, table_name: str) -> bool:
    """Helper that checks whether a table exists in the DB."""
    inspector = inspect(engine)
    return inspector.has_table(table_name)


# ---------- MAIN SCRIPT ENTRYPOINT ----------

def main():
    # Engine
    engine = get_engine()

    # Files
    DATA_DIR = "data"
    files = list_data_files(DATA_DIR)

    if not files:
        raise FileNotFoundError("No CSV or JSON files found in data folder.")

    print("\nAvailable Data Files:\n")
    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    choice = int(input("\nSelect a file number to load: ")) - 1

    df, selected_file = load_selected_file(files, choice, DATA_DIR)

    print(f"\nLoaded file: {selected_file}")
    print(df.head())

    # ✅ NEW: clean damage columns BEFORE anything hits the DB
    df = normalize_damage_cols(df)

    # Keep raw copy
    df_raw = df.copy()

    # Insert raw into staging
    insert_raw_staging(df_raw, engine)
    print("Inserted raw rows into storm_events_details.")

    # Split into clean_base / invalid
    df_clean_base, df_invalid, invalid_count = split_clean_invalid(df_raw)
    print("Rows where ALL coord columns are NULL:", invalid_count)

    # Build cleaned df (drop cols) + fill missing
    df_clean = build_clean_df(df_clean_base)
    df_clean = fill_missing_values(df_clean)

    # Insert cleaned + invalid
    insert_clean_and_invalid(df_clean, df_invalid, engine)
    print("Inserted cleaned rows into storm_events_details_cleaned.")
    print("Inserted invalid rows into storm_events_details_invalid.")

    # Diagnostics
    remaining_nonzero, total_nulls, rows_with_null = analyze_nulls(df_clean)

    print("\nRemaining NULLs Per Column (cleaned DataFrame):")
    print(remaining_nonzero)
    print("\nTotal Remaining NULL Values (cleaned):", total_nulls)
    print("\nRows Still Containing At Least One NULL (cleaned):", rows_with_null)

    df_clean.info()

    print(
        "\nstorm_events_details_invalid exists:",
        table_exists(engine, "storm_events_details_invalid"),
    )

    print("Done. DB triggers will have logged inserts + duplicates to storm_events_audit.")

if __name__ == "__main__":
    main()
