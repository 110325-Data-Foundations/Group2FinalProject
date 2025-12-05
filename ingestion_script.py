from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Revature_110325/Group2FinalProject/scripts/.env")
engine = create_engine(os.getenv("DATABASE_URL"))

rows_loaded = 28467
rows_rejected = 16254

with engine.begin() as conn:
    conn.execute(
        text("""
            INSERT INTO data_load_log (rows_loaded, rows_rejected)
            VALUES (:rows_loaded, :rows_rejected)
        """),
        {"rows_loaded": rows_loaded, "rows_rejected": rows_rejected}
    )

print("Ingestion log entry saved successfully!")

