CREATE OR REPLACE EXTERNAL TABLE `due-fx-analytics.raw_fx.ext_parallel_rates` 
WITH PARTITION COLUMNS (date DATE)
OPTIONS(
    format = "NEWLINE_DELIMITED_JSON",
    uris = ["gs://due-fx-data-245535/raw/cbn/*"],
    hive_partition_uri_prefix = "gs://due-fx-data-245535/raw/cbn"
);