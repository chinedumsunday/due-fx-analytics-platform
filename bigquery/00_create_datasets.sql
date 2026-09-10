CREATE SCHEMA IF NOT EXISTS `due-fx-analytics.raw_fx`
OPTIONS(
    location="us-central1",
    default_table_expiration_days=NULL
);

CREATE SCHEMA IF NOT EXISTS `due-fx-analytics.staging_fx`
OPTIONS(
    location="us-central1",
    default_table_expiration_days=NULL
);

CREATE SCHEMA IF NOT EXISTS `due-fx-analytics.marts_fx`
OPTIONS(
    location="us-central1",
    default_table_expiration_days=NULL
);

ALTER SCHEMA `due-fx-analytics.raw_fx` SET OPTIONS(
    default_table_expiration_days=NULL
);

ALTER SCHEMA `due-fx-analytics.staging_fx` SET OPTIONS(
    default_table_expiration_days=NULL
);

ALTER SCHEMA `due-fx-analytics.marts_fx` SET OPTIONS(
    default_table_expiration_days=NULL
);  
