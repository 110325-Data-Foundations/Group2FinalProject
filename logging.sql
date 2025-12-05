CREATE TABLE data_load_log (
    load_id SERIAL PRIMARY KEY,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rows_loaded INT,
    rows_rejected INT
);


SELECT * FROM data_load_log