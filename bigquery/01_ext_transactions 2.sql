CREATE OR REPLACE EXTERNAL TABLE `due-fx-analytics.raw_fx.ext_transactions` 
WITH PARTITION COLUMNS (date DATE)
OPTIONS(
    format = "PARQUET",
    uris = ["gs://due-fx-data-245535/raw/transactions/*"],
    hive_partition_uri_prefix = "gs://due-fx-data-245535/raw/transactions"
);