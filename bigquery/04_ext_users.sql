CREATE OR REPLACE EXTERNAL TABLE `due-fx-analytics.raw_fx.ext_users` 
WITH PARTITION COLUMNS (date DATE)
OPTIONS(
    format = "PARQUET",
    uris = ["gs://due-fx-data-245535/raw/users/*.parquet"],
    hive_partition_uri_prefix = "gs://due-fx-data-245535/raw/users"
);